import asyncio
import time
from pubnub.pubnub import PubNub, PNStatusCategory
import pubnub
from pubnub.pnconfiguration import PNConfiguration
from kasa import SmartPlug
import sys

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json

#import from other script
from main2 import get_sensor_data
# from main import cancel_timer
from LED import turn_off_led, turn_on_led


pnconf = PNConfiguration()

pnconf.publish_key = 'pub-c-089b5dc9-cf8d-432a-b6b2-2f618d295537'
pnconf.subscribe_key = 'sub-c-c807563f-cc5b-47e0-a81c-bc56a9339313'
pnconf.uuid = 'abc'

pubnub = PubNub(pnconf)

channel = 'SEP728_Group1'
pubnub.subscribe().channels(channel).execute()

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

current_limit = 0.1
humidity_limit = 50
temperature_limit = 50

async def system_monitor():
    ip = '192.168.2.34' #home
    # ip = '192.168.0.151' #LAB
    dev = SmartPlug(ip)

    while True:
        # print(f'system monitoring is on')

        data = await get_sensor_data()
        print('system_monitor: data is received')
        current = data['plugCurrent']
        humidity = data['humidity']
        temperature = data['temperature']
        
        print(f'system monitor: current={current} | humidity={humidity} | temperature={temperature}')

        if current > current_limit:
            await dev.turn_off()
            data['timerData'] = 'false'
            data['action'] = '3'
            data['errorCode'] = '2'
            data['errorDescription'] = 'machine overload'

            print(f'system monitor: kill switch!!')
            print(data)
            turn_on_led('red')

            publish_to_pubnub(data)
            
            break
        elif temperature > temperature_limit:
            await dev.turn_off()
            data['timerData'] = 'false'
            data['action'] = '3'
            data['errorCode'] = '3'
            data['errorDescription'] = 'high temperature'

            print(f'system monitor: kill switch!!')
            print(data)
            turn_on_led('red')

            publish_to_pubnub(data)
            
            break

        time.sleep(3)

asyncio.run(system_monitor())
