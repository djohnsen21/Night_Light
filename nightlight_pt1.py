import machine
from machine import Pin, PWM
import time
import neopixel
import random
import network
import mqtt
from mqtt import MQTTClient
import uasyncio as asyncio  # Import asyncio for async functionality

# MQTT Settings
mqtt_broker = 'broker.hivemq.com'
topic_sub = 'ME35-24/group'
run_program = False  # Global variable to control the program state via MQTT

def callback(topic, msg):
    global run_program
    msg_decoded = msg.decode()

    if msg_decoded == 'on':
        run_program = True
        print("Program started via MQTT.")
    elif msg_decoded == 'off':
        run_program = False
        print("Program stopped via MQTT.")

# ---------------------------------Breathing LED-----------------------------
class Breathing:
    def __init__(self, pin_num):
        self.LED = PWM(Pin(pin_num))  # Can set the desired pin number later
        self.LED.freq(1000)  # Sets PWM frequency to 1000 Hz
    
    async def breathe(self):
        while True:
            if run_program:  # Check if the program should be running
                for i in range(0, 65535, 500):  # Increases brightness
                    self.LED.duty_u16(i)  # Adjusts brightness using PWM
                    await asyncio.sleep(0.01)  # Use asyncio sleep instead of time.sleep
                for i in range(65534, -1, -500):  # Decreases brightness
                    self.LED.duty_u16(i)  # Adjusts brightness using PWM
                    await asyncio.sleep(0.01)  # Use asyncio sleep instead of time.sleep
            else:
                await asyncio.sleep(0.1)  # When not running, just wait to prevent busy looping

# ---------------------------------Button, NeoPixel, and Buzzer-----------------------------
class Button:
    def __init__(self, button_pin, neo_pixel_pin, num_pixels):
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)  # Pull-down ensures button reads zero when not pushed
        self.neo = neopixel.NeoPixel(Pin(neo_pixel_pin), num_pixels)  # Argument from NeoPixel library
        self.buzzer = PWM(Pin(18, Pin.OUT))
        self.buzzer.freq(440)  # Sets frequency to 440 Hz (A4 note)
        self.buzzer.duty_u16(0)  # Starts with the buzzer off
        self.neo.fill((0, 0, 0))  # Turns off the NeoPixel initially
        self.neo.write()
        self.prev_button_state = 1  # Store previous state of the button (1 means not pressed)

    async def beep_and_light(self):
        while True:
            if run_program:  # Check if the program should be running
                current_button_state = self.button.value()  # Get current button state

                if current_button_state == 0 and self.prev_button_state == 1:  # Button pressed (transition from not pressed to pressed)
                    # Set a random color for the NeoPixel when the button is pressed
                    self.neo[0] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    self.neo.write()  # Update the NeoPixel color

                    # Turn on the buzzer
                    self.buzzer.duty_u16(1000)  # Turn on the buzzer (set duty cycle)

                if current_button_state == 1 and self.prev_button_state == 0:  # Button released (transition from pressed to not pressed)
                    # Turn off the NeoPixel
                    self.neo.fill((0, 0, 0))
                    self.neo.write()  # Update the NeoPixel to off

                    # Turn off the buzzer
                    self.buzzer.duty_u16(0)

                self.prev_button_state = current_button_state  # Update previous button state
            await asyncio.sleep(0.05)  # Small delay to prevent high CPU usage

# ---------------------------------MQTT Client-----------------------------
async def mqtt_client():
    client = MQTTClient('ME35_chris', mqtt_broker, 1883)
    client.set_callback(callback)
    client.connect()
    print('Connected to MQTT broker')
    client.subscribe(topic_sub.encode())

    while True:
        client.check_msg()  # Check for new messages
        await asyncio.sleep(0.1)

# ---------------------------------Main Program-----------------------------
async def main():
    led = Breathing(pin_num=0)  # Initializes breathing LED on pin 0
    button_neo = Button(button_pin=20, neo_pixel_pin=28, num_pixels=1)  # Button on pin 20, NeoPixel on pin 28
    
    # Create tasks to run breathing, button press handling, and MQTT client in parallel
    task1 = asyncio.create_task(led.breathe())  # Run the breathing effect
    task2 = asyncio.create_task(button_neo.beep_and_light())  # Handle button presses and control buzzer/light
    task3 = asyncio.create_task(mqtt_client())  # MQTT client task

    await asyncio.gather(task1, task2, task3)  # Run tasks concurrently

# Start the asyncio event loop
asyncio.run(main())
