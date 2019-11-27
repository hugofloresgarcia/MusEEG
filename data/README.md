# the MusEEG/data directory

this project uses a good bit of data.

### longRawTrainingSamples

this is where multiple samples of a single gesture are recorded in a single .csv file. 

for convenience of recording, you can record multiple training samples of the same gesture to the MusEEG/data/longRawTrainingSamples directory and later curate them and cut them into single training chunks using `sortTrainingData.py`. 

### savedChunks

once the long .csv files with multiple samples have been cut and curated, the curated and cut chunks should be saved to the MusEEG/data/savedChunks directory. The savedChunks directory has two subdirectories, bigChunks and smallChunks. These are used to train the large keras models and the always-on small keras models, respectively. 

### savedModels

once a keras model has been created and trained, the model can be saved using MusEEG.classifier.savemodel(). For the sake of organization, saved keras models should be stored here. 

### training

this is where inputs and targets used for training of the ANN are stored. 