# Start

This project evaluates LoRa as an alternative for existing sensor setups using other technologies like ZigBee or GSM. The current scope is to build a simple stack to gather sensor data end visualize is via an web interface.

Current approach is to run LoRa instead of LoRaWAN to avoid third party dependencies for now, however this will be evaluated in the longer run.

In the current stack Grafana is used for data visualization with data stored in a InfluxDB database. However Prometheus could be used as an alternative.

Gateways based on RaspberryPis receive LoRa packages and forward them in the database.

## Sections

Please follow the menu entries on the left to find more information on the topics.

* **Software:** Documentation on created software or setup examples.
* **Hardware:** Collection of hardware used within this project. It may help the development to have such information in a single place instead of distributed over the multiple Vendor websites.
* **Datasheets:** Similar to the hardware section collection of used documents for evaluation.