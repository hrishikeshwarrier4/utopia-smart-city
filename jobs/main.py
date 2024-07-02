import os
import random
import uuid

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
        'location': (location['latitude'],location['longitude']),
        'speed': random.uniform(20,45),
        'direction':'North-East',
        'make':'Tesla',
        'model':'Model S',
        'year': 2024,
        'fuelType':'Electric'
    }


def generate_gps_data(device_id, timestamp, vehicle_type = 'private'):
    return {
        'id': uuid.uuid4(),

    }

def simulate_journey(producer, device_id):
    while True:
        vehicle_data= generate_vehicle_data(device_id)
        gps_data = generate_gps_data(device_id, vehicle_data['timestamp '])
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
