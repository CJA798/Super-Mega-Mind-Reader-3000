import tensorflow as tf
from tensorflow.keras import Sequential
from keras.layers import Dense, Conv3D, Dropout, Flatten, MaxPooling3D
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import os
import tifffile


class ModelHandler:
    def __init__(self):
        self.model_path = None
        self.model = None

        # Create an O'Neill model by default
        self.create_oneill_model(input_shape=(64, 10, 11, 1), num_labels=2)

    def load_h5_or_hdf5(self, model_path):
        self.model = self.model.load_weights(model_path)
        print(f"Model weights loaded from {model_path}")
    
    def test_model(self, test_images, test_labels):
        test_loss, test_accuracy = self.model.evaluate(test_images, test_labels)
        print(f"Test Loss: {test_loss:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")

    def create_oneill_model(self, input_shape, num_labels):
        # Create CNN model
        self.model = Sequential()
        self.model.add(Conv3D(32, kernel_size=(3, 3, 3), padding='same', input_shape=input_shape))
        self.model.add(MaxPooling3D(pool_size=(2, 2, 2)))
        self.model.add(Conv3D(64, kernel_size=(3, 3, 3), padding='same'))
        self.model.add(MaxPooling3D(pool_size=(2, 2, 2)))
        self.model.add(Conv3D(128, kernel_size=(5, 4, 3), padding='same'))
        self.model.add(MaxPooling3D(pool_size=(2, 2, 2)))
        self.model.add(Flatten())
        self.model.add(Dense(1024, activation=tf.nn.relu))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1024, activation=tf.nn.relu))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1024, activation=tf.nn.relu))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(num_labels, activation=tf.nn.softmax))

        # Compile model
        self.model.compile(optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy'])

    def train_model(self, train_images, train_labels, val_images, val_labels, class_weight_dict=None, epochs=100, batch_size=32):
        history = self.model.fit(train_images, train_labels,
                            epochs=epochs,
                            batch_size=batch_size,
                            validation_data=(val_images, val_labels),
                            class_weight=class_weight_dict
                            )
        
    def get_class_weights(self, train_labels):
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(train_labels),
            y=train_labels
        )
        class_weight_dict = dict(enumerate(class_weights))
        print(f"Class weights = {class_weight_dict}")

    def load_tiff_data(self):
        images = []
        labels = []
        class_names = os.listdir(self.data_dir)
        for class_name in class_names:
            class_dir = os.path.join(self.data_dir, class_name)
            for file_name in os.listdir(class_dir):
                file_path = os.path.join(class_dir, file_name)
                with tifffile.TiffFile(file_path) as tif:
                    image = tif.asarray()  # Load the image data
                    images.append(image)
                    labels.append(class_name)

        # Convert lists to numpy arrays
        images = np.array(images)
        labels = np.array(labels)

        # Convert class names to integer labels
        label_map = {name: i for i, name in enumerate(class_names)}
        labels = np.array([label_map[label] for label in labels])

        return images, labels
