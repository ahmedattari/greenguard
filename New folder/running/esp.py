import ujson
import network
import socket
from machine import Pin, ADC
import dht
import time
import machine
# Define pin for the MQ135 sensor
MQ135_PIN = 34

# Define the pin where the DHT11 is connected
DHT_PIN = 4

Moisture_PIN = 26

# Initialize ADC for MQ135 sensor
mq135_sensor = machine.ADC(machine.Pin(MQ135_PIN))
mq135_sensor.atten(machine.ADC.ATTN_11DB)  # Configure for full range (0-3.3V)

# Initialize DHT11 sensor      
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))

# Initialize ADC for Moisture sensor
moisture_adc = machine.ADC(machine.Pin(Moisture_PIN))
moisture_adc.width(machine.ADC.WIDTH_12BIT)
moisture_adc.atten(machine.ADC.ATTN_11DB)

# Thresholds for gas concentrations
gas_thresholds = {
    "Ammonia": {"low": 150, "medium": 250, "high": 350},
    "Carbon Monoxide": {"low": 150, "medium": 250, "high": 350},
    "Nitrogen Dioxide": {"low": 0.1, "medium": 1, "high": 5},
    "Carbon Dioxide": {"high": 10000, "medium": 20000, "low": 30000}
}

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        pass
    
    print('Connection successful')
    print('IP Address:', wlan.ifconfig()[0])

def read_dht11():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temperature, humidity
    except Exception as e:
        print(f"Error reading DHT11: {e}")
        return None, None

def read_mq135():
    try:
        mq135_raw_value = mq135_sensor.read()
        air_quality = interpret_air_quality(mq135_raw_value)
        return mq135_raw_value, air_quality
    except Exception as e:
        print(f"Error reading MQ135: {e}")
        return None, None

def read_moisture():
    try:
        moisture_raw_value = moisture_adc.read()
        moisture_percentage = (100 - ((moisture_raw_value/4095.00) * 100))
        return moisture_percentage
    except Exception as e:
        print(f"Error reading moisture sensor: {e}")
        return 50

def interpret_air_quality(air_quality):
    if air_quality < 1000:
        return "Polluted"
    elif air_quality < 2000:
        return "Medium"
    else:
        return "Clean"

def interpret_gas_concentration(gas_name, raw_value):
    thresholds = gas_thresholds.get(gas_name)
    if thresholds:
        gas_concentration = raw_value * thresholds["high"] / 4095
        if gas_name == "Carbon Dioxide":
            if gas_concentration < 2500:
                return "high", gas_concentration
            elif 2500 <= gas_concentration < 4000:
                return "medium", gas_concentration
            else:
                return "low", gas_concentration
        else:
            if gas_concentration < thresholds["low"]:
                return "low", gas_concentration
            elif thresholds["low"] <= gas_concentration < thresholds["medium"]:
                return "medium", gas_concentration
            else:
                return "high", gas_concentration
    else:
        return "unknown", None

def handle_request(request):
    try:
        request_line = request.split('\r\n')[0]
        method, path, _ = request_line.split()
        
        if method == 'GET' and path == '/sensors':
            time.sleep(5)
            mq135_raw_value, air_quality = read_mq135()
            time.sleep(5)
            temperature, humidity = read_dht11()
            time.sleep(5)
            moisture_percentage = read_moisture()
            
            print("############################")
            print("air_quality", air_quality)
            print("temperature", temperature)
            print("humidity", humidity)
            print("moisture_percentage", moisture_percentage)
            if temperature is None or humidity is None or mq135_raw_value is None or moisture_percentage is None:
                raise ValueError("Error reading sensors")
            
            sensor_data = {
                "temperature": temperature,
                "humidity": humidity,
                "air_quality": air_quality,
                "moisture": moisture_percentage,
                "gas_concentrations": {
                    gas: interpret_gas_concentration(gas, mq135_raw_value) for gas in gas_thresholds
                }
            }
            return 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n' + ujson.dumps(sensor_data)
        
        else:
            return 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>'
    
    except Exception as e:
        print(f"Error handling request: {e}")
        return f'HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n{{"status":"error", "message":"{str(e)}"}}'

# Main function to set up the web server
ssid = 'Home'         # Replace with your Wi-Fi SSID
password = 'home1234'  # Replace with your Wi-Fi password
connect_wifi(ssid, password)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    
    request = cl.recv(1024).decode()
    response = handle_request(request)
    
    cl.send(response)
    cl.close()

