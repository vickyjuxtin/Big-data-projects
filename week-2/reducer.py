import os

def run_reducer(input_dir="sorted", output_file="output.txt"):
    result = {}

    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            with open(os.path.join(input_dir, file), "r") as fin:
                for line in fin:
                    parts = line.strip().split()

                    if len(parts) == 2:
                        key = parts[0]
                        value = int(parts[1])

                        result[key] = result.get(key, 0) + value

    with open(output_file, "w") as fout:
        for key in sorted(result.keys()):
            fout.write(f"{key}\t{result[key]}\n")

    print("Reducing completed successfully.")