# Night Light

This is a night light that was programmed in micropython and used a Raspberry Pi Pico W with a Cytron daughterboard attachment.

The goals of the project were as follows:

1. Turn the nightlight on and off with MQTT commands
2. Program one of the blue LEDs to continually breathe (get brighter then dimmer then brighter)
3. Sound the buzzer and light the NeoPixel when Pin 20 is activated
4. Have Steps 1-3 running asynchronously
5. Use a separate button and LED from the ones built into the board
6. Fabricate a housing for the electrical hardware
7. Use UART or i2c communication to make the light touch-sensitive using an accelerometer
8. Control all steps from a cell phone using a PyScript page
