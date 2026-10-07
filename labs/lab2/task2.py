import argparse
import csv
import json
import logging
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from os.path import exists
from pathlib import Path

RE255 = r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)"
IP_PATTERN = re.compile(rf"^(?:{RE255}\.){{3}}{RE255}$")
RE16 = r"[0-9a-fA-F]{2}"
MAC_PATTERN = re.compile(rf"^(?:{RE16}[:-]){{5}}{RE16}$")


@dataclass
class HostBinding:
    ip: str
    interface: str
    entry_type: str


@dataclass
class ConflictData:
    mac_duplicates: list[tuple[str, list[HostBinding]]]
    invalid_ips: list[str]
    invalid_macs: list[str]


class ConflictFinder:
    mac_to_host: defaultdict[str, list[HostBinding]]

    conflict_data: ConflictData

    def __init__(self):
        self.mac_to_host = defaultdict(list)
        self.conflict_data = ConflictData([], [], [])

    def append(self, mac: str, host: HostBinding) -> bool:
        is_ip_valid = bool(IP_PATTERN.match(host.ip))
        is_mac_valid = bool(MAC_PATTERN.match(mac))
        is_valid = is_mac_valid and is_ip_valid

        if not is_ip_valid:
            self.conflict_data.invalid_ips.append(host.ip)
        if not is_mac_valid:
            self.conflict_data.invalid_macs.append(mac)

        clean_mac = mac.lower().replace("-", ":")
        if is_valid and not any(h.ip == host.ip for h in self.mac_to_host[clean_mac]):
            self.mac_to_host[clean_mac].append(host)

        return is_valid

    def find(self) -> ConflictData:
        self.conflict_data.mac_duplicates = []

        for mac, ips in self.mac_to_host.items():
            if len(ips) > 1:
                self.conflict_data.mac_duplicates.append((mac, ips))

        return self.conflict_data


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ARP analyser",
        description="A utility for analyzing ARP cache snapshots from network devices and detecting anomalies",
    )
    parser.add_argument(
        "--arp-file", required=True, help="Path to ARP table CSV/text file"
    )
    parser.add_argument("--output-json")
    parser.add_argument("--detect-spoofing", action="store_true")
    parser.add_argument("--log-file")

    args = parser.parse_args()

    arp_path = Path(args.arp_file)
    if not exists(arp_path):
        print(f"File not found: '{args.arp_file}'")
        return

    logger = logging.getLogger(__name__)

    if args.log_file:
        file_handler = logging.FileHandler(args.log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    detect_spoofing = args.detect_spoofing
    conflict_finder = ConflictFinder()

    logger.info(f"Parsing ARP table from {args.arp_file}")

    with open(arp_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        _header = next(reader, None)

        for row in reader:
            if not row or len(row) < 2:
                continue

            ip = row[0].strip()
            mac = row[1].strip()
            interface = row[2].strip() if len(row) > 2 else "unknown"
            entry_type = row[3].strip() if len(row) > 3 else "dynamic"

            is_valid = conflict_finder.append(
                mac, HostBinding(ip, interface, entry_type)
            )

            if not is_valid:
                continue

        logger.info(f"Validated {reader.line_num} IP/MAC entries.")

    data = conflict_finder.find() if detect_spoofing else conflict_finder.conflict_data

    print("\n=== Validated Entries Summary ===")
    valid_count = sum(len(ips) for ips in conflict_finder.mac_to_host.values())
    invalid_count = len(data.invalid_ips) + len(data.invalid_macs)

    logger.info(f"Valid IP/MAC Pairs : {valid_count}")
    if invalid_count > 0:
        logger.warning(f"Invalid Syntax     : {invalid_count}")

    if detect_spoofing and data.mac_duplicates:
        print("\n=== CRITICAL SECURITY ALERTS: ARP-SPOOFING DETECTED ===")
        print("[ALERT] MAC Address Duplicate Conflict!\n")

        for mac, hosts in data.mac_duplicates:
            hosts_repr = [f"{h.ip} ({h.interface}/{h.entry_type})" for h in hosts]
            logger.critical(
                f"MAC Address: {mac} associated with MULTIPLE IP addresses: {', '.join(hosts_repr)}"
            )
            for host in hosts:
                print(f"    - {host.ip}")

        print("    -> POSSIBLE MAN-IN-THE-MIDDLE / ARP-SPOOFING ATTACK IN PROGRESS!")

    if args.output_json and data.mac_duplicates:
        alerts = [
            {
                "mac_address": mac,
                "hosts": [asdict(h) for h in hosts],
                "alert_level": "CRITICAL",
            }
            for mac, hosts in data.mac_duplicates
        ]
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=4)
        print(f"[INFO] Security alerts exported to {args.output_json}")


if __name__ == "__main__":
    main()
