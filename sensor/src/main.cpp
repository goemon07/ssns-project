#include <Arduino.h>
#include <SparkFun_MMA8452Q.h>
#include <DHT.h>
#include <XBee.h>

#if !defined(DHT_PIN)
#define DHT_PIN 13
#endif
#define DHT_TYPE DHT22

// Delay in ms between data messages
#define DELAY 500
// Delay if error during message transmission
#define ERROR_DELAY 2000
// Read temperature every n messages
#define TEMPERATURE_SPEED 4
// Send heartbeat every n messages (if no data)
#define HEARTBEET_SPEED 20

// Enable to debug on the serial adapter
// #define SERIAL_DEBUG 1

DHT dht(DHT_PIN, DHT_TYPE);
MMA8452Q accel;
XBee xbee;
XBeeAddress64 sink;
long int i = 0;
bool heartbeatRequired = true;

bool trySend(uint8_t *payload, int payloadLength) {
#ifdef SERIAL_DEBUG
  payload[4] = 0;
  Serial.print("> ");
  Serial.print((char*)payload);
  Serial.print(" (");
  Serial.print(payloadLength);
  Serial.println(" bytes)");
  return true;
#else
  // Discard all incoming packets
  while (xbee.readPacket(10));

#ifdef ZIGBEE_RETRY
  for (int retry = 0; retry < 3; retry++) {
    ZBTxRequest req = ZBTxRequest(sink, payload, payloadLength);
    xbee.send(req);
    while (xbee.readPacket(2000) && xbee.getResponse().isAvailable()) {
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
#else
  // No retry
  ZBTxRequest req = ZBTxRequest(sink, payload, payloadLength);
  xbee.send(req);
#endif
#endif
}

void logRemote(const char *msg) {
  uint8_t payload[strlen(msg) + 4] = { [0] = 'L', 'O', 'G', '_' };
  memcpy(payload + 4, msg, strlen(msg));

  trySend(payload, sizeof(payload));
}

void handshake() {
  uint8_t payload[36] = { [0] = 'H', 'E', 'L', 'O' };
  ZBTxRequest req = ZBTxRequest(XBeeAddress64(), payload, sizeof(payload));

  while (1) {
    xbee.send(req);
    bool retry = false;
    while (!retry && xbee.readPacket(5000) && xbee.getResponse().isAvailable()) {
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
          char buf[100];
          sprintf(buf, "%lx %lx", (unsigned long) rxResponse.getRemoteAddress64().getMsb(), (unsigned long) rxResponse.getRemoteAddress64().getLsb());
          logRemote(buf);

          // TODO: Handle key exchange

          return;
        }
      }
    }
  }
}

void setup() {
#ifdef SERIAL_DEBUG
  Serial.begin(9600);
#endif

  // Set up sensors
  Wire.begin();
  if(accel.begin()) {
    accel.setScale(SCALE_2G);
  }
  dht.begin();

#ifndef SERIAL_DEBUG

  // Set up serial and xbee
  Serial.begin(115200);
  xbee.begin(Serial);

  // Wait for xbee modem to initialize
  delay(5000);

  // Execute handshake
  handshake();
#endif

}

void loop() {
  long start = millis();

  float data[5] = { NAN, NAN, NAN, NAN, NAN };

  // Read temperature sensor every 2s
  if ((i % TEMPERATURE_SPEED) == 0) {
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
    if (!isnan(data[i])) {
      hasData = true;
      break;
    }
  }

  uint8_t *payload = (uint8_t*) malloc(32);
  int payloadLength = 0;

  i++;

  if (hasData) {
    payload[0] = 'D';
    payload[1] = 'A';
    payload[2] = 'T';
    payload[3] = 'A';
    payloadLength = 28;
    memcpy(payload + 4, data, 20);
    memcpy(payload + 24, &i, sizeof(i));
    heartbeatRequired = false;
  } else if ((i % HEARTBEET_SPEED) == 0) {
    if (heartbeatRequired) {
      payload[0] = 'B';
      payload[1] = 'O';
      payload[2] = 'O';
      payload[3] = 'P';
      payloadLength = 4;
    }

    heartbeatRequired = true;
  }

  if (!payload || trySend(payload, payloadLength)) {
    long timeout = max((start - millis()) + DELAY, 10);
    delay(timeout);
  } else {
    delay(ERROR_DELAY);
  }

  free(payload);
}
