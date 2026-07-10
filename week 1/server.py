"""
log_server_simulator.py
------------------------
Pretends to be 3 "high-velocity" Flipkart servers
(Flipkart-Orders, Flipkart-Payments, Flipkart-Delivery).

Run this FIRST, then run log_harvester_daemon.py
"""

import socket
import threading
import random
import time
from datetime import datetime

# Simulated Flipkart modules
BRANCHES = [
    ("flipkart-orders", 9001),
    ("flipkart-payments", 9002),
    ("flipkart-delivery", 9003),
]

LEVELS = ["INFO", "WARNING", "ERROR", "DEBUG"]

# Flipkart log messages
MESSAGE_TEMPLATES = {
    "INFO": [
        "Order#{oid} placed successfully",
        "Order#{oid} payment completed",
        "Order#{oid} shipped successfully",
        "Order#{oid} delivered successfully",
    ],
    "WARNING": [
        "Order#{oid} delivery delayed",
        "Payment verification pending for Order#{oid}",
        "High order volume detected for Order#{oid}",
    ],
    "ERROR": [
        "Payment failed for Order#{oid}",
        "Order#{oid} cancelled due to stock unavailability",
        "Delivery failed for Order#{oid}",
    ],
    "DEBUG": [
        "Retrying database update for Order#{oid}",
        "Cache refreshed for Order#{oid}",
    ],
}


def build_log_line(branch_name):
    """Build one Flipkart log line."""
    level = random.choice(LEVELS)
    oid = random.randint(1000, 9999)

    message = random.choice(
        MESSAGE_TEMPLATES[level]
    ).format(oid=oid)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"{timestamp} | {level} | {branch_name} | {message}\n"


def handle_client(conn, branch_name):
    """Continuously send logs."""

    print(f"[{branch_name}] Harvester connected...")

    try:
        while True:

            line = build_log_line(branch_name)

            conn.sendall(line.encode("utf-8"))

            time.sleep(random.uniform(0.05, 0.4))

            # Send an invalid log occasionally
            if random.random() < 0.05:
                conn.sendall(
                    b"INVALID_FLIPKART_LOG\n"
                )

    except (BrokenPipeError, ConnectionResetError):

        print(f"[{branch_name}] Harvester disconnected.")

    finally:
        conn.close()


def run_branch_server(branch_name, port):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(("127.0.0.1", port))

    server.listen(1)

    print(f"[{branch_name}] Listening on Port {port}")

    while True:

        conn, addr = server.accept()

        client = threading.Thread(
            target=handle_client,
            args=(conn, branch_name),
            daemon=True
        )

        client.start()


if __name__ == "__main__":

    threads = []

    for name, port in BRANCHES:

        t = threading.Thread(
            target=run_branch_server,
            args=(name, port),
            daemon=True
        )

        t.start()

        threads.append(t)

    print("\nFlipkart Log Simulator Started...\n")

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print("\nStopping Flipkart Log Simulator...")