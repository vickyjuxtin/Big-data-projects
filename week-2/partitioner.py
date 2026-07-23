import os

def partition_data(input_dir="mapped", output_dir="partitions", num_partitions=2):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    partition_files = []
    for i in range(num_partitions):
        partition_files.append(
            open(os.path.join(output_dir, f"partition_{i}.txt"), "w")
        )

    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            with open(os.path.join(input_dir, file), "r") as fin:
                for line in fin:
                    parts = line.strip().split()

                    if len(parts) == 2:
                        key = parts[0]
                        value = parts[1]

                        partition = hash(key) % num_partitions
                        partition_files[partition].write(f"{key}\t{value}\n")

    for f in partition_files:
        f.close()

    print("Partitioning completed successfully.")