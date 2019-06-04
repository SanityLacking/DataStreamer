import numpy as np
import pandas as pd


### different time series that can be used as variable rates for the benchmark

def generateSeries(type = "", max=10, min=1, step = 100, random = False, length = 1000):
    output = []
    if type == "":
        output=np.linspace(min,max,step)
    
    elif type =="linear":
        output=np.linspace(min,max,step)

    elif type =="twospikes":
        output = np.append(output, np.full(100,10))
        output = np.append(output, np.linspace(10,100,10))
        output = np.append(output, np.linspace(100,10,10))
        output = np.append(output, np.full(100,10))
        output = np.append(output, np.linspace(10,20,30))
        
        noise = 0.0008*np.asarray(random.sample(range(0,1000),800))
    return output