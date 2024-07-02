import os
import random
import uuid
import requests
from confluent_kafka import SerializingProducer
import simplejson as json
from datetime import datetime, timedelta

LONDON_COORDINATES = {"latitude": 51.5074, "longitude": -0.1278}
BIRMINGHAM_COORDINATES = {"latitude": 52.4862, "longitude": -1.8904}

# Calculate movement increments
LATITUDE_INCREMENTS = (BIRMINGHAM_COORDINATES["latitude"] - LONDON_COORDINATES["latitude"]) / 100
LONGITUDE_INCREMENTS = (BIRMINGHAM_COORDINATES["longitude"] - LONDON_COORDINATES["longitude"]) / 100

# Environment variables for configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
VEHICLE_TOPIC = os.getenv("VEHICLE_TOPIC", "vehicle_data")
GPS_TOPIC = os.getenv("GPS_TOPIC", "gps_data")
TRAFFIC_TOPIC = os.getenv("TRAFFIC_TOPIC", "traffic_data")
WEATHER_TOPIC = os.getenv("WEATHER_TOPIC", "weather_data")
EMERGENCY_TOPIC = os.getenv("EMERGENCY_TOPIC", "emergency_data")

random.seed(42)
start_time = datetime.now()  # Driver starting time
start_location = LONDON_COORDINATES.copy()

def get_next_time():
    global start_time
    start_time += timedelta(seconds= random.randint(30,60)) # updating frequency
    return start_time

def simulate_vehicle_movement():
    global start_location
    # move towards birmingham
    start_location["latitude"] += LATITUDE_INCREMENTS
    start_location["longitude"] += LONGITUDE_INCREMENTS

    # Add some randomness to simulate actual road travel
    start_location["latitude"] += random.uniform(-0.0005, 0.0005)
    start_location["longitude"] += random.uniform(-0.0005, 0.0005)

    return start_location

def generate_vehicle_data(device_id):
    location = simulate_vehicle_movement()
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'timestamp': get_next_time().isoformat(),
        'location': location,
        'speed': random.uniform(20,45),
        'direction':'North-East',
        "make": "Tesla",
        "model": "S Model",
        "year": 2024,
        "fuelType": "Electric"
    }

def generate_gps_data(device_id, timestamp, vehicle_type="private"):
    return {
        "id": uuid.uuid4(),
        "deviceId": device_id,
        "timestamp": timestamp,
        "speed": random.uniform(0, 40),  # km/h
        "direction": "North-East",
        "vehicle_type": vehicle_type
    }

def generate_traffic_camera_data(device_id, timestamp, location):

    google_api_key = 'AIzaSyDDD-M6Di-XcsJ6ZdjpyiTkVDlM9ojqaLo'  # Replace with your actual Google API key

    # Construct the URL for the Street View API
    street_view_url = (
        f"https://maps.googleapis.com/maps/api/streetview"
        f"?size=600x300&location={location['latitude']},{location['longitude']}"
        f"&key={google_api_key}"
    )
    try:
        # Make the request to the Google Street View API
        response = requests.get(street_view_url)

        if response.status_code == 200:
            snapshot = response.url  # The URL of the image
        else:
            snapshot = None
    except Exception as e:
        print(f"Error occurred while fetching traffic snapshot: {e}")
        snapshot = None

    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'timestamp': timestamp,
        'location': location,
        'trafficFlow': random.choice(['Smooth', 'Moderate', 'Heavy']),
        'snapshot': snapshot
    }

def generate_weather_data(device_id, timestamp, location):
    api_key = 'cb9a057593337063764f48842b88ed56'  # Replace with your OpenWeatherMap API key
    base_url = 'http://api.openweathermap.org/data/2.5/weather?'

    try:
        # Ensure location is formatted correctly
        complete_url = f"{base_url}lat={location['latitude']}&lon={location['longitude']}&appid={api_key}&units=metric"
        #print(f"Complete URL: {complete_url}")

        # Make the request
        response = requests.get(complete_url)
        #print(f"Response: {response.text}")

        # Parse the response
        data = response.json()
        #print(f"Response JSON: {data}")

        if data['cod'] != '404':
            main = data['main']
            wind = data['wind']
            weather = data['weather'][0]
            temperature = main['temp']
            humidity = main['humidity']
            weather_condition = weather['main']
            wind_speed = wind['speed']
            precipitation = data.get('rain', {}).get('1h', 0)  # Rainfall in last 1 hour
            air_quality = random.uniform(0, 500)  # Placeholder as OpenWeatherMap doesn't provide air quality

            return {
                'id': uuid.uuid4(),
                'deviceId': device_id,
                'location': location,
                'timestamp': timestamp,
                'temperature': temperature,
                'weatherCondition': weather_condition,
                'precipitation': precipitation,
                'windSpeed': wind_speed,
                'humidity': humidity,
                'airQuality': air_quality
            }
        else:
            print('City not found.')
            return None
    except Exception as e:
        print(f"Unexpected Error occurred: {e}")
        return None

def simulate_journey(producer, device_id):
    while True:
        vehicle_data= generate_vehicle_data(device_id)
        gps_data = generate_gps_data(device_id, vehicle_data['timestamp'])
        traffic_data = generate_traffic_camera_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])
        weather_data = generate_weather_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])
        print(traffic_data)
        break

if __name__ == "__main__":
    producer_config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "error_cb": lambda err: print(f"kafka error: {err}")
    }  # Kafka broker information
    producer = SerializingProducer(producer_config)

    try:
        simulate_journey(producer, "Vehicle-ron")

    except KeyboardInterrupt:
        print('Simulation ended by user')
    except Exception as e:
        print(f"Unexpected Error occurred: {e}")
