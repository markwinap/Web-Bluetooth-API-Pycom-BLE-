# main.py -- put your code here!
import time
import ujson
import pycom
from machine import I2C
from machine import ADC
from network import Bluetooth
from SHT35 import SHT35


BLEConnected = False


def connectionCallback(e):
    events = e.events()
    global BLEConnected
    if events & Bluetooth.CLIENT_CONNECTED:
        BLEConnected = True
        print("Client connected")
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        BLEConnected = False
        print("Client disconnected")


def char1_cb_handler(chr, data):
    events, value = data
    if events & Bluetooth.CHAR_WRITE_EVENT:
        print("Write request")
        pycom.rgbled(int.from_bytes(bytearray(value), 'big'))
    elif events & Bluetooth.CHAR_READ_EVENT:
        print("Read Request")


apin = ADC().channel(pin='P16')

pycom.heartbeat(False)

sensor = SHT35(I2C(0, I2C.MASTER, baudrate=20000))

Bluetooth().set_advertisement(
    name='LoPy', service_uuid=12345)

Bluetooth().callback(trigger=Bluetooth.CLIENT_CONNECTED |
                     Bluetooth.CLIENT_DISCONNECTED, handler=connectionCallback)

Bluetooth().advertise(True)

srv = Bluetooth().service(uuid=12345, isprimary=True, nbr_chars=2, start=True)

char1 = srv.characteristic(uuid=54321, properties=Bluetooth.PROP_INDICATE |
                           Bluetooth.PROP_BROADCAST | Bluetooth.PROP_NOTIFY, value=ujson.dumps({}))

char2 = srv.characteristic(uuid=64321, value=0xff00)

char1_cb = char2.callback(
    trigger=Bluetooth.CHAR_WRITE_EVENT, handler=char1_cb_handler)

while True:
    time.sleep(10)
    c, h = sensor.readData()
    json = ujson.dumps({"h": h, "c": c, "v": apin()})
    if BLEConnected:
        char1.value(json)
