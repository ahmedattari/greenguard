import machine
import time

# Define the pin where the moisture sensor is connected
Moisture_PIN = 26

# Initialize ADC for the moisture sensor
moisture_adc = machine.ADC(machine.Pin(Moisture_PIN))
moisture_adc.width(machine.ADC.WIDTH_12BIT)
moisture_adc.atten(machine.ADC.ATTN_11DB)

while True:
    try:
        # Read Moisture Sensor data
        moisture_raw_value = moisture_adc.read()
        moisture_percentage = (100 - ((moisture_raw_value / 4095.00) * 100))
        
        # Print the moisture sensor value
        print("Moisture Sensor Raw Value: {}".format(moisture_raw_value))
        print("Soil Moisture: {}%".format(moisture_percentage))
        
    except Exception as e:
        print(f"Error reading moisture sensor: {e}")

    # Delay for stability (adjust as needed)
    time.sleep(2)

