import machine
import time
from dht import DHT11

# Define pin for the MQ135 sensor
MQ135_PIN = 34

# Define the pin where the DHT11 is connected
DHT_PIN = 4

Moisture_PIN = 26

# Initialize ADC for MQ135 sensor
mq135_sensor = machine.ADC(machine.Pin(MQ135_PIN))
mq135_sensor.atten(machine.ADC.ATTN_11DB)  # Configure for full range (0-3.3V)

# Initialize DHT11 sensor      
dht_sensor = DHT11(machine.Pin(DHT_PIN))

# Initialize ADC for Moisture sensor
moisture_adc = machine.ADC(machine.Pin(Moisture_PIN))
moisture_adc.width(machine.ADC.WIDTH_12BIT)
moisture_adc.atten(machine.ADC.ATTN_11DB)

# Thresholds and descriptions for air quality
air_quality_thresholds = {
    "clean": 1000,
    "medium": 2000,
    "polluted": 3000
}

# Thresholds for gas concentrations (Example values, adjust as per sensor calibration)
gas_thresholds = {
    "Ammonia": {"low": 150, "medium": 250, "high": 350},
    "Carbon Monoxide": {"low": 150, "medium": 250, "high": 350},
    "Nitrogen Dioxide": {"low": 0.1, "medium": 1, "high": 5},
    "Carbon Dioxide": {"high": 10000, "medium": 20000, "low": 30000}
}

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
        gas_concentration = raw_value * thresholds["high"] / 4095  # Scale the raw value

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

while True:
    try:
        # Read MQ135 data
        mq135_raw_value = mq135_sensor.read()
        air_quality_desc = interpret_air_quality(mq135_raw_value)

        # Read DHT11 data
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Read Moisture Sensor data
        moisture_raw_value = moisture_adc.read()
        moisture_percentage = (100 - ((moisture_raw_value/4095.00) * 100))

        # Print readings
        print("Air Quality (MQ135): {} ({})".format(mq135_raw_value, air_quality_desc))
        print("Temperature: {}°C".format(temperature))
        print("Humidity: {}%".format(humidity))
        print("Soil Moisture: {}%".format(moisture_percentage))

        # Print gas concentrations
        print("Gas Concentrations:")
        for gas_name, thresholds in gas_thresholds.items():
            gas_desc, gas_concentration = interpret_gas_concentration(gas_name, mq135_raw_value)
            if gas_concentration is not None:
                print("- {}: {} ppm ({})".format(gas_name, gas_concentration, gas_desc))
            else:
                print("- {}: Unknown".format(gas_name))

    except Exception as e:
        print("Error: ", e)

    # Delay for stability (adjust as needed)
    time.sleep(2)
    print("###############################################")
