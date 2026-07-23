import os

def run_mapper(input_dir="chunks", output_dir="mapped"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            with open(os.path.join(input_dir, file), "r") as fin:
                with open(os.path.join(output_dir, "map_" + file), "w") as fout:
                    for line in fin:
                        key = line.strip()
                        if key:
                            fout.write(f"{key}\t1\n")

    print("Mapping completed successfully.")