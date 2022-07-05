# main.py -- put your code here!
import dht
import machine
import micropython
import uasyncio
from machine import Pin, SPI
from libs.ST7735 import TFT
from libs.sysfont import sysfont
from libs.seriffont import seriffont
from libs.terminalfont import terminalfont
from boot import config, try_connect_wifi
from umqtt.robust import MQTTClient

# Temperature sensor init
print("Init temperature sensor")
dht22 = dht.DHT22(machine.Pin(22))

# LCD init stuff
def init_lcd():
    print("Init LCD; wait.")
    spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23))
    tft=TFT(spi,2,4,5)
    tft.initr()
    tft.rgb(True)
    # Fill display with black
    tft.fill(TFT.BLACK)
    print("Init LCD done")
    return tft

tft = init_lcd()

topic_pub = 'devices/envbox/'
topic_sub = 'devices/envbox/fan/status'
# Envbox as MD5 hash, this board does not support MD5 library.
client_name = "2f380147f1ed8b2a2735b55becaad4bb"

class Application():

    def __init__(self, temperature, humidity):
        self.mqtt = MQTTClient(client_name,config['broker_url'],user=config['user_mqtt'],password=config['pass_mqtt'], keepalive=240)
        self.temperature = temperature
        self.humidity = humidity
        self.counter = 1
        self.failure = 0
        self.fan = False

    def sub_cb(self, topic, msg):
        print((topic, msg))
        try:
            state = msg.decode("utf-8")
            if(state == "0"):
                if(self.fan == False):
                    print("Received same state (false), skipping update.")
                    return
                self.fan = False
                print(f"Received fan state, {self.fan}")
                self.draw_current_status()
            elif(state == "1"):
                if(self.fan == True):
                    print("Received same state (true), skipping update.")
                    return
                self.fan = True
                print(f"Received fan state, {self.fan}")
                self.draw_current_status()
            else:
                print(f"Invalid parsing, fan state skipping. {state}")
        except Exception as e:
            print("Invalid MQTT input, ignoring.", e)

    """
    This runs every 5 seconds.
    """
    async def measure_temp(self):
        while True:
            dht22.measure()
            self.temperature = dht22.temperature()
            self.humidity = dht22.humidity()
            print("Temperature is {temperature}°C, Humidity is {humidity}%".format(temperature=self.temperature, humidity=self.humidity))

            self.failure = 0
            # Send to MQTT.
            try:
                self.mqtt.publish(topic_pub, f"{self.temperature},{self.humidity}")
                print("Sent data to MQTT")
            except Exception as e:
                print("Failed to send to MQTT", e)
                if(self.failure > 1):
                    machine.reset()

                # MQTT failed so restart
                machine.reset()
            self.draw_current_status()
            await uasyncio.sleep_ms(60_000)

    # Used to change temperature color on display
    def get_color(self):
        color = TFT.GREEN
        if(self.temperature >= 28.0):
            color = TFT.RED
        elif(self.temperature >= 27.0):
            color = TFT.YELLOW
        return color

    def draw_current_status(self):
        tft.fill(TFT.BLACK);
        v = 0
        tft.text((0, v), "Envbox", TFT.RED, seriffont, 2, nowrap=True)
        v += sysfont["Height"] * 3
        tft.text((0, v), f"Fan Status", TFT.YELLOW, sysfont, 2, nowrap=False)
        v += sysfont["Height"] * 2
        tft.text((0, v), f"{'On' if self.fan else 'Off'}", TFT.GREEN if self.fan else TFT.RED, terminalfont, 2, nowrap=False)
        v += sysfont["Height"] * 3
        tft.text((0, v), f"Temperature", TFT.GREEN, sysfont, 2, nowrap=False)
        v += sysfont["Height"] * 3
        tft.text((0, v), f"{self.temperature}c", self.get_color(), terminalfont, 2, nowrap=False)
        v += sysfont["Height"] * 3
        tft.text((0, v), f"Humidity", TFT.BLUE, sysfont, 2, nowrap=False)
        v += sysfont["Height"] * 3
        tft.text((0, v), f"{self.humidity}%", TFT.BLUE, terminalfont, 2, nowrap=False)
        self.counter = self.counter + 1
        print("Drawing current values to screen.")

    async def start_main_loop(self):
        # measures temp and draws status
        uasyncio.create_task(self.measure_temp())

        self.draw_current_status()
        self.mqtt.DEBUG = True
        self.mqtt.set_callback(self.sub_cb)
        self.mqtt.connect()
        self.mqtt.subscribe(topic_sub)

        while True:
            # Lightweight call check if wifi is off
            try_connect_wifi()
            # Draw the display again.
            try:
                self.mqtt.check_msg()
            except Exception as e:
                if(self.failure > 1):
                    machine.reset()
            await uasyncio.sleep_ms(500)

async def main():
    dht22.measure()
    temperature = dht22.temperature()
    humidity = dht22.humidity()
    application = Application(temperature, humidity)
    await application.start_main_loop()

uasyncio.run(main())
