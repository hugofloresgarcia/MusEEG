import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd


# todo: rebuild tensor flow with AVX2 FMA for faster performance

class classifier:
    hiddenNeurons = 20
    numberOfTargets = 10
    inputShape = 350

    # build the model
    def build_model(self, inputShape, hiddenNeurons, numberOfTargets, hiddenActivation='relu',
                    outputActivation='softmax'):
        self.model = keras.Sequential([
            keras.layers.Flatten(input_shape=(inputShape,)),
            keras.layers.Dense(hiddenNeurons, activation=hiddenActivation),
            keras.layers.Dense(numberOfTargets, activation=outputActivation)
        ])
        self.model.compile(optimizer='adam',
                           loss='sparse_categorical_crossentropy',
                           metrics=['accuracy'])
        self.hiddenNeurons = hiddenNeurons
        self.numberOfTargets = numberOfTargets
        self.inputShape = inputShape
        return self.model

    # train the model
    def train_model(self, train_inputs, train_targets, nEpochs):
        self.model.fit(train_inputs, train_targets, epochs=nEpochs)

    def evaluate_model(self, test_inputs, test_targets, verbose=2):
        test_loss, test_acc = self.model.evaluate(test_inputs, test_targets, verbose)
        print('\nTest accuracy:', test_acc)

    def classify(self, inputVector):
        prediction = self.model.predict(inputVector)
        output = np.argmax(prediction)
        return output