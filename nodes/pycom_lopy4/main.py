from network import LoRa
import socket
import ujson
import time
import machine
import pycom
from machine import ADC

from dth import DTH

print("starting")

pycom.heartbeat(False)

th = DTH("P23", 1)
time.sleep(2)

adc = ADC()
adc.vref_to_pin("P22")
adc.vref(1100)
adc_c = adc.channel(pin="P16", attn=ADC.ATTN_11DB)


lora = LoRa(mode=LoRa.LORA, region=LoRa.US915)
lora.init(
    tx_power=14,
    sf=7,
    frequency=915000000,
    coding_rate=LoRa.CODING_4_5,
    bandwidth=LoRa.BW_125KHZ,
    power_mode=LoRa.TX_ONLY,
)


s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

cnt = 0
node = "lopy4_1"


def get_voltage():
    sum = 0
    for i in range(100):
        sum += adc_c.voltage()
    return (sum / 100) * 2 / 1000


while True:
    dht_result = th.read()
    voltage = get_voltage()
    msg = ujson.dumps(
        {
            "node": node,
            "cnt": cnt,
            "bat": voltage,
            "temp": dht_result.temperature / 1.0,
            "hum": dht_result.humidity / 1.0,
        }
    )
    print(msg)
    s.send(msg)
    cnt += 1
    time.sleep(10)
