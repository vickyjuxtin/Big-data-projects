"""
read_binary_logs.py
--------------------
Reads back one binary partition file and decodes it into
human-readable Flipkart log records.

Usage:
    python read_binary_logs.py partitions/flipkart-orders_ERROR.bin
"""

import struct
import sys

LEVEL_CODE = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3
}

CODE_LEVEL = {v: k for k, v in LEVEL_CODE.items()}


def read_records(filepath):

    with open(filepath, "rb") as f:
        data = f.read()

    offset = 0
    records = []

    while offset < len(data):

        # Read record length
        (record_len,) = struct.unpack_from("!I", data, offset)
        offset += 4

        # Read complete record
        record_bytes = data[offset: offset + record_len]
        offset += record_len

        # Decode record
        ts_bytes, level_byte, module_len = struct.unpack_from(
            "!19sBH",
            record_bytes,
            0
        )

        pos = 19 + 1 + 2

        module = record_bytes[pos: pos + module_len].decode("utf-8")
        pos += module_len

        (activity_len,) = struct.unpack_from("!H", record_bytes, pos)
        pos += 2

        activity = record_bytes[pos: pos + activity_len].decode("utf-8")

        records.append(
            {
                "timestamp": ts_bytes.decode("ascii").strip(),
                "level": CODE_LEVEL[level_byte],
                "module": module,
                "activity": activity,
            }
        )

    return records


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print