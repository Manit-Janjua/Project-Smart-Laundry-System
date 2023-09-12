from pubnub.pubnub import PubNub, SubscribeListener, SubscribeCallback, PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.exceptions import PubNubException
import pubnub
import time
import asyncio
from kasa import SmartPlug
import sys
import subprocess
from threading import Timer
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json

#import from other scrip
from main2 import get_sensor_data
from LED import turn_off_led, turn_on_led
# import main3

pnconf = PNConfiguration()

pnconf.publish_key = 'pub-c-089b5dc9-cf8d-432a-b6b2-2f618d295537'
pnconf.subscribe_key = 'sub-c-c807563f-cc5b-47e0-a81c-bc56a9339313'
pnconf.uuid = 'abc'

pubnub = PubNub(pnconf)

channel = 'SEP728_Group1'
pubnub.subscribe().channels(channel).execute()

time_limit = 90
time_start_since = None
timer = None

def upadte_time_start_since():
    global time_start_since
    time_start_since = time.time()

def delay_stop_machine():
    print('timer is up. turing off the machine')
    data = {'action': '1'}
    publish_to_pubnub(data)

def start_timer():
    global timer
    timer = Timer(time_limit, delay_stop_machine)
    timer.start()
    print(f'timer is started. Counting down {time_limit} seconds')

def cancel_timer():
    global timer
    if timer is None:
        print('no timer')
    else:
        timer.cancel()
        print('timer is cancelled.')
    timer = None

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

def decrypt(data_to_decrypt):
    global key
    data_to_decrypt = base64.b64decode(data_to_decrypt)
    cipher = AES.new(key, AES.MODE_ECB)
    return unpad(cipher.decrypt(data_to_decrypt),16)

turn_on_led('green')

class SubscribeHandler(SubscribeCallback):
    async def handle_message(self, pubnub, message):

        ip = '192.168.2.34' #Home
        # ip = '192.168.0.151' #LAB
        dev = SmartPlug(ip)

        data_received_from_pubnub = message.message
        data_received_from_pubnub = json.loads(decrypt(str(data_received_from_pubnub)).decode('utf-8').replace("'", '"'))
        
        if 'plugStatus' in data_received_from_pubnub:
            return
        
        elif data_received_from_pubnub['action'] == '0':
            await dev.turn_on()
            upadte_time_start_since()
            start_timer()
            
            data = await get_sensor_data() 
            if 'errorCode' not in data:
                if data['plugStatus'] == 'ON':
                    turn_on_led('blue')
                
                data['timerData'] = str(time_limit)
                data['action'] = '0'
                data['errorCode'] = '0'
                data['errorDescription'] = 'N/A'
                print(f'\naction 0 were achived, uploading to pubnub\n{data}\n')

                p = subprocess.Popen(['python', 'SEP728_Final_Project/main3.py'])

        elif data_received_from_pubnub['action'] == '1':
            await dev.turn_off()
            cancel_timer()

            data = await get_sensor_data()
            if 'errorCode' not in data:
                if data['plugStatus'] == 'OFF':
                    turn_on_led('green')
                
                data['timerData'] = 'false'
                data['action'] = '1'
                data['errorCode'] = '0'
                data['errorDescription'] = 'N/A'
                print(f'\naction 1 were achived, uploading to pubnub\n{data}\n')
        
        elif data_received_from_pubnub['action'] == '2': 
            data = await get_sensor_data()
            if 'errorCode' not in data:
                if data['plugStatus'] == 'OFF':
                    time_left = 'false'
                else:
                    time_elapsed = time.time() - time_start_since
                    time_left = str(time_limit - time_elapsed)

                data['timerData'] = str(time_left)
                data['action'] = '2'
                data['errorCode'] = '0'
                data['errorDescription'] = 'N/A'
                print(f'\naction 2 were achived, uploading to pubnub\n{data}\n')

        publish_to_pubnub(data)

    def message(self, pubnub, message):
        asyncio.run(self.handle_message(pubnub, message))

pubnub.add_listener(SubscribeHandler())


