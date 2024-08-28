from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

def geocode(address):
    api_key = 'AIzaSyA0VQ8tub7cX2tK3OtA0CcO6jGTcsr4ek4'  # Replace with your actual API key
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(endpoint)
    results = response.json().get('results')
    if results:
        location = results[0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None

def calculate_distance_and_duration(origin_lat, origin_lng, dest_lat, dest_lng):
    api_key = 'AIzaSyA0VQ8tub7cX2tK3OtA0CcO6jGTcsr4ek4'  # Replace with your actual API key
    endpoint = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_lat},{origin_lng}&destinations={dest_lat},{dest_lng}&key={api_key}"
    response = requests.get(endpoint)
    result = response.json()
    if result['rows']:
        elements = result['rows'][0]['elements'][0]
        if elements['status'] == 'OK':
            distance = elements['distance']['value'] / 1000  # in kilometers
            duration = elements['duration']['value'] / 60  # in minutes
            return distance, duration
    return None, None

def estimate_prices(distance):
    base_fare = 3.0  # Base fare in SGD
    per_km_rate = 0.5  # Rate per kilometer in SGD
    
    # Create a dictionary for different services with varied pricing
    prices = {
        'Grab': round(base_fare + per_km_rate * distance + random.uniform(0.0, 0.5), 2),
        'Gojek': round(base_fare + per_km_rate * distance + random.uniform(0.3, 0.8), 2),
        'TADA': round(base_fare + per_km_rate * distance + random.uniform(0.2, 0.4), 2),
        'Ryde': round(base_fare + per_km_rate * distance + random.uniform(0.1, 0.3), 2),
    }
    
    return prices

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    location = request.form['location']
    destination = request.form['destination']

    # Geocode the locations
    location_lat, location_lng = geocode(location)
    destination_lat, destination_lng = geocode(destination)

    if location_lat and location_lng and destination_lat and destination_lng:
        # Calculate distance and duration
        distance, duration = calculate_distance_and_duration(location_lat, location_lng, destination_lat, destination_lng)
        
        # Estimate prices based on distance
        prices = estimate_prices(distance)
        
        # Add random ETA for each service
        comparison_data = {service: {'price': price, 'eta': round(duration + random.uniform(-2, 2), 2)}
                           for service, price in prices.items()}
    else:
        comparison_data = {}

    return render_template('index.html', data=comparison_data, 
                           location_lat=location_lat, location_lng=location_lng, 
                           destination_lat=destination_lat, destination_lng=destination_lng,
                           location=location, destination=destination)

if __name__ == '__main__':
    app.run(debug=True)
