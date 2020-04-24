#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <Wire.h>

#define VBATPIN A7
#define PIN_CS 8
#define PIN_RST 4
#define PIN_IRQ 3
#define INTERVAL 10000
#define DHTTYPE DHT22 // DHT 22 (AM2302)
#define DHTPIN 13

unsigned txNumber;

const long frequency = 915E6; // LoRa Frequency

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

float get_voltage()
{
  float measuredvbat = analogRead(VBATPIN);
  measuredvbat *= 2;    // we divided by 2, so multiply back
  measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
  measuredvbat /= 1024; // convert to voltage
  return measuredvbat;
}

void loop()
{
  if (runEvery(INTERVAL + random(500)))
  {
    if (!LoRa.begin(frequency))
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

    doc["node"] = "feather_1";
    doc["bat"] = get_voltage();
    doc["cnt"] = txNumber++;
    String output;
    serializeJson(doc, output);
    Serial.println(output);
    LoRa_sendMessage(output);
  }
}