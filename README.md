# Flipkart Log Harvester System

A small demo pipeline that simulates high-velocity log streams from three
Flipkart services, harvests them over TCP, encodes them into a compact
binary format on disk, and lets you decode them back into readable records.

## Components

| File | Role |
|---|---|
| `server.py` | Simulates 3 Flipkart branch servers (`orders`, `payments`, `delivery`) that stream fake log lines over TCP. |
| `harvester.py` | Connects to each simulated server, parses incoming log lines, and writes them as length-prefixed binary records into per-module/per-level partition files. |
| `read_binary.py` | Reads a single binary partition file back and decodes it into human-readable records. |

## Requirements

- Python 3.8+
- No third-party dependencies — only the standard library (`socket`,
  `threading`, `struct`, `re`, `collections`).

## How to run it

Run these in **separate terminals**, in this order:

**1. Start the simulated servers**

```bash
python server.py
```

This opens 3 TCP listeners on `127.0.0.1`:

| Branch | Port |
|---|---|
| flipkart-orders | 9001 |
| flipkart-payments | 9002 |
| flipkart-delivery | 9003 |

Each accepted connection gets a steady stream of randomly generated log
lines like:

```
2026-07-10 14:22:31 | INFO | flipkart-orders | Order#4821 placed successfully
```

About 5% of lines are intentionally malformed (`INVALID_FLIPKART_LOG`) to
exercise the harvester's rejection path.

**2. Start the harvester**

```bash
python harvester.py
```

The harvester connects to all 3 ports, parses each line against
`LOG_PATTERN`, and writes valid records to disk under `partitions/`, named
`<module>_<level>.bin` (e.g. `flipkart-orders_ERROR.bin`). It reconnects
automatically if a connection drops. Every 3 seconds it prints a live
per-branch, per-level record count to the console. Press `Ctrl+C` to stop
it and flush/close all open partition files.

**3. Read back a partition file**

```bash
python read_binary.py partitions/flipkart-orders_ERROR.bin
```

This decodes the binary file and returns a list of dicts, each with
`timestamp`, `level`, `module`, and `activity`.

> **Note:** as currently written, `read_binary.py`'s `__main__` block parses
> the file into `records` but never prints them — the script will run and
> exit silently. Add a loop such as:
> ```python
> for r in read_records(sys.argv[1]):
>     print(r)
> ```
> right after the `records = read_records(...)` call to see output.

## Binary record format

Each record in a partition file is stored as:

```
[4 bytes] record_length          (big-endian uint32)
[19 bytes] timestamp             (ASCII, space-padded to 19 chars: "YYYY-MM-DD HH:MM:SS")
[1 byte]  level_code             (0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR)
[2 bytes] module_name_length     (big-endian uint16)
[N bytes] module_name            (UTF-8)
[2 bytes] activity_length        (big-endian uint16)
[M bytes] activity               (UTF-8)
```

`record_length` covers everything **after** the 4-byte length prefix itself
(i.e. timestamp + level + module length/name + activity length/text).

## Log line format expected by the harvester

```
YYYY-MM-DD HH:MM:SS | LEVEL | module-name | free text activity
```

Where `LEVEL` is one of `DEBUG`, `INFO`, `WARNING`, `ERROR`. Lines that
don't match this pattern are counted as `REJECTED` in the harvester's live
stats and are not written to disk.

## Known limitations

- `server.py` and `harvester.py` must be run from the same working
  directory (or `partitions/` won't line up), since `PARTITION_DIR` is a
  relative path.
- The harvester creates one partition file per `(module, level)` pair the
  first time it sees that combination — files aren't pre-created, so a
  quiet module/level combination simply won't have a file yet.
- `read_binary.py` needs the small one-line fix noted above to actually
  print decoded records.


#week-2
# Flipkart MapReduce Engine – Week 2

## Project Overview
The Flipkart MapReduce Engine is a simplified implementation of the MapReduce programming model using Python. The project demonstrates how large datasets can be processed by dividing the work into multiple stages such as splitting, mapping, partitioning, sorting, and reducing. It simulates the core workflow of distributed data processing used in Big Data frameworks like Hadoop.

## Domain
Flipkart E-Commerce

## Objective
To design and implement a basic MapReduce Engine that processes input data efficiently through multiple processing stages and generates the final aggregated output.

## Features
- Splits input data into smaller chunks.
- Generates intermediate key-value pairs.
- Partitions data using hash partitioning.
- Sorts partitioned data.
- Reduces grouped keys to generate final output.
- Modular implementation using separate Python files.

## Project Structure

```
week-2/
│── master.py
│── splitter.py
│── mapper.py
│── partitioner.py
│── sorter.py
│── reducer.py
│── input.txt
│── chunks/
│── mapped/
│── partitions/
│── sorted/
│── output.txt
│── README.md
```

## Modules

### master.py
Controls the complete execution of the MapReduce Engine by calling all modules in sequence.

### splitter.py
Reads the input file and divides it into multiple chunks.

### mapper.py
Processes each chunk and produces intermediate key-value pairs.

### partitioner.py
Uses hash partitioning to distribute mapper output into partition files.

### sorter.py
Sorts each partition so identical keys are grouped together.

### reducer.py
Aggregates all values for each key and generates the final output.

## Workflow

1. Read input.txt
2. Split the input into chunks
3. Execute Mapper
4. Partition mapper output
5. Sort partition files
6. Execute Reducer
7. Generate output.txt

## Technologies Used

- Python 3.x
- Visual Studio Code
- File Handling
- Hashing
- MapReduce Concepts

## Sample Input

```
Mobile
Laptop
Mobile
TV
Laptop
Mobile
Headphone
TV
```

## Sample Output

```
Headphone 1
Laptop 2
Mobile 3
TV 2
```

## How to Run

Open the project in Visual Studio Code and execute:

```bash
python master.py
```

## Learning Outcomes

- Understand MapReduce Architecture
- Data Splitting
- Mapping
- Hash Partitioning
- Sorting
- Reducing
- Modular Programming
- Big Data Processing Concepts

## Author

**vignesh**

**Course:** Bachelor of Computer Applications (BCA)

**Subject:** Big Data Analytics Laboratory
