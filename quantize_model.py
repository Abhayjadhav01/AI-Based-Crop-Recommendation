import tensorflow as tf
import config
import os

def quantize_model(keras_model_path=config.DISEASE_MODEL_PATH, tflite_model_path="disease_model_quantized.tflite"):
    # Load the Keras model
    model = tf.keras.models.load_model(keras_model_path)
    # Create a converter object from the Keras model
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # Set the optimization flag to optimize for size and latency
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    # Convert the model
    tflite_model = converter.convert()
    # Save the quantized model
    with open(tflite_model_path, "wb") as f:
        f.write(tflite_model)
    print(f"Quantized TFLite model saved to {tflite_model_path}")

if __name__ == "__main__":
    quantize_model()
