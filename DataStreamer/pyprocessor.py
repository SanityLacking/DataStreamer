from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import sys
import traceback
import numpy as np
#class class1(object):
    #"""description of class"""

Debug = True


class Processor:
    


    def __init__(self, *args, **kwargs):
        print("class init")
        self.knn = KNeighborsClassifier(n_neighbors=3)
        
        return super().__init__(*args, **kwargs)
    #processor called by c++ to complete the processing.    
    def fit(self, train, labels):
        try:
            if Debug:
                print("train: {}".format(len(train)))
                print("labels: {}".format(len(labels)))

                print("train: {}".format(train[0]))
                print("labels: {}".format(labels[0]))

            print("knn fit")
            
            #trainSet = np.reshape(train, (-1,1))   
            trainSet = np.array(train)
            print("trainset Shape {}".format(trainSet.shape))
            
            labelsSet = np.ravel(labels)
            #labelsSet = np.reshape(labels,(-1,1))
            
            #training_set = np.fromstring(train, dtype = None, sep=',')            
            #labels_set = np.fromstring(labels, dtype = None, sep=',')   
            #         
            trainSet = trainSet.astype(np.float64)
            labelsSet = labelsSet.astype(np.float64)
            self.knn.fit(trainSet, labelsSet)        
        except:
            print(traceback.format_exc())
        return 0

    # the process function
    def process(self, inputArray):
        try:
            #input = np.fromstring(inputArray, dtype = None, sep=',')            
            input = np.array(inputArray)
            input = input.astype(np.float64)
            input = input.reshape(1,-1)

            if Debug:
                print("predict Input shape: {}".format(input.shape))            

            result = self.knn.predict(input)

            if Debug:
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
