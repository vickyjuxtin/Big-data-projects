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
