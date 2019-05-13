
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
    
