from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import RMQSource, \
    FileSink, \
    OutputFileConfig, \
    RollingPolicy
from pyflink.common import Encoder
import os
from pyflink.datastream.connectors.rabbitmq import RMQConnectionConfig
from pyflink.common.serialization import SimpleStringSchema

RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 4000))
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

base_path = os.getenv("OUTPUT_PATH", "/output")


def main():

    print("flink-client starting...")

    # 1. Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.enable_checkpointing(10_000)

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

    # 4. Print or sink the results
    ds.print()
    ds.sink_to(
        sink=FileSink.for_row_format(
            base_path=base_path,
            encoder=Encoder.simple_string_encoder())
        .with_output_file_config(
            OutputFileConfig.builder()
            .with_part_suffix(".txt")
            .build())
        .with_rolling_policy(RollingPolicy.default_rolling_policy(
            part_size=1024 * 1024,

            # milliseconds
            rollover_interval=15 * 1000,
            inactivity_interval=5 * 1000,
        ))
        .build()
    )

    # 5. Execute the job graph
    print("submitting job...", flush=True)
    result = env.execute("rabbitmq-to-file")
    print("execute() returned:", result, flush=True)


if __name__ == '__main__':
    main()
