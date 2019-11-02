from MusEEG import MusEEG
import numpy as np

brain = MusEEG.classifier()
train_inputs, train_targets, test_inputs, test_targets = brain.loadTrainingData(percentTrain=0.75)
brain.build_model(inputShape=brain.inputShape,
                  hiddenNeurons=175,
                  hiddenActivation='elu',
                  numberOfTargets=max(train_targets)+1,
                  regularization='l1_l2 ',
                  loss='sparse_categorical_crossentropy')

brain.train_model(train_inputs, train_targets, nEpochs=80, verbose=2)
brain.evaluate_model(test_inputs, test_targets)

out = brain.classify(train_inputs[1, :])

prompt = input('should we save this model, ye great master?')
if prompt == 'yes':
    name = input('what should we name it, ye great master?')
    brain.savemodel('data/savedModels/'+name)
else:
    print('oh ok')