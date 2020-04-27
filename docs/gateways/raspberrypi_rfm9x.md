# RaspberryPi RFM9x InfluxDB gateway

This setup describes a RaspberryPi receiving LoRa messages via an attached
RFM9x antenna. Currently received packages are expected to contain JSON
strings, however MsgPack and CayenneLPP should be explored as more compact
alternatives.

Messages are stored in batches of five and then uploaded to the InfluxDB
backend. It may run on the RaspberryPi for testing or on an external server.

## `config.ini`

The config file should be edited before starting the script. The section
`nodes` should be treated as a list of names. This option avoids to store
corrupted messages with bad wrong nodes names in the InfluxDB database.

## RaspberryPi setup

The RaspberryPi is expected to run Raspbian and have Python3 and `pip`
installed. Also a network connection to the backend InfluxDB is required. To
install all script requirements run the following command:

```bash
pip install -r requirements.txt
```

## RFM9x wiring

The used RFM9x is a sold as *SX1276 Lora Module for Arduino* and produced by
*blkbox*. It is available at [tindie][tindie].

Below a table of the pins:

| RFM9x | Function  | RPi Pin | RPi GPIO |
| ----- | --------- | ------- | -------- |
| PIN1  | GND       | 6       | -        |
| PIN2  | VIN (3.3) | 1       | -        |
| PIN3  | MISO      | 21      | -        |
| PIN4  | MOSI      | 19      | -        |
| PIN5  | CLK       | 23      | -        |
| PIN6  | nSS       | 22      | D25      |
| PIN7  | nRST      | 11      | D17      |
| PIN14 | GPIO0     | 7       | unused   |

[tindie]: https://www.tindie.com/products/blkbox/sx1276-lora-module-for-arduino/

## Running the Python script

Run the `main.py` script via `nohup` or `tmux` to keep it running on the
RaspberryPi even after closing down a SSH connection.

An example output is attached below. It is possible to change the debug level
to `DEBUG` to print all received messages

```bash
2020-04-27 07:01:56,651 [ERROR] broken message 'bytearray(b'{"node":"feather_2","bat":3.:\xb7\xd7\\\xdc\x7f\xb4\xbc\xa7%\xe9!\xdeM\xf5\xd9 \xd6\xf9')'
2020-04-27 07:02:16,780 [WARNING] missed 3 message(s) from feather_1
2020-04-27 07:02:36,909 [WARNING] missed 5 message(s) from feather_2
```

The logs show that messages arrive partly broken.