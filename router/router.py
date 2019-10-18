import sys
import math
import time
import struct
import json
from math import isnan

import requests

from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice
from digi.xbee.models.message import XBeeMessage


class RoutingServer:
    dev: ZigBeeDevice

    def __init__(self):
        self.dev = None

    def start(self, port):
        self.dev = ZigBeeDevice(port, 115200)
        self.dev.open()

        print('Starting router on', self.dev.get_64bit_addr())

        def _device_discovered(dev: RemoteZigBeeDevice):
            self.device_discovered(dev)

        def _data_received(msg: XBeeMessage):
            self.data_received(msg)

        self.dev.add_data_received_callback(_data_received)

    def stop(self):
        self.dev.close()

    def device_discovered(self, dev: RemoteZigBeeDevice):
        print(dev.get_64bit_addr(), 'joined the network')

    def data_received(self, msg: XBeeMessage):
        try:
            type = msg.data[:4].decode('UTF-8')
            if type == 'HELO':
                requests.post('http://localhost:5000/api/v1/node/register', json={
                    'serial': str(msg.remote_device.get_64bit_addr())
                })
                self.dev.send_data(msg.remote_device, b'HELO')
                print(msg.remote_device.get_64bit_addr(), 'has been registered')
            elif type == 'DATA':
                data = struct.unpack('fffff', msg.data[4:24])
                idx = int.from_bytes(msg.data[-4:], 'little')
                print(msg.remote_device.get_64bit_addr(), idx, data)
                measurements = dict(filter(lambda x: not math.isnan(x[1]), zip(range(len(data)), data)))
                requests.post('http://localhost:5000/api/v1/measurements', json={
                    'serial': str(msg.remote_device.get_64bit_addr()),
                    'data': measurements
                })
                pass
            elif type == 'LOG_':
                print(msg.remote_device.get_64bit_addr(), msg.data[4:].decode('UTF-8'))
            elif type == 'BOOP':
                print(msg.remote_device.get_64bit_addr(), 'is alive (but has no data)')
            else:
                print('Unknown message type:', type)
        except BaseException as e:
            print(e)


if __name__ == '__main__':
    server = RoutingServer()
    port = sys.argv[0] if len(sys.argv) == 1 else '/dev/ttyACM0'
    server.start(port)
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
