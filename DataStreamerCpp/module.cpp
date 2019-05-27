//#include <Windows.h>
#include <Python.h>
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/embed.h"
#include <cmath>
#include "pybind11/numpy.h"

#include <atomic>
#include <string>
#include <vector>
#include <iostream>
#include <sstream>
#include <thread>
#include <chrono>
#include <mutex>
#include <stdlib.h>     /* srand, rand */
#include <time.h>       /* time */
#include <iostream>
#include <algorithm>
#include <numeric>
#include <iterator>     // std::front_inserter
//#include "ThreadPool.h"

namespace py = pybind11;

const bool DEBUG = false;

/*
int dataRead(std::vector<std::string> &dataset, std::vector<std::string> &inputStack) {
	//take line from dataset and put it on input stack. then sleep
	while (!dataset.empty()) {
		if (!dataset.empty()) { //hack way to make lock guard work as it sticks around until it goes out of scope. will have to look at this section further.
			std::lock_guard<std::mutex> guard(readerMutex);
			inputStack.push_back(dataset.front());
			dataset.erase(dataset.begin());
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(READERINTERVAL)); //portable threaded sleep
	}

	return 0;
}
*/
/*
int threadSum(int & x) {
	//take line from dataset and put it on input stack. then sleep
	int count = 100;
	for (int i = 0; i < count; i++) {
		if (x) {
			std::lock_guard<std::mutex> guard(readerMutex);
			x = x + 2;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(READERINTERVAL)); //portable threaded sleep
	}


	return x;
}
*/

/*
int threadCounter(int & x, int & y) {
	//take line from dataset and put it on input stack. then sleep
	int count = 100;
	for (int i = 0; i < count; i++) {
		if (x) {
			std::lock_guard<std::mutex> guard(readerMutex);
			x = x + y;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(READERINTERVAL)); //portable threaded sleep
	}

	return 0;
}
*/

class datasetStream
{
public:
	datasetStream();
	int sum(int x);
	void startCounter(int x);
	int getCounter();

	int setVRate(std::vector<float>vRate);
	int setVRateScalar(float vRate);
	int setStepRate(float stepRate);
	std::deque<std::vector< std::string> >  getResults(bool clear = false);
	int getResultsCount();
	std::deque<std::vector< std::string> >  getCurrentInput();
	int getCurrentInputCount();
	//int initReaders(int length, const char ** string_list);
	int initReaders(std::vector<std::vector< std::string> >  inputData, std::vector<std::string> labels = std::vector<std::string>(), std::vector<std::vector< std::string> >  X_test = std::vector<std::vector< std::string> >());
	bool checkComplete();
	std::string initReadersDebug(std::vector<std::vector< std::string> >  inputData);
	std::string checkForThreadException();

	 int READERINTERVAL = 100; //time to sleep for each datareader in milliseconds aka 1000milli = 1second
	 int PROCESSINTERVAL = 0; //time to sleep for each processor in milliseconds aka 1000milli = 1second
	 int LOADBALANCEINTERVAL = 100; //time to sleep for each datareader in milliseconds aka 1000milli = 1second
	 int MAXLOAD = 10; //number of waiting items before we need to start doing something about it.
	 int READERCOUNT = 6;
	 const int READERSLIMIT = 10000; 
	 int LBMETHOD = 4; // what load balancing method to use 
							//option 1, basic load shed, remove oldest elements to keep the input stack always below the MAXLOAD Limit.
							//option 2, remove newest elements	
							//option 3 remove newest elements in one go.
							//option 4 no balancer engaged.



private:
	bool starter;
	std::vector<std::vector< std::string> > dataset = {}; //the initial load location of the dataset, does not get changed after it is loaded.
	std::deque<std::vector< std::string> > datasetQueue = {}; //the queue of the initial dataset, passed to the worker threads to be inserted into the input queue sequentially.

	std::vector<std::vector< std::string> > inputStack = {}; //stack for the incoming reads to be placed by the datareader threads	
	std::deque<std::vector< std::string> > inputQueue = {}; //the queue of the input data to be processed. this is separate then the dataset queue to simulate incomming input load.

	std::deque<float> vQueue = {}; //queue for storing the variable rate. if rate is a single scalar, this queue will be of size 1

	std::atomic<bool> JobComplete = false;
	std::atomic<bool> ProcessComplete = false;
	std::vector<std::vector< std::string> > outputStack = {};	 //output stack of all processed elements
	std::deque<std::vector< std::string> > outputQueue = {};	//output queue to be passed back to the calling program

	int n = 5;
	int x1 = 1;
	int y1 = 1;


	py::object processMethod; 
	//static std::exception_ptr globalExceptionPtr;


	//std::mutex readerMutex;
	std::mutex datasetMutex; //very important step, make sure your mutexes are defined inside your class so that your classbased functions can see them.
	std::mutex inputQueueMutex;
	std::mutex outputQueueMutex;
	int dataR(std::vector<std::vector< std::string> >  &dataset); //threaded data reader function
	int dataReader(std::deque<std::vector< std::string> > &dataset, std::deque<std::vector< std::string> > &inputQueue, std::deque<float> vQueue, int threadID);
	std::deque<std::string> inputStackTiming;
	bool pContinue = true;
	int val;
	int processData(py::object processMethod);
	int loadbalance();
};


datasetStream::datasetStream()
{
	//readerPool = new ThreadPool readerPool(4);
	//static std::exception_ptr globalExceptionPtr = nullptr;
	/* Acquire GIL before calling Python code */
	py::gil_scoped_acquire acquire;	
	py::print("C++ Class datasetStream Initialized");

	py::object pyProcessor = py::module::import("pyprocessor").attr("Processor"); // import the module, specifically the class I want
	processMethod = pyProcessor();		// initialize the class 
	if (DEBUG == true) {
		py::object debugPrint = processMethod.attr("debugPrint")(); //run a function from the class
		py::print(py::str(debugPrint));
	}
	py::print("Processing Method Chosen, Knn Initialized");
	py::gil_scoped_release release;

}
/* read in the input data and stores it. Initializes the threaded datareaders. 
	String_List: the input dataset in the form of a list of strings for each row, comma delimited
	labels: the list of labels for string list. 

*/

int datasetStream::initReaders(std::vector<std::vector< std::string> >  input, std::vector<std::string> labels, std::vector<std::vector< std::string> >  X_test)
{
	
	//if X_test and y_test are empty, then only X and y are to be used to init.
	//if they are not empty, input and labels are to be used as the training set and X_test and y_test as the test set.
	
	if (labels.size() > 0  )
		assert(input.size() == labels.size());

	if (!X_test.empty()) { // input and labels are training, X_test is unknown data.
		dataset = input; //set the dataset to process to the passed list.
		py::gil_scoped_acquire acquire;
		processMethod.attr("fit")(input, labels);
		py::gil_scoped_release release;
		copy(X_test.begin(), X_test.end(), std::inserter(datasetQueue, datasetQueue.end())); //copy dataset to queue
	}else { //input and labels are training, X_test and y_test is test data and test labels.
		//TODO fix this up more.
		dataset = input; //set the dataset to process to the passed list.
		py::gil_scoped_acquire acquire;
		try
		{
			processMethod.attr("fit")(input, labels);
		}
		catch (const std::exception&)
		{
			py::print("not able to find function fit for singular training set.");
		}
		
		py::gil_scoped_release release;
		copy(input.begin(), input.end(), std::inserter(datasetQueue, datasetQueue.end())); //copy dataset to queue
	}
	//input and labels are used without a training step. 							// TODO//
	
	//create thread of dataReaders
	//datareaders each take a line of input and put it in the IN pile. 
	// the loadbalancer makes sure the IN pile isn't too big. Load balancer is a separate thread that constantly monitors the IN pile.
	// then then the process data thread takes input from the IN pile and processes it and puts it in the OUT pile.
	// getResults function returns any data that is in the OUT pile to the python caller for them to display.

	// start worker threads to share the dataset queue and move it to the input queue
	for (int i = 1; i <= READERCOUNT; i++) {
		std::thread dataReaderThread(&datasetStream::dataReader, this, std::ref(datasetQueue), std::ref(inputQueue), vQueue, i);
		dataReaderThread.detach();
	}


	// start load balancer
	std::thread loadBalancerThread(&datasetStream::loadbalance, this);
	loadBalancerThread.detach();

	// start processor thread
	std::thread processorThread(&datasetStream::processData, this, processMethod);
	processorThread.detach();

	return (int)dataset.size();
}

inline const char * const BoolToString(bool b)
{
	return b ? "true" : "false";
}

// return bool to check if processing is complete. 
bool datasetStream::checkComplete()
{
	try
	{
		/*bool dsQ;
		bool iQ;
		size_t dsQsize;
		size_t iQsize;*/
		std::cout << "checkComplete" << std::endl;
		
		//std::lock_guard<std::mutex> guard(inputQueueMutex);
			//dsQ = datasetQueue.empty();
			//iQ = inputQueue.empty();
			//dsQsize = datasetQueue.size();
			//iQsize = inputQueue.size();


		// If empty() is thread safe, checking empty first, locking, and then rechecking may avoid an unnecessary lock. 
		

		if (datasetQueue.empty() && inputQueue.empty() && ProcessComplete) {
			JobComplete = true;
			py::gil_scoped_acquire acquire;
			py::print("dsQueue: " + std::to_string(datasetQueue.size()) + ", inputQueue: " + std::to_string(inputQueue.size()) + ", ProcessComplete: " + BoolToString(ProcessComplete));
			py::print("job finished");
			py::gil_scoped_acquire release;
		}
		else {
			py::gil_scoped_acquire acquire;
			py::print("dsQueue: " + std::to_string(datasetQueue.size()) + ", inputQueue: " + std::to_string(inputQueue.size()) + ", ProcessComplete: " + BoolToString(ProcessComplete));
			py::gil_scoped_acquire release;
			JobComplete = false;
		}
	}
	catch (const std::exception& e)
	{
		std::cout << "error" << std::endl;
		py::gil_scoped_acquire acquire;
		py::print(e.what());
		py::gil_scoped_acquire release;
	}
	std::cout <<"JobComplete: "<< BoolToString(JobComplete) << std::endl;
	return JobComplete;
}
// does exactly the same thing as InitReaders, but returns the char *  for debugging. DEPRECATED
std::string  datasetStream::initReadersDebug(std::vector<std::vector< std::string> >  string_list) {
	try
	{
		//std::thread thread2(threadCounter, std::ref(x1), std::ref(y1));
		std::this_thread::sleep_for(std::chrono::milliseconds(READERINTERVAL)); //portable threaded sleep 	
		//thread2.join();
	}
	catch (const std::exception& ex)
	{
		return ex.what();
	}

	int result = initReaders(string_list);
	return "everything is fine";
}

//simple function to test the class is working TEST FUNCTION
int datasetStream::sum(int n)
{
	//outputStack.push_back("changed");
	return n + n;
}
void datasetStream::startCounter(int x)
{
	val = x;
	for (int i = 0; i < READERCOUNT; i++) {
		//std::thread thread1(threadSum, std::ref(val));
		//thread1.detach();
	}
}

//set the VRate
int datasetStream::setVRate(std::vector<float> vRate)
{	
	vQueue = std::deque<float>(vRate.begin(),vRate.end());
	int it = *std::max_element(std::begin(vRate), std::end(vRate));	
	READERCOUNT = it;
	py::gil_scoped_acquire acquire;
	py::print("vQueue:");
	py::print(vQueue);
	py::gil_scoped_acquire release;
	return 0;
}

//set the VRate
int datasetStream::setVRateScalar(float vRate)
{
	// first try, create one thread per amount you want to process
	if (vRate > READERSLIMIT) {
		vRate = READERSLIMIT;
		py::gil_scoped_acquire acquire;
		py::print("vRate cannot exceed READERSLIMIT of "+std::to_string(READERSLIMIT)+". vRate capped to limit.");
		py::gil_scoped_acquire release;
	}
	else if (vRate <= 0) {
		vRate = 0;
		py::gil_scoped_acquire acquire;
		py::print("vRate shouldn't be lower or equal to zero. this will stall your program indefinitiely.");
		py::gil_scoped_acquire release;
	}
	vQueue.empty();
	vQueue.push_back(vRate);
	READERCOUNT = vRate;
	return 0;
}

//set the step rate
int datasetStream::setStepRate(float stepRate)
{
	if (stepRate <= 0) {
		stepRate = 0;
		py::gil_scoped_acquire acquire;
		py::print("Step Rate is equal to or less then zero, this can cause unexpected behavouir. You have been warned.");
		py::gil_scoped_acquire release;
	}
	READERINTERVAL = stepRate;
	return 0;
}
//int datasetStream::getCounter()
//{
//	std::lock_guard<std::mutex> guard(readerMutex);
//	int x = val;
//	return x;
//}
/* Get current results that have been processed. if clear is true, will remove all sent results and empty the results vector.
*/
std::deque<std::vector< std::string> > datasetStream::getResults(bool clear)
{

	std::deque<std::vector< std::string> > results;
	if (true) {
		// TODO mutex guard. is this a shallow or hard copy? i think its a hard copy
		std::lock_guard<std::mutex> guard(outputQueueMutex);
		results = outputQueue;
		if (clear) {
			outputQueue.clear();
		}
	}
	return results;
}
int datasetStream::getResultsCount()
{
	int result = -1;
	{
		std::lock_guard<std::mutex> guard(outputQueueMutex);
		result = outputQueue.size();
		//result = 1;
	}
	return result;
}


int datasetStream::getCurrentInputCount()
{
	int result = -1;
	{
		std::lock_guard<std::mutex> guard(inputQueueMutex);
		result = inputQueue.size();
		//result = 1;
	}
	return result;
}
std::deque<std::vector< std::string> > datasetStream::getCurrentInput()
{
	std::deque<std::vector< std::string> > results = {};
	{
		std::lock_guard<std::mutex> guard(inputQueueMutex);
		results = inputQueue;
	}
	return results;
}


int datasetStream::processData(py::object processMethod) {
	
	std::vector< std::string> row;
	py::gil_scoped_acquire acquire;
	py::print("process thread");
	//py::object pyProcessor = py::module::import("pyprocessor").attr("Processor"); // import the module, specifically the class I want
	//py::object Processor = pyProcessor();		// initialize the class 
	if(DEBUG==true){
		py::object debugPrint = processMethod.attr("threadCheck")(); //run a function from the class
		py::print(py::str(debugPrint)); 
	}	

	py::print("Processing Thread Initialized");
	py::gil_scoped_release release;
	while (!JobComplete) { //TODO, come up with a better loop check for this.		
		try	{
			//py::gil_scoped_acquire();
			auto start = std::chrono::steady_clock::now();
			row.clear();
			//check for input rows to process
			{
				std::lock_guard<std::mutex> guard(inputQueueMutex);
				if (!inputQueue.empty()) {
					py::gil_scoped_acquire acquire;
						py::print("inputQueueSize: "+ std::to_string(inputQueue.size()));						
					py::gil_scoped_acquire release;
					row = inputQueue.front();
					inputQueue.pop_front();
				}
			}
			if (!row.empty()) {
				ProcessComplete = false;				
				// get the start time that the row was passed to input queue from end of row and drop time from row for processing.
				//Convert signed integral type to time_point
				auto timeStart = std::stoll(row.back());
				row.pop_back(); //TODO, make this optional to record the start time?
				std::chrono::time_point<std::chrono::steady_clock, std::chrono::milliseconds> dt{ std::chrono::milliseconds{timeStart} };

				py::gil_scoped_acquire acquire;
				if (DEBUG == true)
					py::print("Processing Thread Active");
				py::object output = processMethod.attr("process")(row);

				if (DEBUG == true)
					py::print(output);
				std::string res = output.cast<std::string>();
				py::gil_scoped_release release;
				
				std::vector< std::string> result;
				result.push_back(res);
				auto end = std::chrono::steady_clock::now();

				//std::vector< std::string> result = row;			
				//result.push_back(end);
				result.push_back(std::to_string(std::chrono::duration_cast<std::chrono::microseconds>(end - start).count())); //process time
				result.push_back(std::to_string(std::chrono::duration_cast<std::chrono::microseconds>(end - dt).count())); //time from input to process finished
				{
					std::lock_guard<std::mutex> guard(outputQueueMutex);
					outputQueue.push_back(result);
				}
			}
			else {
				/*py::gil_scoped_acquire acquire;
				py::print("row empty");
				py::gil_scoped_acquire release;*/
			}
			ProcessComplete = true;
			std::this_thread::sleep_for(std::chrono::milliseconds(PROCESSINTERVAL)); //portable threaded sleep 	
		}
		catch (const std::exception& e)
		{
			py::gil_scoped_acquire acquire;
			py::print("processData encountered an Error:");
			py::print(e.what());
			py::gil_scoped_acquire release;
		}
		
	}
	return 0;
}

// worker thread that handles the input load on the processor.


// TODO make this function take a pointer argument so it could be run using a different stack rather then the class variable.
int datasetStream::loadbalance() {
	{
		std::lock_guard<std::mutex> guard(inputQueueMutex); //lock is done here to encompass the size check.
		if (inputQueue.size() < MAXLOAD) {
			switch (LBMETHOD)
			{
			case 1: {
				//option one, basic load shed, remove oldest elements to keep the input stack always below the MAXLOAD Limit.
				//std::vector<string>(inputStack.end()-MAXLOAD, inputStack.end()).swap(inputStack);
				inputQueue.erase(inputQueue.begin(), (inputQueue.end() - MAXLOAD) - 1);
				break;
			}case 2: {
				//option two, remove newest elements
				//std::lock_guard<std::mutex> guard(inputQueueMutex);
				while (inputQueue.size() > MAXLOAD) {
					inputQueue.pop_back();
				}
				break;
			}case 3: { //option two.2 remove newest elements in one go.
				//std::lock_guard<std::mutex> guard(inputQueueMutex);
				inputQueue.resize(MAXLOAD);
				break;
			}case 4: {
				//no balancer engaged.
				break;
			}default:
				break;
			}
		}
	}
	return 0;
}

std::string datasetStream::checkForThreadException()
{
	/*if (globalExceptionPtr)
	{
		try
		{
			std::rethrow_exception(globalExceptionPtr);
		}
		catch (const std::exception &ex)
		{
			std::string output(ex.what());
			return output;
		}
	}*/
	return std::string();
}

// Implementation of worker threads using queues
int datasetStream::dataReader(std::deque<std::vector< std::string> > &dataset, std::deque<std::vector< std::string> > &inputQueue, std::deque<float> vQueue, int threadID){
	//take line from dataset and put it on input stack. then sleep
	int vRate = 0;
	try
	{
		std::vector< std::string> row;
		while (!dataset.empty()){			
				try{
					//get val from vQueue, if vQueue size is equal to 1, don't pop_front else pop_front
					// this means that once the queue is down to one value left, it will remain that way until the processing is finished.
					vRate = vQueue.front();
					/*std::string str("vRate:");
					str = str + std::to_string(vRate);
					py::gil_scoped_acquire acquire;
					py::print(str);
					py::gil_scoped_acquire release;*/
					if (vQueue.size() > 1) {
						vQueue.pop_front();
					}

					//if val > threadID for this step, read input.
					if (vRate >= threadID) {
						/*py::gil_scoped_acquire acquire;
						py::print("threadProcessing: " + std::to_string(threadID));
						py::print(vQueue);
						py::gil_scoped_acquire release;*/
						std::cout << threadID << std::endl;
						row.clear();
						std::lock_guard<std::mutex> guard(inputQueueMutex);
						if(!dataset.empty()) //double check that dataset is valid
							row = dataset.front(); 
						else {                 //else skip to the loop end.     
							py::gil_scoped_acquire acquire;
							py::print("thread not processing: " + std::to_string(threadID) + " pre-emptive finish.");
							py::gil_scoped_acquire release;
							continue;
						}
						auto now = std::chrono::time_point_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now());
						// Convert time_point to signed integral type
						auto integral_duration = now.time_since_epoch().count();
						row.push_back(std::to_string(integral_duration));
						inputQueue.push_back(row);
						dataset.pop_front();
					}
					else {
						py::gil_scoped_acquire acquire;
						py::print("thread not processing: " + std::to_string(threadID)+" because VR = "+std::to_string(vRate));
						py::gil_scoped_acquire release;
					}
					//else do not read input, instead sleep till next step.
				}
				catch (const std::exception& e){
					py::gil_scoped_acquire acquire;
					py::print("dataReader Encountered Error:");
					py::print(e.what());
					py::gil_scoped_acquire release;
				}		
			std::this_thread::sleep_for(std::chrono::milliseconds(READERINTERVAL)); //portable threaded sleep 		
		}
		//std::cout << "DataReader complete: " << std::to_string(threadID) << std::endl;
		/*py::gil_scoped_acquire acquire;
		py::print("DataReader complete:" + std::to_string(threadID));
		py::gil_scoped_acquire release;*/
	}
	catch (const std::exception& b)
	{
		py::gil_scoped_acquire acquire;
		py::print("error!: threadID: " + std::to_string(threadID));
		py::print(b.what());
		py::gil_scoped_acquire release;
	}

	
	return 0;
}
// Implementation of worker threads using vectors. Currently not used in favour of using deques.
int datasetStream::dataR(std::vector<std::vector< std::string> >  &dataset) {
	//take line from dataset and put it on input stack. then sleep
	while (!dataset.empty())
	{
		{
			std::lock_guard<std::mutex> guard(inputQueueMutex);
			inputStack.push_back(dataset.front());
			dataset.erase(dataset.begin());
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(READERINTERVAL)); //portable threaded sleep 		
	}
	return 0;
}







PYBIND11_MODULE(DataStreamerCpp, m) {
	py::class_<datasetStream>(m, "dsStream")
		.def(py::init())
		.def("setStepRate", &datasetStream::setStepRate, "set the step rate")
		.def("setVRate", &datasetStream::setVRate, "set the variable rate")
		.def("setVRateScalar", &datasetStream::setVRateScalar, "set the variable Rate with a scalar")
		//.def("setStepRate", &datasetStream::setStepRate, "set the step rate")
		.def("sum", &datasetStream::sum, "sum to check its working")
		.def("startCounter", &datasetStream::startCounter, "thread Start")
		.def("getResults", &datasetStream::getResults, "get the results", py::arg("clear") = false)
		.def("getResultsCount", &datasetStream::getResultsCount, "get the results count")

		.def("getCurrentInput", &datasetStream::getCurrentInput)
		.def("getCurrentInputCount", &datasetStream::getCurrentInputCount)
		.def("initReaders", &datasetStream::initReaders, "", py::arg(), py::arg("labels") = std::vector<std::string>(), py::arg("X_test") = std::vector<std::vector< std::string> >())
		.def("initReadersDebug", &datasetStream::initReadersDebug)
		.def("checkComplete", &datasetStream::checkComplete, "check if the process is complete")
		.def("checkForThreadException", &datasetStream::checkForThreadException);

	
#ifdef VERSION_INFO
	m.attr("__version__") = VERSION_INFO;
#else
	m.attr("__version__") = "dev";
#endif
}