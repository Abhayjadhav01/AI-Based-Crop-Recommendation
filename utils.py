import requests
import json
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import config

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_weather_data(latitude, longitude, api_key):
    """Fetch real weather data from OpenWeatherMap API."""
    if not api_key:
        st.warning("OpenWeather API key not provided. Using mock data.")
        return config.DEFAULT_PARAMS['temperature'], config.DEFAULT_PARAMS['humidity'], config.DEFAULT_PARAMS['rainfall']

    try:
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': api_key,
            'units': 'metric'
        }
        response = requests.get(config.OPENWEATHER_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            rainfall = data.get('rain', {}).get('1h', 0)  # Rainfall in last hour, default 0
            return temperature, humidity, rainfall
        else:
            st.error(f"OpenWeather API error: {response.status_code}")
            return None, None, None
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None, None, None

@st.cache_data(ttl=3600)
def reverse_geocode(latitude, longitude):
    """Reverse geocode to get address."""
    try:
        geolocator = Nominatim(user_agent="crop_recommender", timeout=10)
        location = geolocator.reverse((latitude, longitude), language='en')
        return location.address if location else "Address not found"
    except Exception as e:
        st.error(f"Error in reverse geocoding: {e}")
        return "Address not found"

@st.cache_data(ttl=3600)
def get_nearby_landmarks(latitude, longitude):
    """Get nearby landmarks."""
    try:
        geolocator = Nominatim(user_agent="crop_recommender", timeout=10)
        viewbox_str = f"{longitude-0.02},{latitude-0.02},{longitude+0.02},{latitude+0.02}"
        landmarks = geolocator.geocode(
            query="landmark",
            exactly_one=False,
            limit=5,
            viewbox=viewbox_str,
            bounded=True,
            language='en'
        )
        if landmarks:
            result = []
            for lm in landmarks:
                dist = geodesic((latitude, longitude), (lm.latitude, lm.longitude)).meters
                result.append((lm.address, dist))
            return result
        return []
    except Exception as e:
        st.error(f"Error fetching landmarks: {e}")
        return []

def validate_inputs(N, P, K, temp, hum, ph, rain):
    """Validate input parameters."""
    errors = []
    if not (0 <= N <= 200): errors.append("Nitrogen should be between 0-200 kg/ha")
    if not (0 <= P <= 150): errors.append("Phosphorus should be between 0-150 kg/ha")
    if not (0 <= K <= 200): errors.append("Potassium should be between 0-200 kg/ha")
    if not (-50 <= temp <= 60): errors.append("Temperature should be between -50-60°C")
    if not (0 <= hum <= 100): errors.append("Humidity should be between 0-100%")
    if not (0 <= ph <= 14): errors.append("pH should be between 0-14")
    if not (0 <= rain <= 1000): errors.append("Rainfall should be between 0-1000 mm")
    return errors

def call_gemini_api(prompt, api_key):
    """Call Gemini API for AI recommendations."""
    if not api_key:
        return None
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(config.GEMINI_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            st.warning(f"Gemini API error: {response.text}")
            return None
    except Exception as e:
        st.warning(f"Error contacting Gemini API: {e}")
        return None

def call_gemini_disease_solution(disease, confidence, location=None, api_key=None):
    """Generate AI-based disease solution using Gemini API."""
    if not api_key:
        return None
    prompt = f"Provide a detailed solution for the plant disease '{disease}' detected with {confidence:.2f}% confidence."
    if location:
        prompt += f" Consider the location: {location}."
    prompt += " Include preventive measures, treatment steps, and any additional advice."
    return call_gemini_api(prompt, api_key)
