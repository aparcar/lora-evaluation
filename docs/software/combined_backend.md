# Combined backend

This document describes the setup of a LoRa receiver storing data in a InfluxDB and offering collected stats via Grafana. The services run on a RaspberryPi combined with a Adafruit Feather M0 with RFM95 antenna to receive the data.

In later iterations the Feather M0 will be replaced by a SX127x antenna directly connected to the RasperryPi and database and web frontend should run on a virtual machine.

## RaspberryPi setup

Install the latest version of [Raspbian](raspbian) (currently 2020-02-13) on a MicroSD card and install the packages via the package manager `apt`

```bash
sudo apt install -y \
    influxdb \          # database
    python3-influxdb \  # python bindings
    python3-serial \    # access to serial console
    nohup               # to keep the script running in background
```

The Debian ports of Grafana are highly outdated and therefore the official Grafana repository is used instead:

```bash
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list 
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y grafana-rpi
```

More details on the upstream Grafana are available [here][grafana-debian].

[raspbian]: https://www.raspberrypi.org/downloads/raspbian/
[grafana-debian]: https://grafana.com/docs/grafana/latest/installation/debian/

## Receiver setup (`lora2json`)

The LoRa receiver is based on the Arduino library called [arduino-LoRa][arduino-lora] which receives LoRa messages on a single channel and prints them to a serial console in JSON format. In this setup a Feather M0 is used, however other Arduino compatible boards with a LoRa connector can be used.

The `lora2json` source code is in [gateway/src/](/lora2json/main.cpp).

For simple deployment and managing of various LoRa boards [Visual Studio Code][vscode] in combination with [PlatformIO][platformio] is used. However it is also possible to use the [Arduino IDE][arduino-ide].

The following two libraries are required:

* `#include <ArduinoJson.h>` via [ArduinoJson][arduinojson]
* `#include <LoRa.h>` via [Arduino LoRa][arduino-lora]

Once connected to a RaspberryPi or Linux running computer, a serial device is available, for the Feather M0 most likely called `/dev/ttyACM0`. This may vary between boards. Below is an example line printed by the receiver when receiving a LoRa message from a node called `heltec_wsl_1`, including temperature, humidity, a package counter, RSSI and SnR:

```json
{"temp":26.4,"hum":67.6,"node":"heltec_wsl_1","bat":0,"cnt":1233,"rssi":-58,"snr":9.25}
```

[arduino-lora](https://github.com/sandeepmistry/arduino-LoRa/)
[vscode][https://code.visualstudio.com/]
[platformio][https://platformio.org/]
[arduino-ide][https://www.arduino.cc/en/Main/Software]
[arduinojson][https://arduinojson.org/]

## InfluxDB setup

InfluxDB standard installation uses the username `root` in combination with the password `root`, this should be changed for a production setup, however is keep for this proof of concept. The database only runs on localhost and therefore is not accessible from outside.

## Grafana setup

To setup Grafana open the web interface on the RaspberryPi IP address or default hostname `raspberrypi`. The web interface runs on port `3000`. The first login works with the credential combination `admin/admin` and should be changed as the interface is, unlike the database, available in the network.

The InfluxDB is added as a datasource, running on `http://localhost:8086` with login `root/root`.

Instead of setting up the Dashboard manually it is possible to paste the included JSON file [`model.json`](/misc/grafana_dashboard.json) into the Dashboard import dialog.

## Running `json2influx` 

Once all components are installed and setup the Python script [`json2influx.py`](/lora2influx.py) that reads JSON messages from Serial and inserts them into the InfluxDB is started as following:

```bash
nohup python3 lora2influx.py &
```
It is no possible to close any used SSH connection and the script still continues to run.To see the (debug) logs run the following command:

```bash
tail -f nohup.out
```

The output should look similar to the following lines:

```bash
2020-04-24 04:39:33,197 [DEBUG] Starting new HTTP connection (1): localhost:8086
2020-04-24 04:39:33,203 [DEBUG] http://localhost:8086 "POST /query?q=CREATE+DATABASE+%22uhmdemo%22&db=uhmdemo HTTP/1.1" 200 None
2020-04-24 04:39:35,393 [DEBUG] b'{"temp":26.5,"hum":67.5,"node":"heltec_wsl_1","bat":0,"cnt":1218,"rssi":-59,"snr":9.75}\r\n'
2020-04-24 04:39:35,419 [DEBUG] http://localhost:8086 "POST /write?db=uhmdemo HTTP/1.1" 204 0
2020-04-24 04:39:37,898 [DEBUG] b'{"temp":26.3,"hum":73.8,"node":"feather_1","bat":3.925195,"cnt":2406,"rssi":-63,"snr":9.25}\r\n'
2020-04-24 04:39:37,921 [DEBUG] http://localhost:8086 "POST /write?db=uhmdemo HTTP/1.1" 204 0
```

## Result

Below is a picture of the setup running with three nodes for about 20 minutes. It shows the measured temperature, humidity, battery voltage and RSSI value.

![](/img/grafana.png)
