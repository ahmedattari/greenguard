import machine
import time

# Define pin for the MQ135 sensor
MQ135_PIN = 34

# Initialize MQ135 sensor (Analog pin)
mq135_sensor = machine.ADC(machine.Pin(MQ135_PIN))
mq135_sensor.atten(machine.ADC.ATTN_11DB)  # Configure for full range (0-3.3V)

# Thresholds and descriptions for air quality
air_quality_thresholds = {
    "clean": 1000,
    "medium": 2000,
    "polluted": 3000
}

# Thresholds for gas concentrations (These are example values and need proper calibration)
gas_thresholds = {
    "Ammonia": {"low": 150, "medium": 250, "high": 350},
    "Carbon Monoxide": {"low": 150, "medium": 250, "high": 350},
    "Nitrogen Dioxide": {"low": 0.1, "medium": 1, "high": 5},
    "Carbon Dioxide": {"high": 10000, "medium": 20000, "low": 30000}  # Adjusted for high and low logic
}

#def interpret_air_quality(air_quality):
#    for desc, threshold in air_quality_thresholds.items():
#        if air_quality < threshold:
#            print("Name: ", desc)
#            return desc
#    return "unknown"

def interpret_air_quality(air_quality):
    if air_quality < 1000:
        return "Polluted"
    elif air_quality < 2000 and air_quality > 1000:
        return "Medium"
    elif air_quality > 2000:
        return "Clean"
    

def interpret_gas_concentration(gas_name, raw_value):
    thresholds = gas_thresholds.get(gas_name)
    if thresholds:
        gas_concentration = raw_value * thresholds["high"] / 4095  # Scale the raw value

        # Adjust logic specifically for Carbon Dioxide
        if gas_name == "Carbon Dioxide":
            # Reverse the logic: label as "high" when gas_concentration is below "low"
            if gas_concentration < 2500:
                return "high", gas_concentration
            elif 2500 <= gas_concentration < 4000:
                return "medium", gas_concentration
            else:
                return "low", gas_concentration
        else:
            # Normal logic for other gases
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
        raw_value = mq135_sensor.read()
        air_quality_desc = interpret_air_quality(raw_value)

        # Print air quality reading
        print("Air Quality (MQ135): {} ({})".format(raw_value, air_quality_desc))

        # Print gas concentrations
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
    time.sleep(2)
    print("###############################################")

