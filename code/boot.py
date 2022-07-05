import ujson
# boot.py -- run on boot-up


FIRST_LAUNCH = True

config = ujson.loads(open('config.json').read())

# Network set to station mode
print("Init network, loading...")
def setup_network():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return wlan

# Assign the network class to wlan
wlan = setup_network()

# Connecting to WiFi
def try_connect_wifi():
    # If WiFi is connected do nothing
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(config["SSID"], config["SSID_PASSWORD"])
        while not wlan.isconnected():
            pass
    # Only print network info at first boot
    if(FIRST_LAUNCH):
        print('network config:', wlan.ifconfig())

# Connect to WiFi
try_connect_wifi()


FIRST_LAUNCH = False
