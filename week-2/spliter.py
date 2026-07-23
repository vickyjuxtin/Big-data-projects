import os

def split_input(input_file="input.txt", output_dir="chunks", num_chunks=2):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "r") as f:
        lines = f.readlines()

    chunk_size = (len(lines) + num_chunks - 1) // num_chunks

    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size

        with open(f"{output_dir}/chunk_{i}.txt", "w") as out:
            out.writelines(lines[start:end])

    print("Input file split successfully.")