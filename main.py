import machine
import utime
import network
import urequests as requests

from machine import I2C

from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd


# LCD Display Configuration
i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

I2C_ADDR = i2c.scan()    # Default 0x27, Sometimes can be othervalues
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

lcd = I2cLcd(i2c, I2C_ADDR[0], I2C_NUM_ROWS, I2C_NUM_COLS)


# Buzzer Configuration
buzzer_pin = machine.Pin(15, machine.Pin.OUT)


# Fire Sensor Configuration
adc_fire = machine.ADC(0)  # Assuming GPIO 26 for the analog input
dig_fire = machine.Pin(22, machine.Pin.IN)  # Assuming GPIO 22 for the digital input


# LED Configuration
red = machine.Pin(17, machine.Pin.OUT)
green = machine.Pin(16, machine.Pin.OUT)


# Wifi Configuration
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("NETWORK_NAME", "NETWORK_PASSWORD")
# wlan.connect("username", "password")    # Place your wifi/hotspot "username", "password"
utime.sleep(3)
print(wlan.isconnected())


# Push Bullet API Configuration
api_key = "API_KEY"
notification_title = "!!! Alert !!!"
notification_body = "Fire Alert"


def send_notification(api_key, title, body):
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {"Access-Token": api_key, "Content-Type": "application/json"}
    data = {"type": "note", "title": title, "body": body}

    response = requests.post(url, headers=headers, json=data)
    print(response.text)  # Print the response for debugging purposes


def activate_buzzer():
    buzzer_pin.value(1)


def deactivate_buzzer():
    buzzer_pin.value(0)


while True:
    adc_fire_value = adc_fire.read_u16()
    dig_fire_value = dig_fire.value()

    # Testing
    # adc_fire_value = 3000      # Fire
    # adc_fire_value = 300000    # No Fire

    print("ADC Fire:", adc_fire_value)
    print("Digital Fire:", dig_fire_value)

    if adc_fire_value > 30000:
        red.value(0)
        green.value(1)

        deactivate_buzzer()

        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("      Fire      ")
        lcd.move_to(0, 1)
        lcd.putstr("  Not Detected  ")

        # Notification Not Send

        utime.sleep(1)
    else:
        red.value(1)
        green.value(0)

        activate_buzzer()

        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("    ! Fire !    ")
        lcd.move_to(0, 1)
        lcd.putstr(" !! Detected !! ")

        # Notification Send
        send_notification(api_key, notification_title, notification_body)

        utime.sleep(3)
    
    print("==============================")

