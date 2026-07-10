"""
log_harvester_daemon.py
------------------------
Flipkart Log Harvester
"""

import socket
import threading
import re
import struct
import os
import time
from collections import defaultdict

BRANCHES = [
    ("flipkart-orders", 9001),
    ("flipkart-payments", 9002),
    ("flipkart-delivery", 9003),
]

HOST = "127.0.0.1"
PARTITION_DIR = "partitions"

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*"
    r"(?P<level>INFO|WARNING|ERROR|DEBUG)\s*\|\s*"
    r"(?P<module>[\w\-]+)\s*\|\s*"
    r"(?P<activity>.+)$"
)

LEVEL_CODE = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
}

CODE_LEVEL = {v: k for k, v in LEVEL_CODE.items()}

partition_files = {}
partition_locks = {}
partitions_master_lock = threading.Lock()

stats_lock = threading.Lock()
stats = defaultdict(int)

RECONNECT_DELAY_SECONDS = 3


def get_partition_file(module, level):
    key = (module, level)

    with partitions_master_lock:

        if key not in partition_files:

            os.makedirs(PARTITION_DIR, exist_ok=True)

            filename = os.path.join(
                PARTITION_DIR,
                f"{module}_{level}.bin"
            )

            partition_files[key] = open(
                filename,
                "ab"
            )

            partition_locks[key] = threading.Lock()

            print(f"[partition] Created {filename}")

        return partition_files[key]


def encode_record(timestamp, level, module, activity):

    ts_bytes = timestamp.encode("ascii").ljust(19, b" ")[:19]

    level_byte = LEVEL_CODE[level]

    module_bytes = module.encode("utf-8")

    activity_bytes = activity.encode("utf-8")

    header = struct.pack(
        "!19sBH",
        ts_bytes,
        level_byte,
        len(module_bytes)
    )

    middle = struct.pack(
        "!H",
        len(activity_bytes)
    )

    return header + module_bytes + middle + activity_bytes


def write_payload(record):
    """Write one structured payload to the correct partition file."""

    binary_record = encode_record(
        record["timestamp"],
        record["level"],
        record["module"],
        record["activity"]
    )

    length_prefix = struct.pack("!I", len(binary_record))

    key = (record["module"], record["level"])

    f = get_partition_file(
        record["module"],
        record["level"]
    )

    with partition_locks[key]:
        f.write(length_prefix + binary_record)
        f.flush()


def process_line(raw_line, branch_name):
    """Validate a log line and store it."""

    match = LOG_PATTERN.match(raw_line)

    if not match:
        with stats_lock:
            stats[(branch_name, "REJECTED")] += 1
        return

    payload = {
        "timestamp": match.group("timestamp"),
        "level": match.group("level"),
        "module": match.group("module"),
        "activity": match.group("activity"),
    }

    write_payload(payload)

    with stats_lock:
        stats[(branch_name, payload["level"])] += 1


def harvest_from_branch(branch_name, port):
    """Connect to a Flipkart server and continuously read logs.

    Reconnects automatically with a short delay if the connection
    drops or cannot be established.
    """

    while True:

        sock = None

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, port))

            print(f"[{branch_name}] Connected on port {port}")

            buffer = b""

            while True:

                chunk = sock.recv(4096)

                if not chunk:
                    print(f"[{branch_name}] Server closed connection.")
                    break

                buffer += chunk

                while b"\n" in buffer:

                    line_bytes, buffer = buffer.split(b"\n", 1)

                    try:
                        line = line_bytes.decode("utf-8").strip()
                    except UnicodeDecodeError:
                        continue

                    if line:
                        process_line(line, branch_name)

        except OSError as exc:
            print(f"[{branch_name}] Connection error: {exc}")

        finally:
            if sock is not None:
                sock.close()

        print(f"[{branch_name}] Reconnecting in {RECONNECT_DELAY_SECONDS}s...")
        time.sleep(RECONNECT_DELAY_SECONDS)


def print_stats_periodically():
    """Print live statistics every 3 seconds."""

    while True:
        time.sleep(3)

        with stats_lock:
            if not stats:
                continue

            print("\n========== Live Ingestion Stats ==========")

            for (branch, level), count in sorted(stats.items()):
                print(f"{branch:20s} {level:10s} {count}")

            print("==========================================\n")


if __name__ == "__main__":

    threads = []

    # Start one harvester thread for each Flipkart server
    for name, port in BRANCHES:
        t = threading.Thread(
            target=harvest_from_branch,
            args=(name, port),
            daemon=True
        )
        t.start()
        threads.append(t)

    # Start statistics thread
    stats_thread = threading.Thread(
        target=print_stats_periodically,
        daemon=True
    )
    stats_thread.start()

    print("Flipkart Harvester Daemon Running. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down harvester...")

        with partitions_master_lock:
            for f in partition_files.values():
                f.close()

        print("All partition files closed.")