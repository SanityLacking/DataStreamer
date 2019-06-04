
#CSVfileName ="../datasets/kdd99-unsupervised-ad.csv"
HEADER = None
CSVfileName ="../datasets/kddcup_data_10_percent_corrected.csv"
resultsFilePath ="../results/"
MAXROWS = 10000
DEBUG = True
TESTSIZE = 0.95
RANDOMSTATE = 16
PROCESSOR = "KNN"   #Options are "KNN", "RTREE"

LATENCYBOUND = 100000 #upper bound for latency of data from input to processed. in microseconds aka, 1,000,000 to one second

READERINTERVAL = 100000 #time to sleep for each datareader in milliseconds aka 1000milli = 1second



