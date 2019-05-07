from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import sys
import traceback
import numpy as np
#class class1(object):
    #"""description of class"""




class Processor:



    def __init__(self, *args, **kwargs):
        print("class init")
        self.knn = KNeighborsClassifier(n_neighbors=3)
        
        return super().__init__(*args, **kwargs)
    #processor called by c++ to complete the processing.    
    def fit(self, train, labels):
        try:
            trainSet =[]
            labelsSet = []
            print("knn fit")
            for i in train:    
                trainSet.append(i.split(','))
            train = np.reshape(train, (-1,1))   
            print(train.shape)
            for i in labels:    
                labelsSet.append(i.split(','))
            labels = np.reshape(labels,(-1,1))
            print(labels.shape)
            #training_set = np.fromstring(train, dtype = None, sep=',')            
            #labels_set = np.fromstring(labels, dtype = None, sep=',')            
            self.knn.fit(trainSet, labelsSet)        
        except:
            print(traceback.format_exc())
        return 0

    # the process function
    def process(self, inputArray):
        try:
            input = np.fromstring(inputArray, dtype = None, sep=',')            
            input = input.reshape(-1,1)            
            result = self.knn.predict(input)
            print("knn result:{}".format(result))       
        except:
            print(traceback.format_exc())
        return result


    def debugPrint(self):        
        return "Python Processor Initialized"
    def threadCheck(self):        
        return "Python Processor ready for Thread"



def debugPrint():

    return "hello how are you?"
