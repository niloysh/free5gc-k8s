#!/usr/local/bin/python
import os
import json
import logging
import re
import subprocess
import time

from prometheus_client import start_http_server, Gauge, REGISTRY
from prometheus_client import PLATFORM_COLLECTOR, PROCESS_COLLECTOR, GC_COLLECTOR

# Define constants
DEFAULT_SERVER_PORT = 9000
DEFAULT_SLEEP_INTERVAL = 10
DEFAULT_GTP_IFNAME = 'upfgtp'

# Read environment variables
SERVER_PORT = int(os.environ.get('SERVER_PORT', DEFAULT_SERVER_PORT))
SLEEP_INTERVAL = int(os.environ.get('SLEEP_INTERVAL', DEFAULT_SLEEP_INTERVAL))
GTP_IFNAME = os.environ.get('GTP_IFNAME', DEFAULT_GTP_IFNAME)

# Define Prometheus metrics
PACKET_COUNT = Gauge('pdr_packet_count', 'Number of packets', [
                     'seid', 'pdrid', 'n3_ip', 'n4_ip', 'direction'])
BYTE_COUNT = Gauge('pdr_byte_count', 'Number of bytes', [
                   'seid', 'pdrid', 'n3_ip', 'n4_ip', 'direction'])

# Unregister default Prometheus collectors
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(GC_COLLECTOR)


def extract_hostname():
    hostname = str(os.getenv('HOSTNAME'))
    parts = hostname.split('-')
    if len(parts) < 2:
        return hostname
    upf = parts[1].upper()
    return upf


logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s | {extract_hostname()} | %(levelname)s | %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)


def set_prometheus_metrics(pdr_stats_list):
    for pdr in pdr_stats_list:
        ul_label = {'seid': pdr['seid'], 'pdrid': pdr['pdrid'],
                    'n3_ip': pdr['n3_ip'], 'n4_ip': pdr['n4_ip'], 'direction': 'UL'}
        dl_label = {'seid': pdr['seid'], 'pdrid': pdr['pdrid'],
                    'n3_ip': pdr['n3_ip'], 'n4_ip': pdr['n4_ip'], 'direction': 'DL'}
        PACKET_COUNT.labels(**ul_label).set(pdr['ul_packet_count'])
        PACKET_COUNT.labels(**dl_label).set(pdr['dl_packet_count'])
        BYTE_COUNT.labels(**ul_label).set(pdr['ul_byte_count'])
        BYTE_COUNT.labels(**dl_label).set(pdr['dl_byte_count'])


def get_pdr_stats():
    command = ['./gogtp5g-tunnel', 'list', 'stats']
    # Run the command and capture the output
    output = subprocess.check_output(command)
    return parse_stats(output)


def parse_stats(output):
    try:
        stats = json.loads(output)
    except (json.JSONDecodeError, TypeError):
        logging.warning("Invalid PDR statistics format...")
        return []

    if stats is None:
        logging.warning("No PDR statistics found...")
        return []

    pdr_stats_list = []
    for s in stats:
        pdr_stats = {
            'seid': s['SEID'],
            'pdrid': s['ID'],
            'ul_packet_count': s['UL_PKT_CNT'],
            'dl_packet_count': s['DL_PKT_CNT'],
            'ul_byte_count': s['UL_BYTE_CNT'],
            'dl_byte_count': s['DL_BYTE_CNT'],
            'timestamp': int(time.time()),
            'n3_ip': get_upf_ip_addr('n3'),
            'n4_ip': get_upf_ip_addr('n4')
        }
        pdr_stats_list.append(pdr_stats)
    return pdr_stats_list


def get_upf_ip_addr(iface: str) -> str:
    """
    Returns the IP address of the interface.
    """
    try:
        output = subprocess.check_output(["ip", "addr", "show", iface])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command {e.cmd} failed with error {e.returncode}: {e.stderr}")
    except Exception as e:
        raise RuntimeError(f"Error executing command: {e}")

    ipv4_regex = r'inet ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)'
    match = re.search(ipv4_regex, output.decode())
    if match:
        return match.group(1)
    else:
        raise RuntimeError("IP address not found in output")


def log_data(data):
    for log in data:
        packet_counts = f"({log['ul_packet_count']}, {log['dl_packet_count']})"
        byte_counts = f"({log['ul_byte_count']}, {log['dl_byte_count']})"
        seid, pdrid, n3_ip, n4_ip = log['seid'], log['pdrid'], log['n3_ip'], log['n4_ip']
        log_str = f"seid={seid} | pdrid={pdrid} | packet_counts={packet_counts} | byte_counts={byte_counts} | n3_ip={n3_ip} | n4_ip={n4_ip}"
        logging.info(log_str)


def main():
    start_http_server(SERVER_PORT)
    logging.info(f"Starting Prometheus server on port {SERVER_PORT}...")
    while True:
        try:
            pdr_stats = get_pdr_stats()
            if pdr_stats:
                log_data(pdr_stats)
                set_prometheus_metrics(pdr_stats)
        except Exception as e:
            logging.exception(e)

        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    main()