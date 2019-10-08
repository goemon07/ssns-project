#include <Arduino.h>
#include <SparkFun_MMA8452Q.h>
#include <DHT.h>

#if !defined(DHT_PIN)
#define DHT_PIN 13
#endif
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);
MMA8452Q accel;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  if(accel.begin() == false) {
    Serial.println("Error initializing MMA8452Q.");
  }
  dht.begin();
}

void loop() {

  Serial.print("Temp: ");
  Serial.println(dht.readTemperature());
  Serial.print("Humidity: ");
  Serial.println(dht.readHumidity());

  if (accel.available()) {      
    Serial.print("X: ");
    Serial.print(accel.getCalculatedX(), 3);
    Serial.print("\tY: ");
    Serial.print(accel.getCalculatedY(), 3);
    Serial.print("\tZ: ");
    Serial.print(accel.getCalculatedZ(), 3);
    Serial.println("\n");
  }
  delay(2000);
}
