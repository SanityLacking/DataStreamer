from DataStreamerCpp import dsStream  #custom module that wraps the cpp file api.
import numpy as np
import pandas as pd
import collections
import time
import config ## TODO decide whether to use this or not, or to provide some sort of different option for these variables.
import matplotlib.pyplot as plt
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
    def checkException(self):
        output = self.cppProcessor.checkForThreadException()        
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



    #####
    ##### Metric Calculation Section
    #####

def caclulateErr(results, Print=False):
    df =pd.DataFrame()
    df["result"] = results["predicted"].str.strip("[]")
    df["truth"] = results["Label"]
    df['result'] = df['result'].astype(np.float64)
    df['truth'] = df['truth'].astype(np.float64)
    res =df.loc[~(df['result'] == df['truth'])]
    output ="error rate: {}%".format(len(res)/len(results)*100)
    if Print:
        print(output)
    return output


def caclulateLatency(results, vRate=None, Print=False):
    df =pd.DataFrame()    
    df['latency'] = results['latency'].astype(np.float64)
    #if isinstance(le_list,(,)):
    #df['vRate'] = vRate
    res =df.loc[~(df['latency'] >= config.LATENCYBOUND)]
    output ="exceed rate: {}%".format(len(res)/len(results)*100)
    if Print:
        print(output)

    vFig =plt.figure()
    vAx = vFig.add_subplot(1,1,1)
    vYRate = np.arange(0,len(vRate),config.READERINTERVAL)
    vAx.plot(vRate,vYRate)

    return output


def expandVRate(vRate, data):
    valSum=0;
    newVRate =pd.DataFrame()
    addonRate = pd.DataFrame()
    newVRate['vRate'] = vRate
    newVRate['vInterval'] = np.nan
    for i in range(len(vRate)):
#         print(i)
        newVRate['vInterval'][i] = valSum
#         print("val:{}".format(newVRate['vRate'][i]))
        valSum += newVRate['vRate'][i]
    lastRow = newVRate.iloc[-1]
    print("lastrow {} datasize {}".format(lastRow['vInterval'],len(data)))
    dataSize = len(data)
    if lastRow['vInterval'] < dataSize:        
        for i in range(abs(len(newVRate) - len(data))):
    #   row = {"vRate":lastRow['vRate'],"vIntervnal":valSum}
            addonRate = addonRate.append( {"vRate":lastRow['vRate'],"vInterval":valSum}, ignore_index=True)
            valSum += addonRate['vRate'][i]    
    elif lastRow['vInterval'] > len(data):
        #loop through the vRate to find the point that matches the size of results. slice the vRate at that point.
        #actually just c
#       print("newRate {}".format(newVRate))
        maxLen = len(data)        
        for i in range(maxLen):            
            if newVRate['vInterval'][i] > maxLen:
                #print("larger then")
                #slice here and add new ending point of the vRate with interval equal to maxlen
                newVRate = newVRate.iloc[0:i]
                #print(newVRate)
                newVRate = newVRate.append({"vRate":newVRate['vRate'][i-1],"vInterval":maxLen}, ignore_index=True)
                break
            elif newVRate['vInterval'][i] == maxLen:
                #print("same size")
                #slice directly here
                newVRate = newVRate.iloc[0:i]    
                break
    return newVRate 


def visualizeResults(vRate, data):
    fig, ax1 = plt.subplots()

    # ax = plt.axes()
    color = 'tab:blue'
    ax1.set_xlabel('data inputs')
    ax1.set_ylabel('process time (s)')
    lns1 = ax1.plot(data['latency'].astype(np.float64) /1000000)
    lns2 = ax1.plot(data['processTime'].astype(np.float64)/1000000)
    ax1.tick_params(axis='y')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:green'
    ax2.set_xlabel('time (s)')
    ax2.set_ylabel('Input Rate (data points per interval)', color=color)
    lns3 = ax2.plot(vRate['vInterval'],vRate['vRate'], color=color, linestyle = 'dashed')
    ax2.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    ## added these three lines
    lns = lns1+lns2+lns3
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0)

    plt.plot()
    return 0
