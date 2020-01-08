import MusEEG
import pandas
import os
import numpy as np

save = False

brain = MusEEG.classifier()
train_inputs, train_targets, test_inputs, test_targets = brain.loadTrainingData(subdir=os.path.join('batch2_improved_320samples', 'bigChunks'), percentTrain=0.7)
brain.build_model(inputShape=brain.inputShape,
                  hiddenNeurons=100,
                  hiddenActivation='elu',
                  numberOfTargets=max(train_targets) + 1,
                  regularization='l1_l2 ',
                  loss='sparse_categorical_crossentropy')

brain.train_model(train_inputs, train_targets, nEpochs=50, verbose=2)
brain.evaluate_model(test_inputs, test_targets)

cm = brain.print_confusion(test_inputs, test_targets)

cmdataframe = pandas.DataFrame(cm)

print('hi')
if save:
    prompt = input('should we save this model, ye great master?')
    if prompt == 'yes':
        name = input('what should we name it, ye great master?')
        brain.savemodel(name)
    else:
        print('oh ok')
