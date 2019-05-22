from DataStreamerCpp import dsStream  #custom module that wraps the cpp file api.
import numpy as np
import pandas as pd
import time
## Purpose of this class file is to provide an easy to read python class for quick intergration into a python project.
## rather then having to examine the c++ code and output, you can just use this wrapper. 
## additionally configuration args can be added in here without the need to expose them to the main file.

class DataStreamer(object):
    
    
    
    def __init__(self, *args, **kwargs):                      
        self.cppProcessor = dsStream()
        return super().__init__(*args, **kwargs)

    def initialize():


        return 0

    def process(self, X_train, y_train, X_test):
        output = self.cppProcessor.initReaders(X_train, y_train, X_test)
        return output


    def checkComplete(self ):
        output = self.cppProcessor.checkComplete() 
        return output

    def getResultsCount(self ):
        output = self.cppProcessor.getResultsCount()
        return output

    def getResults(self ):
        output = self.cppProcessor.getResults()
        return output


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