from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import RMQSource
from pyflink.common import Types
import os
from pyflink.datastream.connectors.rabbitmq import RMQConnectionConfig
from pyflink.datastream.functions import MapFunction, RuntimeContext
from pyflink.common.serialization import SimpleStringSchema
import json
from datetime import datetime, timezone
from pyflink.common import RestartStrategies


RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 4000))
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", 9200))
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "toxicity-results")

# base_path = os.getenv("OUTPUT_PATH", "/output")
MODEL_DIR = os.getenv("MODEL_DIR", "/models/gametox-distilbert")


class ToxicityClassifier(MapFunction):
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.tokenizer = None
        self.model = None

    def open(self, runtime_context: RuntimeContext):
        from transformers import AutoModelForSequenceClassification, \
                AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_dir
        )
        self.model.eval()
        self.id2label = {
            int(k): v for k, v in self.model.config.id2label.items()
        }

    def map(self, value):
        import torch

        text = str(json.loads(value))
        if not text:
            return json.dumps(
                {"text": text, "label": None, "error": "empty message"}
            )
        try:
            enc = self.tokenizer(
                text, truncation=True, max_length=128, return_tensors="pt"
            )
            with torch.inference_mode():
                logits = self.model(**enc).logits[0]
            probs = torch.softmax(logits, dim=-1).tolist()
            best = max(range(len(probs)), key=probs.__getitem__)
            return json.dumps(
                {
                    "text": text,
                    "label": self.id2label[best],
                    "label_id": best,
                    "confidence": round(probs[best], 4),
                    # "scores": {
                        # self.id2label[i]:
                            # round(p, 4) for i, p in enumerate(probs)
                    # },
                },
                ensure_ascii=False,
            )
        except Exception as exc:
            return json.dumps(
                {
                    "text": text,
                    "label": None,
                    "error": str(exc)
                }, ensure_ascii=False
            )


# new map which adds elements to ElasticSearch DB
class ElasticsearchWriter(MapFunction):
    MAPPING = {
        "properties": {
            "text": {"type": "text"},
            "label": {"type": "keyword"},
            "label_id": {"type": "integer"},
            "confidence": {"type": "float"},
            "error": {"type": "keyword"},
            "@timestamp": {"type": "date"},
        }
    }

    def __init__(self, host, port, index):
        self.host = host
        self.port = port
        self.index = index
        self.client = None

    # init ElasticSearch instance
    def open(self, runtime_context: RuntimeContext):
        from elasticsearch import Elasticsearch

        self.client = Elasticsearch(
            f"http://{self.host}:{self.port}",
            request_timeout=10,
            max_retries=3,
            retry_on_timeout=True,
        )

        # setup index
        if not self.client.indices.exists(index=self.index):
            try:
                self.client.indices.create(
                    index=self.index, mappings=self.MAPPING
                )
            except Exception as exc:
                if "resource_already_exists_exception" not in str(exc):
                    raise

    def map(self, value):
        try:
            doc = json.loads(value)
            doc["@timestamp"] = datetime.now(timezone.utc).isoformat()

            # add the value to this DB
            self.client.index(index=self.index, document=doc)
        except Exception as exc:
            print(f"ElasticSearch write failed: {exc}", flush=True)
        return value

    def close(self):
        if self.client is not None:
            self.client.close()


def main():

    print("flink-client starting...")

    # 1. Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.enable_checkpointing(10_000)
    env.set_restart_strategy(RestartStrategies.no_restart())

    env.add_jars(
        "file:///opt/connectors/flink-connector-rabbitmq.jar",
        "file:///opt/connectors/amqp-client.jar",
    )
    connection_config = (
        RMQConnectionConfig.Builder()
        .set_virtual_host("/")
        .set_host(RABBITMQ_HOST)
        .set_port(RABBITMQ_PORT)
        .set_user_name("guest")
        .set_password("guest")
        .build()
    )

    rabbitmq_source = RMQSource(
        connection_config,
        "mod-jobs",
        False,
        SimpleStringSchema(),
    )

    ds = env.add_source(rabbitmq_source)

    # 3. Apply transformations (map, filter, etc.) using Python functions
    ds = ds.map(ToxicityClassifier(MODEL_DIR), output_type=Types.STRING())

    # 4. Print results through ElasticSearch
    ds = ds.map(
        ElasticsearchWriter(
            ELASTICSEARCH_HOST, ELASTICSEARCH_PORT, ELASTICSEARCH_INDEX
        ),
        output_type=Types.STRING(),
    )

    ds.print()

    # 5. Execute the job graph
    print("submitting job...", flush=True)
    result = env.execute("rabbitmq-to-file")
    print("execute() returned:", result, flush=True)


if __name__ == '__main__':
    main()
