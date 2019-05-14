
from itertools import islice
from random import random
import time
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from DataStreamerCpp import dsStream  #custom module that wraps the cpp file api.
from matplotlib import interactive
import datetime as dt
import matplotlib.animation as animation
from pylive import live_plotter
interactive(True)
from sklearn import preprocessing

import seaborn as sns
import matplotlib


cppProcess = dsStream()
#CSVfileName ="../datasets/kdd99-unsupervised-ad.csv"
CSVfileName ="../datasets/kddcup_data_10_percent_corrected.csv"
resultsFilePath ="../results/"
MAXROWS = 100

Debug = True

#update the graph
def update_line(hl, new_data):
    hl.set_xdata(numpy.append(hl.get_xdata(), new_data))
    hl.set_ydata(numpy.append(hl.get_ydata(), new_data))
    plt.draw()


def saveResults(data, filename=None):
    if filename == None:
        filename = time.strftime("%Y%m%d-%H%M%S") + '.csv'
    pd.DataFrame(data).to_csv(resultsFilePath+filename)
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
            print(type(value))
            print("classes of {} are:{}".format(key,np.sort(value.classes_)))
            #print(key, type(value)) 
            output[key]= value.inverse_transform(data[key])     
    return output

def startDataStream():   
    count = 0
    inputFile =[]
    labels =[]
    with open(CSVfileName, "r", newline='') as csvfile:
        #for row in csvfile:
        #    if MAXROWS > 0 and count >= MAXROWS:
        #       break
        #    count= count + 1
        #    #break apart the data and the label
        #    #print(type(row))
        #    labels.append(row[41].encode('utf-8'))
        #    inputFile.append(row.encode('utf-8'))
        #    print('currently reading {}  rows \r'.format(count), end ="")
        #csvfile.close()  
                           
        data = pd.read_csv(CSVfileName, header = None, nrows = 20)

        labels = (data.iloc[:,41])        
        inputFile =data.drop([41], axis=1)                                        
        le = preprocessing.LabelEncoder()
        le.fit(labels)
        print("classes of labels are:{}".format(le.classes_))
        labels_encoded = le.transform(labels)
    
        inputFile = inputFile.apply(preprocessing.LabelEncoder().fit_transform)
        #print(inputFile)
        inputFile = inputFile.astype(str)
        inputFile = inputFile.values.tolist()
        labels = labels_encoded.astype(str)
        print(type(labels))                     
        labels = labels.tolist()
        if Debug:
            print(len(inputFile))
            print(len(labels))
        sent = cppProcess.initReaders(inputFile, labels)
        print("initReader {}".format(sent))
        
        print(cppProcess.checkComplete())
        count =0
        size = 100
        x_vec = np.linspace(0,1,size+1)[0:-1]
        #y_vec = np.random.randn(len(x_vec))
        #x_vec = np.zeros(shape=(1,1))
        y_vec = np.zeros(shape=(100,1))
        line1 = []
        fig=plt.figure(figsize=(13,6))
        while cppProcess.checkComplete() != True:
            if Debug:
                print('currently processed {} lines...\r'.format(cppProcess.getResultsCount()), end ="")                      
            #y_vec[-1] = np.random.randn(1)
            y_vec[-1] = cppProcess.getResultsCount()
            line1 = live_plotter(x_vec,y_vec,line1, figure=fig)
            y_vec = np.append(y_vec[1:],0.0)
        
            ## display results ##
            results = cppProcess.getResults()


       
        ### Results ###
        results = cppProcess.getResults()
        
        print("return results: {}".format(results))    
        saveResults(results)
        #input()
        
if __name__ == "__main__":
    startDataStream()
    
