from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types

def main():

    print("flink-client starting...")

    # 1. Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # 2. Create a data stream (e.g., from a collection or source)


    # 3. Apply transformations (map, filter, etc.) using Python functions

    # 4. Print or sink the results

    # 5. Execute the job graph


if __name__ == '__main__':
    main()