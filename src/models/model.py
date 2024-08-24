import tensorflow as tf
from tensorflow.keras import Sequential
from keras.layers import Dense, Conv3D, Dropout, Flatten, MaxPooling3D
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import time
import os


class ModelHandler:
    def __init__(self, dataset_handler)-> None:
        self.model_path = None
        self.model = None

        # Initialize the dataset handler
        self.dataset_handler = dataset_handler
        
        # Create an O'Neill model by default
        self.create_oneill_model(input_shape=(64, 10, 11, 1), num_labels=2)

    def load_h5_or_hdf5(self, model_path):
        self.model.load_weights(model_path)
        print(f"Model weights loaded from {model_path}")

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
        return history
        
    def test_model(self, test_images, test_labels)-> None:
        test_loss, test_accuracy = self.model.evaluate(test_images, test_labels)
        print(f"Test Loss: {test_loss:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")

    def save_model(self)-> None:
        # Get current timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # Set the save path
        save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", f"model_{timestamp}.hdf5")
        # Save the model
        self.model.save(save_path)
        print(f"Model saved to {save_path}")

    def get_class_weights(self, train_labels)-> dict:
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(train_labels),
            y=train_labels
        )
        class_weight_dict = dict(enumerate(class_weights))
        print(f"Class weights = {class_weight_dict}")
        return class_weight_dict

    
