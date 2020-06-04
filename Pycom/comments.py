# main.py -- put your code here!
import time
import ujson
import pycom
from machine import I2C
from machine import ADC
from network import Bluetooth
from SHT35 import SHT35

# Global Vaariables
# Variables Globales
BLEConnected = False

# Functions
# Funciones


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


# Optional - Pin for reading battery voltage
# Opcional - Pin para leer el nivel de voltaje de la bateria
apin = ADC().channel(pin='P16')
# Turn of LED blinking
# Apagar el parpadeo del LED
pycom.heartbeat(False)
# Init SHT35 sensor on hardware I2C pin
# Inicializar el sensor SHT35 en los pines i2c de la placa
sensor = SHT35(I2C(0, I2C.MASTER, baudrate=20000))
# Set BLE advertisement name and manufacturer data
# Configura el nombre y datos anunciados por BLE
Bluetooth().set_advertisement(name='LoPy', service_uuid=12345)


# Callback event for on connected and on disconnected
# Llamada de retorno sobre los eventos connectado y desconectado

# Triggers Bluetooth.NEW_ADV_EVENT, Bluetooth.CLIENT_CONNECTED, or Bluetooth.CLIENT_DISCONNECTED
Bluetooth().callback(trigger=Bluetooth.CLIENT_CONNECTED |
                     Bluetooth.CLIENT_DISCONNECTED, handler=connectionCallback)

# Start sending BLE advertisements.
# Inicia los mensajes de anuncio de BLE
Bluetooth().advertise(True)


# Create and init BLE service and declare 2 characteristics
srv = Bluetooth().service(uuid=12345, isprimary=True, nbr_chars=2, start=True)


# Characteristics Bluetooth.PROP_BROADCAST, Bluetooth.PROP_READ, Bluetooth.PROP_WRITE_NR, Bluetooth.PROP_WRITE, Bluetooth.PROP_NOTIFY, Bluetooth.PROP_INDICATE, Bluetooth.PROP_AUTH, Bluetooth.PROP_EXT_PROP
# Info https://www.oreilly.com/library/view/getting-started-with/9781491900550/ch04.html
char1 = srv.characteristic(uuid=54321, properties=Bluetooth.PROP_INDICATE |
                           Bluetooth.PROP_BROADCAST | Bluetooth.PROP_NOTIFY, value=ujson.dumps({}))

char3 = srv.characteristic(uuid=54321, properties=Bluetooth.PROP_INDICATE | Bluetooth.PROP_BROADCAST |
                           Bluetooth.PROP_READ | Bluetooth.PROP_NOTIFY, value=ujson.dumps({}))

char2 = srv.characteristic(uuid=64321, value=0xff00)

# Characteristic callback events: Bluetooth.CHAR_READ_EVENT, Bluetooth.CHAR_WRITE_EVENT, Bluetooth.NEW_ADV_EVENT, Bluetooth.CLIENT_CONNECTED, Bluetooth.CLIENT_DISCONNECTED, Bluetooth.CHAR_NOTIFY_EVENT
char1_cb = char2.callback(
    trigger=Bluetooth.CHAR_WRITE_EVENT, handler=char1_cb_handler)

while True:
    time.sleep(10)
    c, h = sensor.readData()
    json = ujson.dumps({"h": h, "c": c, "v": apin()})
    if BLEConnected:
        char1.value(json)
