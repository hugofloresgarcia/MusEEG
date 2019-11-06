## the MusEEG/scripts directory

The MusEEG/scripts directory contains a series of sample scripts that can be useful during the creation of your own training samples and ANN (artificial neural network).

### sortTrainingData
`sortTrainingData.py` provides an example of importing long .csv files that contain multiple samples of the same gesture from the MusEEG/data/longRawTrainingSamples directory and using the `MusEEG.TrainingDataMacro` class to evaluate, curate, and save individual training samples to the /data/savedChunks directory

### processTrainingData
`processTrainingData.py` grabs the curated chunks from the /data/savedChunks directory and performs the processing and feature extraction routine (wavelet transform and statistical extraction), as well as creates training inputs and targets and stores them in the /data/training directory

### optimizeClassifier
because the dataset is quite small, training ANN models is relatively computationally inexpensive. This lets us perform an exhaustive search of different ANN models with different activation units, hidden layer sizes, and regularization parameters within the span of a couple of minutes. `optimizeClassifier.py` tries every combination of different hidden layer activations, output layer activations, regularization parameters, number of hidden neurons, and loss algorithms to find the one that performs with the highest accuracy. The `optimizeClassifier.py` creates a .csv file in the /data/ClassifierOptimizations directory which contains the test results for each of the combinations tried. Currently, there isn't a way for it to find the most accurate model automatically, so you will have to look through the generated .csv file in /data/ClassifierOptimizations manually. 

### saveModels
`saveModels.py` trains and saves a keras model in the /data/savedModels directory. 

todo: integrate `optimizeClassifier` and  `saveModels.py` for it to automatically save the model with the highest training/testing accuracy. 