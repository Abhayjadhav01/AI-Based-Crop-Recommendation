import streamlit as st
import pandas as pd
from PIL import Image
import config
import utils
import model
from model import get_top_crops

def manual_input():
    """Get manual input parameters from user."""
    st.header("Manual Parameter Input")
    with st.form("manual_input_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            N = st.number_input("Nitrogen (N) content in soil (kg/ha)", value=config.DEFAULT_PARAMS['N'], key='N_manual')
            P = st.number_input("Phosphorus (P) content in soil (kg/ha)", value=config.DEFAULT_PARAMS['P'], key='P_manual')
            K = st.number_input("Potassium (K) content in soil (kg/ha)", value=config.DEFAULT_PARAMS['K'], key='K_manual')
        with col2:
            temp = st.number_input(r"Temperature ($^\circ$C)", value=config.DEFAULT_PARAMS['temperature'], key='temp_manual')
            hum = st.number_input("Humidity (%)", value=config.DEFAULT_PARAMS['humidity'], key='hum_manual')
        with col3:
            ph = st.number_input("pH value of the soil", value=config.DEFAULT_PARAMS['ph'], key='ph_manual')
            rain = st.number_input("Rainfall (mm)", value=config.DEFAULT_PARAMS['rainfall'], key='rain_manual')

        submitted = st.form_submit_button("Submit Parameters")

    if not submitted:
        return False

    # Validate inputs
    errors = utils.validate_inputs(N, P, K, temp, hum, ph, rain)
    if errors:
        for error in errors:
            st.error(error)
        return False

    st.session_state.N = N
    st.session_state.P = P
    st.session_state.K = K
    st.session_state.temp = temp
    st.session_state.hum = hum
    st.session_state.ph = ph
    st.session_state.rain = rain
    return True

def fetch_data():
    """Fetch soil and weather data based on user location input."""
    import folium
    from streamlit_folium import st_folium
    from folium import plugins

    st.header("Automatic Parameter Fetching with Google Maps")
    st.markdown(
        """
        Use the map below to select your farm's real-time location. The system will retrieve coordinates, address, and nearby landmarks.
        """
    )

    # Initialize session state for map selection
    if 'selected_lat' not in st.session_state:
        st.session_state.selected_lat = None
    if 'selected_lng' not in st.session_state:
        st.session_state.selected_lng = None

    # Default location
    default_location = config.DEFAULT_LOCATION
    st.info("Click on the map to select your farm location.")

    # Build map
    map_center = [st.session_state.selected_lat, st.session_state.selected_lng] if st.session_state.selected_lat and st.session_state.selected_lng else default_location
    google_maps_api_key = st.text_input("Enter your Google Maps API Key for a realistic map:", type="password", key="google_key")
    zoom_level = config.ZOOM_SELECTED if st.session_state.selected_lat and st.session_state.selected_lng else config.ZOOM_DEFAULT

    if google_maps_api_key:
        google_tiles = f"https://mt1.google.com/vt/lyrs=r&x={{x}}&y={{y}}&z={{z}}&key={google_maps_api_key}"
        m = folium.Map(
            location=map_center,
            zoom_start=zoom_level,
            tiles=None,
            attr='',
            control_scale=True,
            zoom_control=True,
            prefer_canvas=True,
            show=False
        )
        folium.TileLayer(
            tiles=google_tiles,
            attr='Google',
            name='Google Maps',
            overlay=False,
            control=False
        ).add_to(m)
    else:
        m = folium.Map(
            location=map_center,
            zoom_start=zoom_level,
            tiles='OpenStreetMap',
            attr='',
            control_scale=True,
            zoom_control=True,
            prefer_canvas=True,
            show=False
        )

    # Add marker if selected
    if st.session_state.selected_lat and st.session_state.selected_lng:
        folium.Marker(
            location=[st.session_state.selected_lat, st.session_state.selected_lng],
            popup="Selected Location",
            icon=folium.Icon(color='red', icon='glyphicon glyphicon-map-marker', prefix='glyphicon')
        ).add_to(m)

    # Add fullscreen
    plugins.Fullscreen().add_to(m)
    m.get_root().html.add_child(folium.Element('<style>.leaflet-control-attribution {display: none !important;}</style>'))

    # Render map
    map_data = st_folium(m, width=config.MAP_WIDTH, height=config.MAP_HEIGHT, returned_objects=["last_clicked"])

    # Update session state if clicked
    if map_data and map_data.get("last_clicked"):
        st.session_state.selected_lat = map_data["last_clicked"]["lat"]
        st.session_state.selected_lng = map_data["last_clicked"]["lng"]

    # If location selected, show info and fetch data
    if st.session_state.selected_lat and st.session_state.selected_lng:
        latitude = st.session_state.selected_lat
        longitude = st.session_state.selected_lng
        st.success(f"Selected Location: Latitude {latitude:.5f}, Longitude {longitude:.5f}")

        # Reverse geocode
        address = utils.reverse_geocode(latitude, longitude)
        st.write(f"**Address:** {address}")

        # Nearby landmarks
        landmarks = utils.get_nearby_landmarks(latitude, longitude)
        if landmarks:
            st.write("**Nearby Landmarks:**")
            for addr, dist in landmarks:
                st.write(f"- {addr} ({dist:.0f} meters away)")
        else:
            st.write("No major landmarks found nearby.")

        # API Key input
        try:
            openweather_key = st.secrets["OPENWEATHER_API_KEY"]
        except:
            openweather_key = st.text_input("Enter OpenWeather API Key:", type="password", key="weather_key")

        # Fetch data button
        if st.button("Fetch Data for This Location"):
            with st.spinner("Fetching data..."):
                temp, hum, rain = utils.get_weather_data(latitude, longitude, openweather_key)
                if temp is not None:
                    st.session_state.N = config.DEFAULT_PARAMS['N']  # Mock soil data, could integrate real API
                    st.session_state.P = config.DEFAULT_PARAMS['P']
                    st.session_state.K = config.DEFAULT_PARAMS['K']
                    st.session_state.ph = config.DEFAULT_PARAMS['ph']
                    st.session_state.temp = temp
                    st.session_state.hum = hum
                    st.session_state.rain = rain
                    st.session_state.latitude = latitude
                    st.session_state.longitude = longitude
                    st.session_state.address = address
                    st.success("Data fetched successfully!")
                else:
                    st.warning("Could not fetch data. Please try again.")
    else:
        st.info("No location selected yet.")

def display_parameters():
    """Display current input parameters with visualization."""
    import plotly.express as px

    N = st.session_state.get('N', config.DEFAULT_PARAMS['N'])
    P = st.session_state.get('P', config.DEFAULT_PARAMS['P'])
    K = st.session_state.get('K', config.DEFAULT_PARAMS['K'])
    temp = st.session_state.get('temp', config.DEFAULT_PARAMS['temperature'])
    hum = st.session_state.get('hum', config.DEFAULT_PARAMS['humidity'])
    ph = st.session_state.get('ph', config.DEFAULT_PARAMS['ph'])
    rain = st.session_state.get('rain', config.DEFAULT_PARAMS['rainfall'])
    latitude = st.session_state.get('latitude', None)
    longitude = st.session_state.get('longitude', None)
    address = st.session_state.get('address', None)

    st.markdown("### Current Parameters")
    param_col1, param_col2, param_col3, param_col4, param_col5, param_col6, param_col7 = st.columns(7)
    param_col1.metric("N", f"{N:.2f}")
    param_col2.metric("P", f"{P:.2f}")
    param_col3.metric("K", f"{K:.2f}")
    param_col4.metric("Temp", f"{temp:.2f} °C")
    param_col5.metric("Humidity", f"{hum:.2f} %")
    param_col6.metric("pH", f"{ph:.2f}")
    param_col7.metric("Rainfall", f"{rain:.2f} mm")

    if latitude and longitude:
        st.markdown(f"**Location:** {latitude:.5f}, {longitude:.5f}")
    if address:
        st.markdown(f"**Address:** {address}")

    # Visualization
    params = ['N', 'P', 'K', 'Temp', 'Humidity', 'pH', 'Rainfall']
    values = [N, P, K, temp, hum, ph, rain]
    fig = px.bar(x=params, y=values, title="Parameter Values", labels={'x': 'Parameter', 'y': 'Value'})
    st.plotly_chart(fig, use_container_width=True)

def recommend_crops(model):
    """Recommend crops with visualization."""
    import plotly.express as px

    N = st.session_state.get('N', config.DEFAULT_PARAMS['N'])
    P = st.session_state.get('P', config.DEFAULT_PARAMS['P'])
    K = st.session_state.get('K', config.DEFAULT_PARAMS['K'])
    temp = st.session_state.get('temp', config.DEFAULT_PARAMS['temperature'])
    hum = st.session_state.get('hum', config.DEFAULT_PARAMS['humidity'])
    ph = st.session_state.get('ph', config.DEFAULT_PARAMS['ph'])
    rain = st.session_state.get('rain', config.DEFAULT_PARAMS['rainfall'])

    input_data = pd.DataFrame([[N, P, K, temp, hum, ph, rain]], columns=config.FEATURES)

    # Get top crops
    top_crops = get_top_crops(model, input_data)

    # Display top crops
    st.markdown("### Top Crop Recommendations")
    for i, (crop, prob) in enumerate(top_crops, 1):
        st.write(f"{i}. {crop} ({prob:.2f}%)")

    # Visualization
    crops = [crop for crop, _ in top_crops]
    probs = [prob for _, prob in top_crops]
    fig = px.pie(values=probs, names=crops, title="Crop Recommendation Probabilities")
    st.plotly_chart(fig, use_container_width=True)

    # Gemini AI recommendation
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
    except:
        gemini_key = st.text_input("Enter Gemini API Key for AI recommendation:", type="password", key="gemini_key")

    if gemini_key:
        prompt = (
            f"Given: N={N}, P={P}, K={K}, Temp={temp}, Humidity={hum}, pH={ph}, Rainfall={rain}. "
            f"Model suggests: {top_crops[0][0]}. Recommend the best crop and reason briefly."
        )
        ai_response = utils.call_gemini_api(prompt, gemini_key)
        if ai_response:
            st.success(f"AI Recommendation: {ai_response}")
        else:
            st.info("AI recommendation not available.")

    # Add to history
    if 'history' not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append({
        'params': {'N': N, 'P': P, 'K': K, 'temp': temp, 'hum': hum, 'ph': ph, 'rain': rain},
        'recommendation': top_crops[0][0],
        'timestamp': pd.Timestamp.now()
    })

def show_history():
    """Show recommendation history."""
    st.header("Recommendation History")
    if 'history' in st.session_state and st.session_state.history:
        for i, rec in enumerate(reversed(st.session_state.history[-10:])):  # Last 10
            st.write(f"**{i+1}. {rec['timestamp']}** - Recommended: {rec['recommendation']}")
            with st.expander("Parameters"):
                st.json(rec['params'])
    else:
        st.info("No history yet.")

def disease_detection():
    """Disease detection from image."""
    st.header("🌿 Crop Disease Detection")
    st.markdown("Upload an image of your crop leaf or take a photo to detect possible diseases.")

    # Load disease model
    disease_model = model.load_disease_model()

    # Image input
    uploaded_file = st.file_uploader("Upload an image of your crop leaf", type=["jpg", "jpeg", "png"])
    camera_image = st.camera_input("Or take a photo")

    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=400)
    elif camera_image is not None:
        image = Image.open(camera_image)
        st.image(image, caption="Captured Image", width=400)

    if image is not None and st.button("Detect Disease"):
        with st.spinner("Analyzing image..."):
            result = model.predict_disease(disease_model, image)
            if result:
                disease, confidence, reliable = result
                if disease == "Healthy":
                    st.success(f"Result: {disease}")
                else:
                    if reliable:
                        st.error(f"Detected Disease: {disease}")
                    else:
                        st.warning(f"Detected Disease: {disease} - Low confidence, please verify.")
                # Display static solution
                solution = config.DISEASE_SOLUTIONS.get(disease, "No specific solution available.")
                st.info(f"**Solution:** {solution}")

                # AI-generated solution
                try:
                    gemini_key = st.secrets["GEMINI_API_KEY"]
                except:
                    gemini_key = st.text_input("Enter Gemini API Key for AI solution:", type="password", key="gemini_disease_key")
                if gemini_key:
                    location = st.session_state.get('address', None)
                    ai_solution = utils.call_gemini_disease_solution(disease, None, location, gemini_key)
                    if ai_solution:
                        st.success(f"**AI-Generated Solution:** {ai_solution}")
                    else:
                        st.info("AI solution not available.")

                # User feedback
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Accurate"):
                        st.success("Thank you for your feedback!")
                with col2:
                    if st.button("👎 Inaccurate"):
                        st.info("Feedback noted. We'll improve the model.")
            else:
                st.warning("Unable to analyze the image. Please try again.")
