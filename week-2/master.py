import spliter
import mapper
import partitioner
import sorter
import reducer


def main():
    print("===== Flipkart MapReduce Engine =====")

    # Step 1: Split Input
    spliter.split_input()

    # Step 2: Mapper
    mapper.run_mapper()

    # Step 3: Partitioner
    partitioner.partition_data()

    # Step 4: Sorter
    sorter.sort_partitions()

    # Step 5: Reducer
    reducer.run_reducer()

    print("===== MapReduce Completed Successfully =====")


if __name__ == "__main__":
    main()