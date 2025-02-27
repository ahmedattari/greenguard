import requests

def get_sensor_data():
    url = "http://172.20.10.2/sensors"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(data)
        return data
    except requests.RequestException as e:
        print(f"Error requesting sensor data: {e}")
        return None

if __name__ == "__main__":
    x = 'y'
    while x == 'y':
        sensor_data = get_sensor_data()
        if sensor_data:
            print("Sensor Data:")
            print(f"Temperature: {sensor_data['temperature']}°C")
            print(f"Humidity: {sensor_data['humidity']}%")
            print(f"Air Quality: {sensor_data['air_quality']}")
            print(f"Soil Moisture: {sensor_data['moisture']}%")
            print("Gas Concentrations:")
            for gas, (quality, concentration) in sensor_data['gas_concentrations'].items():
                print(f"- {gas}: {concentration} ppm ({quality})")

        x = input("Continue: n/y: ")