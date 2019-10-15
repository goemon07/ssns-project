import time
import struct

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

        net = self.dev.get_network()
        net.start_discovery_process()
        net.add_device_discovered_callback(_device_discovered)

    def stop(self):
        self.dev.close()

    def device_discovered(self, dev: RemoteZigBeeDevice):
        print(dev.get_64bit_addr(), 'joined the network')

    def data_received(self, msg: XBeeMessage):
        type = msg.data[:4].decode('UTF-8')
        print(msg.remote_device.get_64bit_addr(), 'sent', type)
        if type == 'HELO':
            self.dev.send_data(msg.remote_device, b'HELO')
        elif type == 'DATA':
            data = struct.unpack('fffff', msg.data[4:])
            print(data)
            pass


if __name__ == '__main__':
    server = RoutingServer()
    server.start('/dev/ttyACM0')
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
