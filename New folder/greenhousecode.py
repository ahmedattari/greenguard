import dht
import machine
import time

# Define pins for the sensors
DHT_PIN = 26
MQ135_PIN = 34
MOISTURE_SENSOR_PIN = 32

# Initialize DHT11 sensor
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))

# Initialize MQ135 sensor (Analog pin)
mq135_sensor = machine.ADC(machine.Pin(MQ135_PIN))
mq135_sensor.atten(machine.ADC.ATTN_11DB)  # Configure for full range (0-3.3V)

# Initialize Moisture sensor (Analog pin)
moisture_sensor = machine.ADC(machine.Pin(MOISTURE_SENSOR_PIN))
moisture_sensor.atten(machine.ADC.ATTN_11DB)  # Configure for full range (0-3.3V)

# Thresholds and descriptions for air quality
air_quality_thresholds = {
    "clean": 1000,
    "medium": 2000,
    "polluted": 3000
}

# Thresholds for gas concentrations
gas_thresholds = {
    "Ammonia": {"low": 200, "medium": 400, "high": 600},
    "Benzene": {"low": 400, "medium": 800, "high": 1200},
    "Carbon Monoxide": {"low": 300, "medium": 600, "high": 900},
    "Nitrogen Dioxide": {"low": 500, "medium": 1000, "high": 1500},
    "Smoke": {"low": 1000, "medium": 2000, "high": 3000},
    "Carbon Dioxide": {"low": 1000, "medium": 2000, "high": 3000},
    "Alcohol": {"low": 1000, "medium": 2000, "high": 3000}
}

def read_dht_data():
    try:
        # Trigger a measurement
        dht_sensor.measure()
        
        # Read temperature and humidity
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        return temperature, humidity
    except Exception as e:
        print("Error reading DHT11 sensor: ", e)
        return None, None

def interpret_air_quality(air_quality):
    for desc, threshold in air_quality_thresholds.items():
        if air_quality < threshold:
            return desc
    return "unknown"

def interpret_gas_concentration(gas_name, raw_value):
    thresholds = gas_thresholds.get(gas_name)
    if thresholds:
        gas_concentration = raw_value * thresholds["high"] / 4095  # Scale the raw value
        if gas_concentration < thresholds["low"]:
            return "low", gas_concentration
        elif thresholds["low"] <= gas_concentration < thresholds["medium"]:
            return "medium", gas_concentration
        else:
            return "high", gas_concentration
    else:
        return "unknown", None

while True:
    try:
        # Read DHT11 data
        temperature, humidity = read_dht_data()
        
        # Read MQ135 data
        raw_value = mq135_sensor.read()
        air_quality_desc = interpret_air_quality(raw_value)
        
        # Read moisture sensor data
        moisture_level = moisture_sensor.read()

        # Print sensor readings with descriptions
        print("Temperature: {}°C".format(temperature))
        print("Humidity: {}%".format(humidity))
        print("Air Quality (MQ135): {} ({})".format(raw_value, air_quality_desc))
        print("Soil Moisture Level: {}".format(moisture_level))
        print("Gas Concentrations:")
        for gas_name, thresholds in gas_thresholds.items():
            gas_desc, gas_concentration = interpret_gas_concentration(gas_name, raw_value)
            if gas_concentration is not None:
                print("- {}: {} ppm ({})".format(gas_name, gas_concentration, gas_desc))
            else:
                print("- {}: Unknown".format(gas_name))
        
    except Exception as e:
        print("Error: ", e)
    
    # Wait for 10 seconds before the next reading
    time.sleep(10)
