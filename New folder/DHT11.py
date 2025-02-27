import time
import machine
from dht import DHT11

# Define the pin where the DHT11 is connected
dht_pin = machine.Pin(4)

# Initialize the DHT11 sensor
dht_sensor = DHT11(dht_pin)

while True:
    try:
        # Measure the temperature and humidity
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Print the temperature and humidity values
        print("Temperature: {}°C".format(temperature))
        print("Humidity: {}%".format(humidity))

    except Exception as e:
        print("Error: {}".format(e))

    # Wait for 2 seconds before taking another measurement
    time.sleep(2)
