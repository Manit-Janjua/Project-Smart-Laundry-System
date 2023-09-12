import sys
from kasa import SmartPlug
import Adafruit_DHT
import time
from pubnub.pubnub import PubNub, SubscribeListener, SubscribeCallback, PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.exceptions import PubNubException
import pubnub
import asyncio
import time
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json

#import from other script
from LED import turn_off_led, turn_on_led

key = "SEP728Group1MMVS"
key = key.encode('utf-8')
def encrypt(data_to_encrypt):
    global key
    data_to_encrypt = str(data_to_encrypt).encode('utf-8')
    data_to_encrypt = pad(data_to_encrypt,16)
    cipher = AES.new(key, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(data_to_encrypt)).decode('utf-8')

def publish_to_pubnub(data):
    pubnub.publish().channel(channel).message(encrypt(data)).sync()

pnconf = PNConfiguration()

pnconf.publish_key = 'pub-c-089b5dc9-cf8d-432a-b6b2-2f618d295537'
pnconf.subscribe_key = 'sub-c-c807563f-cc5b-47e0-a81c-bc56a9339313'
pnconf.uuid = 'abc'

pubnub = PubNub(pnconf)

channel = 'SEP728_Group1'

# my_listener = SubscribeListener()
# pubnub.add_listener(my_listener)

pubnub.subscribe().channels(channel).execute()
# my_listener.wait_for_connect()
# print('***************Connected to PubNub***************')

async def get_sensor_data():
    ip = '192.168.2.34' #Home
    # ip = "192.168.0.151" #LAB
    dev = SmartPlug(ip)

    try:            
        await dev.update()
        # print('***************Connected to the smart plug***************')
        voltage = dev.emeter_realtime['voltage']
        current = dev.emeter_realtime['current']
        power = round(dev.emeter_realtime['power'],2)
        
        if dev.is_on:
            plugStatus = 'ON'
        else:
            plugStatus = 'OFF'

        time = dev.time.strftime("%Y-%m-%d %H:%M:%S")
        
        #get 'humidity' and 'temperature' data. Function is defied in 'tenst_sensors.py'
        sensor = Adafruit_DHT.DHT11
        pin = 4
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        
        data = {
            "plugStatus": plugStatus,
            "plugCurrent": current,
            "plugVoltage": voltage,
            "plugPower": power,
            "temperature": temperature,
            "humidity":humidity,
            "timestamp": time
        }

    except Exception as e:
        data = {
            "plugStatus": 'N/A',
            "plugCurrent": 'N/A',
            "plugVoltage": 'N/A',
            "plugPower": 'N/A',
            "temperature": 'N/A',
            "humidity":'N/A',
            "timestamp": 'N/A',
            "timerData": 'false',
            "action": '6',
            'errorCode': '1',
            'errorDescription': 'Plug is disconnected'
        }

        turn_on_led('red')
        print(str(e))
        print(data)
        
        publish_to_pubnub(data)
        sys.exit(1)

    return data

