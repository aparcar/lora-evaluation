import serial
import json
import logging
import sys
from influxdb import InfluxDBClient
from influxdb import SeriesHelper

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler(sys.stderr)],
)

client = InfluxDBClient("localhost", 8086, "root", "root", "uhmdemo")
client.create_database("uhmdemo")

nodes = {}


class BasicSeriesHelper(SeriesHelper):
    class Meta:
        client = client
        series_name = "events.stats.basic"
        fields = ["temp", "hum", "cnt", "rssi", "snr", "bat"]
        tags = ["gateway", "node"]
        bulk_size = 1
        autocommit = True


while True:
    with serial.Serial("/dev/ttyACM0", 19200) as ser:
        line = ser.readline()  # read a '\n' terminated line
        try:
            logging.debug(f"{line}")
            msg = json.loads(line)
        except json.JSONDecodeError:
            logging.error(f"json decoding failed on '{line}'")
            continue
        except UnicodeDecodeError:
            logging.error(f"broken message '{line}'")
            continue

        if not msg:
            logging.debug(f"skip empty message")
            continue

        node = msg.pop("node", None)
        if not node:
            logging.error(f"node attribute missing in '{line}")
            continue

        if node in nodes:
            msg_cnt_diff = msg.get("cnt", 0) - nodes[node].get("cnt", 0)
            if msg_cnt_diff > 1:
                logging.warning(f"missed {msg_cnt_diff} message(s) from {node}")
            elif msg_cnt_diff < 1:
                logging.warning(f"missed {msg_cnt_diff} message(s) from {node}")

        nodes[node] = msg

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
