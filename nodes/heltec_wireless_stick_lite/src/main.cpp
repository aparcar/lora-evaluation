#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <Wire.h>
#include "config.h"
#include "voltage.h"

unsigned txNumber;

DHT_Unified dht(DHTPIN, DHTTYPE);

void LoRa_txMode()
{
  LoRa.idle();            // set standby mode
  LoRa.disableInvertIQ(); // normal mode
}

void LoRa_sendMessage(String message)
{
  LoRa_txMode();        // set tx mode
  LoRa.beginPacket();   // start packet
  LoRa.print(message);  // add payload
  LoRa.endPacket(true); // finish packet and send it
}

void onTxDone()
{
  LoRa.sleep(); // Go to sleep to save some engery
}

boolean runEvery(unsigned long interval)
{
  static unsigned long previousMillis = 0;
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval)
  {
    previousMillis = currentMillis;
    return true;
  }
  return false;
}

void setup()
{
  delay(1000);
  Serial.begin(9600); // initialize serial

  dht.begin();
  sensor_t sensor;
  dht.temperature().getSensor(&sensor);

  LoRa.setPins(PIN_CS, PIN_RST, PIN_IRQ);

  txNumber = 0;
  LoRa.onTxDone(onTxDone);
}

void loop()
{
  if (runEvery(INTERVAL + random(500)))
  {
    if (!LoRa.begin(FREQ))
    {
      Serial.println("LoRa begin fail");
      return;
    }
    StaticJsonDocument<256> doc;

    sensors_event_t event;
    dht.temperature().getEvent(&event);
    if (!isnan(event.temperature))
    {
      doc["temp"] = event.temperature;
    }

    dht.humidity().getEvent(&event);
    if (!isnan(event.relative_humidity))
    {
      doc["hum"] = event.relative_humidity;
    }

    doc["node"] = NODE_ID;
    doc["bat"] = get_voltage();
    doc["cnt"] = txNumber++;
    String output;
    serializeJson(doc, output);
    Serial.println(output);
    LoRa_sendMessage(output);
  }
}