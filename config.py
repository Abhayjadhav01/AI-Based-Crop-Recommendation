# Configuration file for Crop Recommendation App

# API Keys (use st.secrets or environment variables)
OPENWEATHER_API_KEY = None  # To be set via st.secrets or input
GEMINI_API_KEY = None  # To be set via st.secrets or input
GOOGLE_MAPS_API_KEY = None  # To be set via st.secrets or input

# API URLs
OPENWEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# Default Values
DEFAULT_LOCATION = [20.5937, 78.9629]  # India center
DEFAULT_PARAMS = {
    'N': 90.0,
    'P': 42.0,
    'K': 43.0,
    'temperature': 20.88,
    'humidity': 82.0,
    'ph': 6.5,
    'rainfall': 202.9
}

# Model Configuration
MODEL_PATH = "crop_model.pkl"
DATASET_PATH = "Crop_recommendation.csv"
FEATURES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
TARGET = 'label'

# UI Configuration
MAP_HEIGHT = 600
MAP_WIDTH = 900
ZOOM_DEFAULT = 5
ZOOM_SELECTED = 15

# Other Constants
TOP_N_CROPS = 3

# Disease Detection Constants
DISEASE_MODEL_PATH = "disease_model.h5"  # Assuming a Keras model
DISEASE_CLASSES = [
    "Healthy",
    "Bacterial Spot",
    "Early Blight",
    "Late Blight",
    "Leaf Mold",
    "Septoria Leaf Spot",
    "Spider Mites",
    "Target Spot",
    "Tomato Mosaic Virus",
    "Tomato Yellow Leaf Curl Virus",
    "Potato Late Blight",
    "Corn Borer",
    "Wheat Rust",
    "Rice Blast",
    "Apple Scab",
    "Grape Downy Mildew"
]  # Expanded classes for multiple crops
IMAGE_SIZE = (224, 224)  # Input size for the model
CONFIDENCE_THRESHOLD = 70.0  # Minimum confidence for reliable detection

# Disease Solutions (Detailed and Preventive)
DISEASE_SOLUTIONS = {
    "Healthy": "No action needed. The plant is healthy. Continue regular care: proper watering, fertilization, and pest monitoring.",
    "Bacterial Spot": "Remove and destroy affected leaves immediately. Apply copper-based fungicide every 7-10 days. Avoid overhead watering to prevent spread. Use drip irrigation. Plant resistant varieties in future.",
    "Early Blight": "Remove infected leaves and dispose of them. Apply fungicide like chlorothalonil or mancozeb. Improve air circulation by pruning. Mulch around plants to prevent soil splash. Rotate crops annually.",
    "Late Blight": "Remove and destroy all infected plants immediately. Apply fungicide containing chlorothalonil or copper. Avoid wet conditions; ensure good drainage. Use blight-resistant varieties. Monitor weather forecasts.",
    "Leaf Mold": "Improve ventilation by spacing plants properly. Apply fungicide if conditions are humid. Reduce humidity with fans or better airflow. Avoid wetting leaves during watering. Use resistant varieties.",
    "Septoria Leaf Spot": "Remove affected leaves promptly. Apply fungicide such as chlorothalonil. Avoid wetting foliage. Ensure plants are not overcrowded. Rotate crops to prevent recurrence.",
    "Spider Mites": "Spray with insecticidal soap, neem oil, or miticides. Increase humidity around plants. Introduce natural predators like ladybugs. Avoid broad-spectrum insecticides that harm beneficial insects.",
    "Target Spot": "Remove infected leaves. Apply fungicide regularly. Ensure proper plant spacing for air circulation. Avoid overhead watering. Use crop rotation and resistant varieties.",
    "Tomato Mosaic Virus": "Remove and destroy infected plants immediately. Control aphids with insecticides or neem oil. Use virus-resistant tomato varieties. Disinfect tools between uses. Avoid smoking near plants.",
    "Tomato Yellow Leaf Curl Virus": "Control whitefly populations with insecticides or sticky traps. Use TYLCV-resistant varieties. Remove infected plants. Plant in shaded areas if possible. Monitor transplants.",
    "Potato Late Blight": "Destroy infected plants and tubers. Apply fungicide protectants. Ensure good drainage and avoid overhead irrigation. Plant certified seed potatoes. Rotate crops away from potatoes.",
    "Corn Borer": "Apply insecticides targeting borers. Use Bt corn varieties. Monitor for egg masses and destroy. Crop rotation helps. Plant trap crops like sudangrass.",
    "Wheat Rust": "Apply fungicides like triazoles. Use rust-resistant wheat varieties. Remove volunteer wheat plants. Ensure proper nitrogen fertilization without excess.",
    "Rice Blast": "Apply fungicide such as tricyclazole. Use resistant rice varieties. Avoid excessive nitrogen. Ensure proper water management. Remove infected plant debris.",
    "Apple Scab": "Apply fungicide during wet weather. Use scab-resistant apple varieties. Prune to improve air circulation. Rake and destroy fallen leaves. Avoid overhead irrigation.",
    "Grape Downy Mildew": "Apply fungicide like copper or mancozeb. Ensure good canopy ventilation. Avoid wetting leaves. Use mildew-resistant grape varieties. Monitor humidity levels."
}
