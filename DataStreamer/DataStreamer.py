from DataStreamerCpp import dsStream  #custom module that wraps the cpp file api.
import numpy as np
import pandas as pd
import collections
import time
## Purpose of this class file is to provide an easy to read python class for quick intergration into a python project.
## rather then having to examine the c++ code and output, you can just use this wrapper. 
## additionally configuration args can be added in here without the need to expose them to the main file.

class DataStreamer(object):
    
    
    
    def __init__(self, *args, **kwargs):                      
        self.cppProcessor = dsStream()
        return super().__init__(*args, **kwargs)
    
    
    #initalize the stream
    #vRate: the variable rate of how many data points to arrive per step default  100milliseconds
    #stepRate: the step rate in miliseconds. default is 100, aka 1/10 of a second.
    #readerCount: TODO, number of readers to use a threads for incoming datapoints.
    #randomRate: random noise to apply to the rate per step. default is 0
    #randomStep: TODO
    #loadMethod: TODO set which load method to use, default, no load balancer engaged.
    def initialize(self, vR, stepRate = 10, randomRate = 0, randomStep = 0):        
        vRate = vR
        if isinstance(vRate,(collections.Sequence, np.ndarray, pd.DataFrame)):  
            #vRate is a sequence, follow the sequence step by step 
            print("sequence")
            if isinstance(vRate,np.ndarray):
                vRate = vRate.tolist()
            if isinstance(vRate,pd.DataFrame): #TODO, check how the interaction between dataframes and the list works for this.                
                vRate = vRate.values.tolist()
            if len(vRate) > 0:
                self.cppProcessor.setVRate(vRate)
            else: 
                raise ValueError('Variable rates in Initialize must not be empty, consider using a scalar.')
            
        else: 
            #vRate is a scalar
            self.cppProcessor.setVRateScalar(vRate)


        return 0

    def process(self, X_train, y_train, X_test):
        output = self.cppProcessor.initReaders(X_train, y_train, X_test)
        return output


    def checkComplete(self):
        output = self.cppProcessor.checkComplete()        
        return output

    def getResultsCount(self):
        output = self.cppProcessor.getResultsCount()
        return output

    def getResults(self):
        output = self.cppProcessor.getResults()
        return output
    
    
    #pause the processor, will not be immediate, but will stop next item from being processed. time recorders also paused. If already paused no effect.
    def pause(self):
        #TODO
        #output = self.cppProcessor.pause()
        return 0

    #resume the processor after pause has been called. If not paused, no effect.
    def resume(self):
        #TODO
        #output = self.cppProcessor.resume()
        return 0

def caclulateErr(results, print=False):
    df =pd.DataFrame()
    df["result"] = results["predicted"].str.strip("[]")
    df["truth"] = results["Label"]
    df['result'] = df['result'].astype(np.float64)
    df['truth'] = df['truth'].astype(np.float64)
    res =df.loc[~(df['result'] == df['truth'])]
    output ="error rate: {}%".format(len(res)/len(results)*100)
    if print:
        print(output)
    return output