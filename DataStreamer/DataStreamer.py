
from itertools import islice
from random import random
import time
import csv
import os
import numpy as np
import matplotlib as plt
import pandas as pd
import sys
from DataStreamerCpp import dsStream  #custom module that wraps the cpp file api.

cppProcess = dsStream()
CSVfileName ="../datasets/kdd99-unsupervised-ad.csv"
MAXROWS = 100


def startDataStream():   
    count = 0
    inputFile =[]
    with open(CSVfileName, "r", newline='') as csvfile:
        for row in csvfile:
            if MAXROWS > 0 and count >= MAXROWS:
               break
            count= count + 1
            inputFile.append(row.encode('utf-8'))
            sys.stdout.write("currently reading {} rows \r".format(count))
            sys.stdout.flush()
        csvfile.close()
        print("total rows counted:{}".format(count))
         
        string_length = len(inputFile)
        print("inputCount: {}".format(cppProcess.getCurrentInputCount()))


        sent = cppProcess.initReaders(inputFile)
        print("initReader {}".format(sent))
        
        
        #time.sleep(1) #apparently using a sleep breaks things for some reason? no idea why.
        #for i in range (1000):


        #currently the code is breaking here, TODO figure out why getCurrentInputCount is breaking.
        #error is in the processThread in the cpp file.
        #I think the problem is there is no error checking for running front() and pop_front() when the dqueue is empty. TODO add in try catch blocks to fix this.
        try:
            for i in range (10):
                #print("inputCount: {}".format(cppProcess.getCurrentInputCount()))
                print(i)
                time.sleep(0.01)
        except:
            print("it broke again")
        
        print("inputCount contents: {}".format(cppProcess.getCurrentInput()))

        ### Results ###
        results = cppProcess.getResults()
        print("return results: {}".format(results))                         
        results = ''.join(results)
        try:
            df = pd.read_csv(pd.compat.StringIO(results), header=None)
            print(df.head())
            print(df.shape)
        except: 
            print("error: results not in a csv format.")
        



if __name__ == "__main__":
    startDataStream()
    

