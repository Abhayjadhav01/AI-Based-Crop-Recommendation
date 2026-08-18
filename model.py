import streamlit as st
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
import config
import numpy as np
from PIL import Image
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
except ImportError:
    tf = None
    Sequential = None
    Conv2D = None
    MaxPooling2D = None
    Flatten = None
    Dense = None

@st.cache_resource
def load_model(model_path=config.MODEL_PATH):
    """Load the pre-trained model from a pickle file."""
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        st.success("Model loaded successfully!")
        return model
    else:
        st.error(f"Model file '{model_path}' not found. Please train the model first.")
        st.stop()
        return None

def train_and_save_model(dataset_file=config.DATASET_PATH, model_path=config.MODEL_PATH):
    """Train the model from dataset and save it."""
    st.info("Training the model. This may take a moment...")
    try:
        df = pd.read_csv(dataset_file)
        features = config.FEATURES
        target = config.TARGET
        X = df[features]
        y = df[target]
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X, y)
        joblib.dump(model, model_path)
        st.success("Model trained and saved successfully!")
        return model
    except Exception as e:
        st.error(f"Error training model: {e}")
        return None

def predict_crop(model, input_data):
    """Predict the top crop recommendation."""
    prediction = model.predict(input_data)
    return prediction[0]

def get_top_crops(model, input_data, top_n=config.TOP_N_CROPS):
    """Get top N crop recommendations based on prediction probabilities."""
    proba = model.predict_proba(input_data)[0]
    classes = model.classes_
    top_indices = proba.argsort()[-top_n:][::-1]
    top_crops = [(classes[i], proba[i] * 100) for i in top_indices]  # Convert to percentage
    return top_crops

@st.cache_resource
def load_disease_model(model_path=config.DISEASE_MODEL_PATH):
    """Load the pre-trained disease detection model."""
    if tf is None:
        return None
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path)
        return model
    else:
        # Create dummy model if not exists
        if Sequential is None:
            st.error("TensorFlow not available. Cannot create dummy model.")
            return None
        st.info("Disease model not found. Creating dummy model...")
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(config.IMAGE_SIZE[0], config.IMAGE_SIZE[1], 3)),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(128, activation='relu'),
            Dense(len(config.DISEASE_CLASSES), activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        model.save(model_path)
        st.success("Dummy disease model created and saved.")
        return model

def preprocess_image(image):
    """Preprocess the image for the model with center crop."""
    # Resize to larger size first, then center crop to IMAGE_SIZE
    temp_size = (256, 256)
    image = image.resize(temp_size)
    # Center crop
    width, height = image.size
    left = (width - config.IMAGE_SIZE[0]) / 2
    top = (height - config.IMAGE_SIZE[1]) / 2
    right = left + config.IMAGE_SIZE[0]
    bottom = top + config.IMAGE_SIZE[1]
    image = image.crop((left, top, right, bottom))
    image_array = np.array(image) / 255.0  # Normalize
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
    return image_array

def predict_disease(model, image):
    """Predict disease from the image."""
    if model is None:
        return None
    processed_image = preprocess_image(image)
    predictions = model.predict(processed_image)
    predicted_class_idx = np.argmax(predictions, axis=1)[0]
    predicted_class = config.DISEASE_CLASSES[predicted_class_idx]
    confidence = predictions[0][predicted_class_idx] * 100
    reliable = confidence >= config.CONFIDENCE_THRESHOLD
    return predicted_class, confidence, reliable
