import board
import adafruit_rfm9x
import digitalio
import json
import logging
import busio


class LoRaReceiver:
    """Recieve LoRa messages from RFM9x antenna"""

    def __init__(self, config):
        """Init LoRa receiver on pins set in configuration

        Initialize the RFM9x module, passed configuration requires pin_nss,
        pin_rst and freq.
        
        Args:
            config (dict): Configuration for RFM9x modul
        """
        NSS = digitalio.DigitalInOut(getattr(board, config["pin_nss"]))
        RST = digitalio.DigitalInOut(getattr(board, config["pin_rst"]))
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.rfm9x = adafruit_rfm9x.RFM9x(spi, NSS, RST, float(config["freq"]))

    def receive_raw(self):
        """Receive LoRa message and RSSI value

        Returns:
            tuple: containing packet as string and RSSI ans integer
        """
        packet = self.rfm9x.receive(timeout=1200, with_header=True)
        if packet:
            return (packet, self.rfm9x.rssi)
        else:
            return (None, None)

    def receive_json(self):
        """Receive LoRa message and parse containing JSON

        Retusn:
            dict: Parsed LoRa message plus RSSI
        """
        packet, rssi = self.receive_raw()
        try:
            logging.debug(f"{packet}")
            msg = json.loads(packet)
        except json.JSONDecodeError:
            logging.error(f"json decoding failed on '{packet}'")
            return None
        except UnicodeDecodeError:
            logging.error(f"broken message '{packet}'")
            return None

        if not isinstance(msg, dict):
            logging.warning(f"Packet was not interpret as dict")
            logging.debug(f"Packet: {packet}")
            return None
            
        msg["rssi"] = rssi
        return msg