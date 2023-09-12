import RPi.GPIO as GPIO


def turn_off_led():
    red_pin = 38
    green_pin = 40
    blue_pin = 36
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup([red_pin, green_pin, blue_pin], GPIO.OUT)
    GPIO.cleanup()

def turn_on_led(color):
    red_pin = 38
    green_pin = 40
    blue_pin = 36
    if color == 'red':
        color = red_pin 
    elif color == 'green':
        color = green_pin
    elif color == 'blue':
        color = blue_pin
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup([red_pin, green_pin, blue_pin], GPIO.OUT)
    GPIO.output([red_pin, green_pin, blue_pin], GPIO.LOW)
    GPIO.output(color, GPIO.HIGH)

# turn_off_led()