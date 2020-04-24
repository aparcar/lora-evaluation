#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>

#define VBATPIN A7
#define PIN_CS 8
#define PIN_RST 4
#define PIN_IRQ 3
#define FREQ 915E6

void LoRa_rxMode()
{
  LoRa.disableInvertIQ();
  LoRa.receive();
}

void onReceive(int packetSize)
{
  String message = "";

  while (LoRa.available())
  {
    message += (char)LoRa.read();
  }

  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  JsonObject obj = doc.as<JsonObject>();
  obj["rssi"] = LoRa.packetRssi();
  obj["snr"] = LoRa.packetSnr();
  serializeJson(doc, Serial);
  Serial.println();
}

void setup()
{
  Serial.begin(9600); // initialize serial
  while (!Serial)
    ;

  LoRa.setPins(PIN_CS, PIN_RST, PIN_IRQ);

  if (!LoRa.begin(FREQ))
  {
    Serial.println("LoRa init failed. Check your connections.");
    while (true)
      ; // if failed, do nothing
  }

  LoRa.onReceive(onReceive);
  LoRa_rxMode();
}

void loop()
{
}
