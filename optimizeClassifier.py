import os
import MusEEG
import pandas as pd

brain = MusEEG.classifier()
train_inputs, train_targets, test_inputs, test_targets = brain.loadTrainingData(percentTrain=0.75)

results = []
hiddenActivations = ['relu', 'sigmoid', 'tanh', 'elu' ]
outputActivations = ['softmax']
hiddenNeurons = range(50, 250, 25)
regularizers = ['l1', 'l2', 'l1_l2', 'no']
losses = ['sparse_categorical_crossentropy']
for a in hiddenActivations:
    for n in hiddenNeurons:
        for r in regularizers:
            for l in losses:
                brain.build_model(brain.inputShape, hiddenNeurons=n, hiddenActivation=a,
                                  numberOfTargets=(max(train_targets) + 1), regularization=r, loss=l)
                name = a + '/ act ' + str(n) + ' neurons/ ' + \
                       r + ' reg/ ' + l + ' losses '
                hist = brain.train_model(train_inputs, train_targets, 80, verbose=0)
                test_accuracy = brain.evaluate_model(test_inputs, test_targets)
                brain.clear()
                results.append([name, test_accuracy])

print('stop')
print(results)
results = pd.DataFrame(results)
results.to_csv(os.path.join(MusEEG.parentDir, 'data', 'ClassifierOptimizations', 'nothalloween.csv'))
results.plot()
print('hi')

#it appears as if using elu, 175 neurons, l1_l2 regulation and sparse categorical crossentropy losses is the best, with 93%