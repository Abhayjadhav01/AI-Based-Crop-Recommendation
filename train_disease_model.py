import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import config
import kagglehub

def create_model(num_classes):
    model = Sequential([
        Conv2D(16, (3, 3), activation='relu', input_shape=(config.IMAGE_SIZE[0], config.IMAGE_SIZE[1], 3)),
        MaxPooling2D((2, 2)),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    return model

def main(dataset_path, epochs=30, batch_size=32):
    # Data preprocessing
    datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    train_generator = datagen.flow_from_directory(
        dataset_path,
        target_size=config.IMAGE_SIZE,
        batch_size=batch_size,
        class_mode='categorical',
        subset='training'
    )

    validation_generator = datagen.flow_from_directory(
        dataset_path,
        target_size=config.IMAGE_SIZE,
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation'
    )

    num_classes = len(train_generator.class_indices)
    print(f"Number of classes: {num_classes}")
    print(f"Class indices: {train_generator.class_indices}")

    # Create model
    model = create_model(num_classes)

    # Compile model
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    # Add callbacks
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=1e-6)

    # Train model
    history = model.fit(
        train_generator,
        epochs=epochs,
        validation_data=validation_generator,
        callbacks=[early_stopping, reduce_lr]
    )

    # Evaluate on test set (using validation as test for simplicity)
    test_loss, test_accuracy = model.evaluate(validation_generator)
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}")

    # Save evaluation metrics
    with open('disease_model_metrics.txt', 'w') as f:
        f.write(f"Test Loss: {test_loss:.4f}\n")
        f.write(f"Test Accuracy: {test_accuracy:.4f}\n")
        f.write(f"Number of Classes: {num_classes}\n")
        f.write(f"Class Indices: {train_generator.class_indices}\n")

    # Save model
    model.save(config.DISEASE_MODEL_PATH, save_format='h5')
    print(f"Model saved as {config.DISEASE_MODEL_PATH}")

if __name__ == "__main__":
    import sys
    epochs = 30
    batch_size = 32
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        # Download latest version
        dataset_path = kagglehub.dataset_download("emmarex/plantdisease")
        print("Path to dataset files:", dataset_path)
    if os.path.exists(dataset_path):
        if len(sys.argv) > 2:
            try:
                epochs = int(sys.argv[2])
            except ValueError:
                print("Invalid epochs value, using default 30")
        if len(sys.argv) > 3:
            try:
                batch_size = int(sys.argv[3])
            except ValueError:
                print("Invalid batch size value, using default 32")
        main(dataset_path, epochs=epochs, batch_size=batch_size)
    else:
        print("Invalid path. Please provide a valid directory path.")
