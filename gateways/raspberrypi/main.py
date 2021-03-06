import serial
import json
import logging
import sys
from influxdb import InfluxDBClient
from influxdb import SeriesHelper

from configparser import ConfigParser

from lorareceiver import LoRaReceiver

config = ConfigParser(allow_no_value=True)
config.read("config.ini")

logging.basicConfig(
    level=config["main"]["logging_level"],
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stderr)],
)

client = InfluxDBClient(
    config["influx"]["host"],
    config["influx"]["port"],
    config["influx"]["user"],
    config["influx"]["pass"],
    config["influx"]["database"],
)
client.create_database(config["influx"]["database"])


class BasicSeriesHelper(SeriesHelper):
    class Meta:
        client = client
        series_name = "events.stats.basic"
        fields = ["temp", "hum", "cnt", "rssi", "snr", "bat"]
        tags = ["gateway", "node"]
        bulk_size = 5
        autocommit = True


nodes = {}
for node in config["nodes"].keys():
    nodes[node] = 0

receiver = LoRaReceiver(config["receiver"])

while True:
    msg = receiver.receive_json()

    if not msg:
        logging.debug(f"skip empty message")
        continue

    node = msg.pop("node", None)
    if not node:
        logging.error(f"node attribute missing in '{msg}'")
        continue

    if node not in nodes:
        logging.info(f"skip unknown node {node}")
        continue

    current_cnt = msg.get("cnt", 0) or 0

    msg_cnt_diff = current_cnt - nodes.get(node, 0)
    if msg_cnt_diff > 1:
        logging.warning(f"missed {msg_cnt_diff} message(s) from {node}")
    elif msg_cnt_diff < 1:
        logging.warning(f"missed {msg_cnt_diff} message(s) from {node}")

    nodes[node] = current_cnt

    BasicSeriesHelper(
        gateway="feather_gw",
        node=node,
        temp=float(msg.get("temp", 0)),
        hum=float(msg.get("hum", 0)),
        bat=float(msg.get("bat", 0)),
        snr=float(msg.get("snr", 0)),
        cnt=msg.get("cnt", 0),
        rssi=msg.get("rssi", -200),
    )
