
from itertools import islice
from random import random
import time
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys

from matplotlib import interactive
import datetime as dt
import matplotlib.animation as animation
from pylive import live_plotter
interactive(True)
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib

import config
import DataStreamer as DS   # the wrapper for the datastreamer


ds = DS.DataStreamer()


#update the graph
def update_line(hl, new_data):
    hl.set_xdata(numpy.append(hl.get_xdata(), new_data))
    hl.set_ydata(numpy.append(hl.get_ydata(), new_data))
    plt.draw()


def saveResults(data, filename=None):
    if filename == None:
        filename = time.strftime("%Y%m%d-%H%M%S") + '.csv'
    data.to_csv(config.resultsFilePath+filename, index=False)
    return 0



# a better working implementation of the fit transform function available in the label encoder library. Adds in the features
# I personally expected in it when I used it.
#performs individual column label encoding. provides list of label encoders for reversing of the transformation at a later date.
#copy is performed to not effect the original data passed in.
#object only is the default state, set this to false to enable the label encode for all columns individually.
def fit_transform_cols(data, object_only = True):
    if object_only == True:
        object_data =  data.select_dtypes(include=['object']).copy()
    else:
        object_data =  data.copy()
    # print(types.head())
    output = pd.DataFrame(data).copy()
    le_list = {}
    for col in object_data:   
        #print(np.sort(object_data[col].unique()) )
        le = preprocessing.LabelEncoder()
        le.fit(object_data[col])    
        le_list[col] = le
        #print("classes of {} are:{}".format(col,np.sort(le.classes_)))        
        output[col] = le.transform(object_data[col])
    return output, le_list
    
   #reverses the fit_transform_cols. takes in the dataset and the dictionary of of the label encoders. 
   # keys of the dictionary refer to the column names of the input dataframe that are to be transformed reversed.
   #can take single label encoder to run on entire dataframe.
def transform_reverse_cols(data, le_list):
    output = data.copy()
    # if single label encoder is passed, use that for the entire dataframe.
    if isinstance(le_list,preprocessing.LabelEncoder):
          for col in output:
            output[col]= le_list.inverse_transform(output[col])  
            #print("classes of {} are:{}".format(key,np.sort(value.classes_)))                       
    else:
        output = pd.DataFrame(data).copy()
        for key, value in le_list.items():
            print("value type:{}".format(type(value)))
            print("classes of {} are:{}".format(key,np.sort(value.classes_)))
            #print(key, type(value)) 
            output[key]= value.inverse_transform(data[key])     
    return output

def startDataStream():   
    count = 0
    inputFile =[]
    labels =[]
    csv_start_time = time.monotonic()                           
    data = pd.read_csv(config.CSVfileName, header = config.HEADER, nrows = config.MAXROWS)

    labels = (data.iloc[:,41])        
    inputFile =data.drop([41], axis=1)                                        
    le = preprocessing.LabelEncoder()
    le.fit(labels)
    print("classes of labels are:{}".format(le.classes_))
    labels_encoded = le.transform(labels)
    
    inputFile, le_list = fit_transform_cols(inputFile)
    #inputFile = inputFile.apply(preprocessing.LabelEncoder().fit_transform)
    #print(inputFile)
    inputFile = inputFile.astype(str)
    inputFile = inputFile.values.tolist()
    labels = labels_encoded.astype(str)

    X_train, X_test, y_train, y_test = train_test_split(inputFile, labels, test_size=config.TESTSIZE, random_state=config.RANDOMSTATE)

    #print(type(labels))                     
    labels = labels.tolist()
    if config.DEBUG:
        print("total set size:{}".format(len(inputFile)))
        print("train size: {}".format(len(X_train)))            
        print("test size: {}".format(len(X_test)))
    start_time = time.monotonic()
    print("csv read in: {} seconds".format(start_time - csv_start_time))


    vRate=np.linspace(1,100,100)
    vRate=np.append(vRate,np.linspace(100,1,100))
    print(vRate)
    ds.initialize(10) 

    sent = ds.process(X_train, y_train, X_test)
    #print("initReader: {} sent, {} recieved".format(len(inputFile),sent))
        
    #print(cppProcess.checkComplete())
    count =0
    size = 100
    x_vec = np.linspace(0,1,size+1)[0:-1]
    #y_vec = np.random.randn(len(x_vec))
    #x_vec = np.zeros(shape=(1,1))
    y_vec = np.zeros(shape=(100,1))
    line1 = []
    fig=plt.figure(figsize=(13,6))
    while ds.checkComplete() != True:
        #print(ds.checkException())
        #if config.DEBUG:
        #   print('currently processed {} lines...\r'.format(ds.getResultsCount()))                      
        #y_vec[-1] = np.random.randn(1)
        y_vec[-1] = ds.getResultsCount()
        line1 = live_plotter(x_vec,y_vec,line1, figure=fig)
        y_vec = np.append(y_vec[1:],0.0)
        
        ## display results ##
        #results = cppProcess.getResults()


       
    ### Results ###
        
    results = ds.getResults()
    end_time = time.monotonic()
    print("results processed in: {} seconds".format(end_time - start_time))
    print(type(results))
    df_results = pd.DataFrame(results)
    #print(df_results.shape)
    #print(y_test.shape)

    # if the y_test array isn't full, initialize it to NAN values so it can be added to the output for consistency sake.
    if len(y_test) == 0:  
        y_test = np.full(len(df_results.index), np.nan)

    df_results['label'] = y_test
    #print(df_results.head())
    df_results = df_results.rename(columns={ df_results.columns[0]: "predicted",df_results.columns[1]: "latency",df_results.columns[2]: "processTime",df_results.columns[3]: "Label"  })
    #print("return results: {}".format(results))    
    print("return results: {} rows processed".format(len(df_results)))    
    print(df_results.head())    

    print(DS.caclulateErr(df_results))
    print(DS.caclulateLatency(df_results, vRate))

    
    saveResults(df_results)
    input()

        
        
if __name__ == "__main__":
    startDataStream()
    print("program end!")
    
