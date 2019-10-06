#include <Arduino.h>
#include <DHT.h>

#if !defined(DHT_PIN)
#define DHT_PIN 13
#endif

DHT *dht = new DHT();

void setup() {
  Serial.begin(9600);
  dht->setup(DHT_PIN, DHT::DHT22);
}

void loop() {
  Serial.print("Temp: ");
  Serial.print(dht->getTemperature());
  Serial.print(", Humidity: ");
  Serial.println(dht->getHumidity());

  delay(2000);
}
