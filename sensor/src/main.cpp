#include <Arduino.h>
#include <SparkFun_MMA8452Q.h>
#include <DHT.h>
#include <XBee.h>

#if !defined(DHT_PIN)
#define DHT_PIN 13
#endif
#define DHT_TYPE DHT22

// Delay in ms between data messages
#define DELAY 250
// Delay if error during message transmission
#define ERROR_DELAY 2000
// Read temperature every n messages
#define TEMPERATURE_SPEED 8
// Send heartbeat every n messages (if no data)
#define HEARTBEET_SPEED 40

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

bool trySend(uint8_t *payload, int payloadLength) {
  ZBTxRequest req = ZBTxRequest(XBeeAddress64(), payload, payloadLength);
  for (int retry = 0; retry < 3; retry++) {
    xbee.send(req);
    while (xbee.readPacket(100) && xbee.getResponse().isAvailable()) {
      switch (xbee.getResponse().getApiId()) {
        case ZB_TX_STATUS_RESPONSE:
        {
          ZBTxStatusResponse txStatus;
          xbee.getResponse().getTxStatusResponse(txStatus);
          if (txStatus.isSuccess()) {
            return true;
          }
          break;
        }
      }
    }
  }

  return false;
}

void log(const char *msg) {
  uint8_t payload[strlen(msg) + 4] = { [0] = 'L', 'O', 'G', '_' };
  memcpy(payload + 4, msg, strlen(msg));

  trySend(payload, sizeof(payload));
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

  log("Handshake completede successfully");
}

void loop() {
  float data[5] = { NAN, NAN, NAN, NAN, NAN };

  // Read temperature sensor every 2s
  if (i % TEMPERATURE_SPEED == 0) {
    data[0] = dht.readTemperature();
    data[1] = dht.readHumidity();
  }

  // Read accelerometer every 250ms
  if (accel.available()) {
    data[2] = accel.getCalculatedX();
    data[3] = accel.getCalculatedY();
    data[4] = accel.getCalculatedZ();
  }

  bool hasData = false;
  for (unsigned int i = 0; i < sizeof(data) / sizeof(float); i++) {
    if (isnan(data[i]) != 1) {
      hasData = true;
      break;
    }
  }

  uint8_t *payload = NULL;
  int payloadLength;

  i++;

  if (hasData) {
    payload = new uint8_t[24] { 'D', 'A', 'T', 'A' };
    payloadLength = 24;
    memcpy(payload + 4, data, 20);
  } else if (i % HEARTBEET_SPEED == 0) {
    payload = new uint8_t[4] { 'B', 'O', 'O', 'P' };
    payloadLength = 4;
  } else {
    delay(DELAY);
    return;
  }

  if (trySend(payload, payloadLength)) {
    delay(DELAY);
  } else {
    delay(ERROR_DELAY);
  }
}
