#include <Arduino.h>
#include <SparkFun_MMA8452Q.h>
#include <DHT.h>
#include <XBee.h>

#if !defined(DHT_PIN)
#define DHT_PIN 13
#endif
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);
MMA8452Q accel;
XBee xbee;
XBeeAddress64 sink = XBeeAddress64();
int i = 0;

void handshake() {
  uint8_t payload[36] = { [0] = 'H', 'E', 'L', 'O' };
  ZBTxRequest req = ZBTxRequest(XBeeAddress64(), payload, sizeof(payload));

  while (1) {
    xbee.send(req);
    bool retry = false;
    while (!retry && xbee.readPacket(1000) && xbee.getResponse().isAvailable()) {
      switch (xbee.getResponse().getApiId()) {
      case ZB_TX_STATUS_RESPONSE:
      {
        ZBTxStatusResponse txStatus;
        xbee.getResponse().getTxStatusResponse(txStatus);
        if (txStatus.isError()) {
          retry = true;
        }
        break;
      }
      case ZB_RX_RESPONSE:
      {
        ZBRxResponse rxResponse;
        xbee.getResponse().getZBRxResponse(rxResponse);
        sink = rxResponse.getRemoteAddress64();

        // TODO: Handle key exchange
        
        return;
      }
      }
    }
  }
}

void setup() {
  // Set up sensors
  Wire.begin();
  if(accel.begin() == false) {
    Serial.println("Error initializing MMA8452Q.");
  }
  dht.begin();


  // Set up serial and xbee
  Serial.begin(115200);
  xbee.begin(Serial);

  // Wait for xbee modem to initialize
  delay(5000);

  // Execute handshake
  handshake();
}

void loop() {
  float data[5] = { NAN, NAN, NAN, NAN, NAN };

  // Read temperature sensor every 2s
  if (i % 20 == 0) {
    data[0] = dht.readTemperature();
    data[1] = dht.readHumidity();
  }

  // Read accelerometer every 100ms
  if (accel.available()) {
    data[2] = accel.getCalculatedX();
    data[3] = accel.getCalculatedY();
    data[4] = accel.getCalculatedZ();
  }

  uint8_t payload[24] = { [0] = 'D', 'A', 'T', 'A' };
  memcpy(payload + 4, data, 20);
  i++;

  ZBTxRequest req = ZBTxRequest(XBeeAddress64(), payload, sizeof(payload));
  for (int retry = 0; retry < 3; retry++) {
    xbee.send(req);
    while (xbee.readPacket(100) && xbee.getResponse().isAvailable()) {
      switch (xbee.getResponse().getApiId()) {
      case ZB_TX_STATUS_RESPONSE:
        ZBTxStatusResponse txStatus;
        xbee.getResponse().getTxStatusResponse(txStatus);
        if (txStatus.isSuccess()) {
          delay(250);
          return;
        }
        break;
      }
    }
  }
  delay(2000);
}
