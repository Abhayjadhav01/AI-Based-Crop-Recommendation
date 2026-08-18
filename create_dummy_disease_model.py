
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import config

print("Creating dummy disease model...")

# Create a simple CNN model
model = Sequential([
    Conv2D(16, (3, 3), activation='relu', input_shape=(config.IMAGE_SIZE[0], config.IMAGE_SIZE[1], 3)),
    MaxPooling2D((2, 2)),
    Conv2D(32, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(len(config.DISEASE_CLASSES), activation='softmax')
])

print("Model created.")

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("Model compiled.")

# Save the model
model.save(config.DISEASE_MODEL_PATH)
print(f"Dummy disease model saved as {config.DISEASE_MODEL_PATH}")
