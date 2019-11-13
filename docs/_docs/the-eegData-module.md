---
layout: page
title:  "the eegData module"
categories: [docs]
comments: false
---
##### The eegData Class

The eegData class can load and preprocess EEG data. The eegData class has the following defaulted attributes (tailored for the Emotiv EPOC+)

{% highlight python %}
class eegData:
    threshold = 250 #threshold, in mV, to indicate that a new facial gesture was created
    sampleRate = 256 #sample rate of Emotiv EPOC+
    chunkSize = int(256*1.5) #number of samples in chunks that are processed
    backTrack = 35 #number of samples to backtrack from threshold
    nchannels = 14 #number of channels in Emotiv EPOC+
    emotivChannels = ["EEG.AF3", "EEG.F7", "EEG.F3", "EEG.FC5", "EEG.T7", "EEG.P7", "EEG.O1",
                           "EEG.O2", "EEG.P8", "EEG.T8", "EEG.FC6", "EEG.F4", "EEG.F8", "EEG.AF4"]
{% endhighlight  %}

The `threshold` attribute defines the threshold (in mV) that an EEG signal has to cross in order for it to start the classification process. If the current EEG sample is past the given `threshold`, the processor in the main file (to be created) will create an `eegData` object with the number of samples in `chunkSize` starting at:
     `current sample where threshold was passed - backTrack`

The `backTrack` parameter was added because some EEG messages have valuable information well before the threshold is passed, so the chunk that is processed must contain data before the threshold.

##### The Wavelet Method
{% highlight python %}
    def wavelet(self):
        """"
        wavelet transform (4-level) for a single eeg chunk
        creates a self.wavelets list which contains np arrays with the coefficients
        """
        self.nchannels = len(self.chunk[0, :])
        self.cA4 = []
        self.cD4 = []
        self.cD3 = []
        self.cD2 = []
        self.cD1 = []
        for i in range(0, self.nchannels):
            cA4, cD4, cD3, cD2, cD1 = wavedec(self.chunk[:, i], 'db2', level=4)
            self.cA4.append(cA4)
            self.cD4.append(cD4)
            self.cD3.append(cD3)
            self.cD2.append(cD2)
            self.cD1.append(cD1)

        self.wavelets = [np.asarray(self.cA4), np.asarray(self.cD4), np.asarray(self.cD3), np.asarray(self.cD2), np.asarray(self.cD1)]
{% endhighlight  %}

The `wavelet` method performs a 4-level wavelet decomposition on EEG signals. Based on my research (will upload a link to my thesis as soon as its done) a 4-level wavelet decomposition is an efficient way of performing feature extraction on EEG signals, as it essentially splits the raw signal into alpha, beta, delta, theta, and gamma waves, which are all different brain waves where different brain processes are executed.

The `wavelet` method processes the `self.chunk`, which should be created prior to processing.
As an output, the `wavelet` method creates a `self.wavelets` attribute, which is a list that contains lumpy arrays with each decomposition vector that results from the wavelet decomposition.

##### the extractStatsFromWavelets method

{% highlight python %}   
def extractStatsFromWavelets(self):
        """
        calculates mean, standard deviation, variance, kurtosis, and skewness from self.wavelets object.
        creates self.mean, self.std, self.kurtosis, self.skew which are numpy arrays with 14 rows (eeg channels)
        and 5 columns (per coefficients)
        """
        self.mean = np.ndarray((self.nchannels, 5))
        self.var = np.ndarray((self.nchannels, 5))
        self.std = np.ndarray((self.nchannels, 5))
        self.kurtosis = np.ndarray((self.nchannels, 5))
        self.skew = np.ndarray((self.nchannels, 5))
        ## ojo, dimensions are transposed here
        for i in range(0, self.nchannels):
            self.mean[i, :] = [np.mean(self.cA4[i]), np.mean(self.cD4[i]), np.mean(self.cD3[i]), np.mean(self.cD2[i]), np.mean(self.cD1[i])]
            self.var[i, :] = [np.var(self.cA4[i]), np.var(self.cD4[i]), np.var(self.cD3[i]), np.var(self.cD2[i]), np.var(self.cD1[i])]
            self.std[i, :] = [np.std(self.cA4[i]), np.std(self.cD4[i]), np.std(self.cD3[i]), np.std(self.cD2[i]), np.std(self.cD1[i])]
            self.kurtosis[i, :] = [kurtosis(self.cA4[i]), kurtosis(self.cD4[i]), kurtosis(self.cD3[i]), kurtosis(self.cD2[i]), kurtosis(self.cD1[i])]
            self.skew[i, :] = [skew(self.cA4[i]), skew(self.cD4[i]), skew(self.cD3[i]), skew(self.cD2[i]), skew(self.cD1[i])]
{% endhighlight  %}

The `extractStatsFromWavelets` calculates the mean, standard deviation, variance, kurtosis, and skewness from each of the wavelet coefficient vectors stored in self.wavelets. As a result, it creates the self.mean, self.std, self.kurtosis, self.skew which are numpy arrays with 14 rows (eeg channels) and 5 columns (per coefficients).

##### the flattenIntoVector method
{% highlight python %}   
    def flattenIntoVector(self):
        """
        creates an input array for ANN, structured as:
            [mean, var, std, kurtosis, skew]
            each of these is 14 channels * 5 wavelet coefficients long = 70 floats
            vector is flattened, and for 5 stat features * 70 numbers = 350 numbers
        """
        mean = self.mean.flatten()
        var = self.var.flatten()
        std = self.std.flatten()
        kurtosis = self.kurtosis.flatten()
        skew = self.skew.flatten()

        self.inputVector = np.array([mean, var, std, kurtosis, skew])
        self.inputVector = self.inputVector.flatten()
        return self.inputVector
{% endhighlight  %}

The `flattenIntoVector` method prepares the statistical features calculated in `extractStatsFromWavelets` for a Deep Network by concatenating the vectors and flattening them into a single array. The structure of the input array is as follows:
{% highlight python %}   
            [mean, var, std, kurtosis, skew]
            each of these is 14 channels * 5 wavelet coefficients long = 70 floats
            vector is flattened, and for 5 stat features * 70 numbers = 350 floats
{% endhighlight  %}
