import os
import platform
import pandas
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import regularizers
from MusEEG import parentDir
from sklearn.metrics import confusion_matrix

class classifier:
    hiddenNeurons = 20
    numberOfTargets = 10
    inputShape = 350

    def __init__(self):
        print('welcome')

    def loadTrainingData(self, percentTrain=0.75,
                         address=os.path.join(parentDir, 'data', 'training'),
                         subdir='bigChunks',
                         inputFilename='inputs.csv',
                         targetFilename='targets.csv'):
        inputsAll = pandas.read_csv(os.path.join(address, subdir,  inputFilename)).values
        targetsAll = pandas.read_csv(os.path.join(address, subdir,  targetFilename)).values
        # use index from 1 on bc index 0 is just a counter for some reason.
        inputsAll[:, 0] = targetsAll[:, 1]
        # first column of inputsAll will now be the targets (sorry programming gods, I'm going crazy over this one)
        trainingData = pandas.DataFrame(inputsAll)
        #shuffle the data!!!
        trainingData = trainingData.reindex(np.random.permutation(trainingData.index))
        trainingData = trainingData.values

        #slice it up, baby
        slice = round(len(trainingData[:, 0])*percentTrain)
        train_inputs = trainingData[0:slice, 1:]
        train_targets = trainingData[0:slice, 0]
        test_inputs = trainingData[slice:, 1:]
        test_targets = trainingData[slice:, 0]

        return train_inputs, train_targets, test_inputs, test_targets

    # build the model
    def build_model(self, inputShape, hiddenNeurons, numberOfTargets, hiddenActivation='relu',
                    outputActivation='softmax', regularization='l2_l2', optimizer='adam', loss='sparse_categorical_crossentropy'):
        if regularization == 'l1':
            reg = regularizers.l1(0.001)
            self.model = keras.Sequential([
                keras.layers.Dense(hiddenNeurons,
                                   activation=hiddenActivation,
                                   activity_regularizer=reg,
                                   input_dim=inputShape),
                keras.layers.Dense(numberOfTargets, activation=outputActivation),
            ])
        elif regularization == 'l2':
            reg = regularizers.l2(0.001)
            self.model = keras.Sequential([
                keras.layers.Dense(hiddenNeurons,
                                   activation=hiddenActivation,
                                   activity_regularizer=reg,
                                   input_dim=inputShape),
                keras.layers.Dense(numberOfTargets, activation=outputActivation),
            ])
        elif regularization == 'l1_l2':
            reg = regularizers.l1_l2(0.001)
            self.model = keras.Sequential([
                keras.layers.Dense(hiddenNeurons,
                                   activation=hiddenActivation,
                                   activity_regularizer=reg,
                                   input_dim=inputShape),
                keras.layers.Dense(numberOfTargets, activation=outputActivation),
            ])
        else:
            self.model = keras.Sequential([
                keras.layers.Dense(hiddenNeurons, activation=hiddenActivation,
                                   input_dim=inputShape),
                keras.layers.Dense(numberOfTargets, activation=outputActivation)])

        self.model.compile(optimizer=optimizer,
                           loss=loss,
                           metrics=['accuracy'])
        self.hiddenNeurons = hiddenNeurons
        self.numberOfTargets = numberOfTargets
        self.inputShape = inputShape
        return self.model

    # train the model
    def train_model(self, train_inputs, train_targets, nEpochs, verbose=0):
        self.model.fit(train_inputs, train_targets, epochs=nEpochs, verbose=verbose)

    def evaluate_model(self, test_inputs, test_targets, verbose=2):
        test_loss, test_acc = self.model.evaluate(test_inputs, test_targets, verbose)
        print('\nTest accuracy:', test_acc)
        return test_acc

    def print_confusion(self, test_inputs, test_targets):
        prediction = self.model.predict(test_inputs)
        prediction = np.array([np.argmax(row) for row in prediction])
        cm = confusion_matrix(test_targets, prediction)
        print(cm)
        return cm

    def classify(self, inputVector):
        prediction = self.model.predict(inputVector)
        output = np.argmax(prediction)
        return output

    def clear(self):
        keras.backend.clear_session()

    def savemodel(self, filename, address=os.path.join(parentDir, 'data', 'savedModels')):
        self.model.save(os.path.join(address, filename), save_format='tf')

    def loadmodel(self, filename, address=os.path.join(parentDir, 'data', 'savedModels')):
        """
        load a saved keras model
        :param filename: name of the savedModel
        :param address: address (relative to the parent directory) where your model is stored. defaults to /data/SavedModels
        :return:
        """
        self.model = keras.models.load_model(os.path.join(address, filename))
        if platform.uname()[1] == 'raspberrypi':
            litemodel = self.createLiteModel(self.model)
            self.model = litemodel


    def createLiteModel(self, model):
        """
        create tflite model from saved keras model
        :param filename: name of the savedModel
        :param address: address (relative to the parent directory) where your model is stored. defaults to /data/SavedModels
        :return: tensorflow lite model
        """
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        return converter.convert()


