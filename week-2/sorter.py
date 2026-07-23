import os

def sort_partitions(input_dir="partitions", output_dir="sorted"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            with open(os.path.join(input_dir, file), "r") as fin:
                lines = fin.readlines()

            lines.sort()

            with open(os.path.join(output_dir, "sorted_" + file), "w") as fout:
                fout.writelines(lines)

    print("Sorting completed successfully.")