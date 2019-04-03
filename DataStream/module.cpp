//#include <Windows.h>
#include <Python.h>
#include "pybind11/pybind11.h"
#include <cmath>

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

const int MAXLOAD = 10; //number of waiting items before we need to start doing something about it.
const int MAXREADERS = 2;
const int LBMETHOD = 3; // what load balancing method to use


std::mutex readerMutex;
int milisec = 100;
struct timespec req = { milisec / 1000, milisec % 1000 * 1000000L };
const int READERINTERVAL = 100; //time to sleep for each datareader in milliseconds aka 1000milli = 1second
const double e = 2.7182818284590452353602874713527;




double sinh_impl(double x) {
	return (1 - pow(e, (-2 * x))) / (2 * pow(e, -x));
}

double cosh_impl(double x) {
	return (1 + pow(e, (-2 * x))) / (2 * pow(e, -x));
}

double tanh_impl(double x) {
	return sinh_impl(x) / cosh_impl(x);
}


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

class datasetStream
{
public:
	datasetStream();
	int sum(int);
	char *  getResults();
	char *  getCurrentInput();
	int getCurrentInputCount();
	//int initReaders(int length, const char ** string_list);
	int initReaders(const char *  string);
	const char * initReadersDebug(char *  string);
	std::vector<std::string> inputStack; //stack for the incoming reads to be placed by the datareader threads	
	std::vector<std::string> outputStack = {};
	int n = 5;
	int x1 = 1;
	int y1 = 1;
	void __delete__();
private:
	int val;
	//int processData(std::vector<std::string>&inputStack, std::vector<std::string>&outputStack, KNN &knn);
	int loadbalance(std::vector<std::string> &inputStack);

};


datasetStream::datasetStream()
{
}
/* read in the input data and stores it. Initializes the threaded datareaders. */
int datasetStream::initReaders(const char *  string_list) {



	std::string ab = std::string() + string_list;
	std::vector<std::string> tokens;
	std::string token;
	std::istringstream tokenStream(ab);

	while (std::getline(tokenStream, token))
	{
		tokens.push_back(token);
	}

	outputStack.insert(outputStack.end(), tokens.begin(), tokens.end());

	//convert list of strings into vector of vectors
	int count = tokens.size();
	//KNN knn;
	//std::vector<std::string> files(string_list, string_list + length);
	//std::vector<string>trainingSet = knn.getTrainingSet(tokens);
	//knn.initKnn(trainingSet);


	//std::vector<std::string> inputStack; //stack for the incoming reads to be placed by the datareader threads	
	//create thread of dataReaders
	//datareaders each take a line of input and put it in the IN pile. 
	// the loadbalancer makes sure the IN pile isn't too big. Load balancer is a separate thread that constantly monitors the IN pile.
	// then then the process data thread takes input from the IN pile and processes it and puts it in the OUT pile.
	// getResults function returns any data that is in the OUT pile to the python caller for them to display.



	//std::thread threadS(threadSum, std::ref(x1), std::ref(y1));
	/*while (x1 < 100) {
		cout << x1 << endl;
	}
*/

//for(int i = 0; i < MAXREADERS; i++){
	//std::thread dataReader(dataRead, std::ref(tokens), std::ref(inputStack));
	//int x1, y1 = 1;
	//std::thread threadSum(threadSum, std::ref(x1), std::ref(y1));
//}


//load balance
	loadbalance(inputStack);

	//process		
	//processData(inputStack, outputStack, knn);


	/*istringstream iss(string_list);
	while (std::getline(getline(ss, item, ','))
	{
		m_vecFields.push_back(item);
	}*/

	return (int)outputStack.size();
}
/* does exactly the same thing as InitReaders, but returns the char *  for debugging.*/
const char * datasetStream::initReadersDebug(char *  string_list) {
	try
	{
		std::thread thread2(threadCounter, std::ref(x1), std::ref(y1));
		std::this_thread::sleep_for(std::chrono::milliseconds(READERINTERVAL)); //portable threaded sleep 	
		//thread2.join();
	}
	catch (const std::exception& ex)
	{
		return ex.what();
	}

	int result = initReaders(string_list);
	return string_list;
}

//simple function to test the class is working
int datasetStream::sum(int n)
{
	outputStack.push_back("changed");
	return n + n;
}
char * datasetStream::getResults()
{
	//const char * chr = "Empty Results";
	if (!outputStack.empty()) {
		std::string a = std::accumulate(outputStack.begin(), outputStack.end(), std::string(""), [](std::string &ss, std::string &s)
		{
			return ss.empty() ? s : ss + "" + s;
		});

		char *cstr = &a[0u];
		return cstr;
	}
	else {
		return nullptr;
	}
	//char *cstr = (char*)chr;
	//return cstr;	
}

int datasetStream::getCurrentInputCount()
{
	return x1;
}
char * datasetStream::getCurrentInput()
{
	//const char * chr = "Empty Results";
	if (!inputStack.empty()) {
		std::string a = std::accumulate(inputStack.begin(), inputStack.end(), std::string(""), [](std::string &ss, std::string &s)
		{
			return ss.empty() ? s : ss + "" + s;
		});

		char *cstr = &a[0u];
		return cstr;
	}
	else {
		return nullptr;
	}
}
/*
int datasetStream::processData(std::vector<std::string>&inputStack, std::vector<std::string>&outputStack, KNN &knn) {
	std::string row;
	while (true) {
		//check for input rows to process

		if (!inputStack.empty()) {
			row.clear();
			std::lock_guard<std::mutex> guard(readerMutex); //if  i use the reque data type i don't need a lock here i think.
			row = inputStack.back();
			inputStack.pop_back();
		}
		if (!row.empty()) {
			//do some processing
			double result = knn.KNNprocess(row);
			//put results in the outputStack
			outputStack.push_back(std::to_string(result));
		}

	}
	return 0;
}
*/
int datasetStream::loadbalance(std::vector<std::string> &inputStack) {
	if (inputStack.size() < MAXLOAD) {
		switch (LBMETHOD)
		{
		case 1:
			//option one, basic load shed, remove oldest elements
			//std::vector<string>(inputStack.end()-MAXLOAD, inputStack.end()).swap(inputStack);
			inputStack.erase(inputStack.begin(), (inputStack.end() - MAXLOAD) - 1);
			break;
		case 2:
			//option two, remove newest elements
			while (inputStack.size() > MAXLOAD) {
				inputStack.pop_back();
			}
			break;
		case 3: //option two.2 remove newest elements in one go.
			inputStack.resize(MAXLOAD);
			break;

		default:
			break;
		}
	}
	return 0;
}




//
//	Make the functions available for the python file to read.
//

namespace py = pybind11;

PYBIND11_MODULE(DatasetStream, m) {
	py::class_<datasetStream>(m, "dsStream")
		.def(py::init())
		.def("sum", &datasetStream::sum, "sum to check its working")
		.def("getResults", &datasetStream::getResults,"get the results")
		.def("getCurrentInput", &datasetStream::getCurrentInput)
		.def("initReaders", &datasetStream::initReaders)
		.def("initReadersDebug", &datasetStream::initReadersDebug);
	
	m.def("fast_tanh2", &tanh_impl, R"pbdoc(
        Compute a hyperbolic tangent of a single argument expressed in radians.
    )pbdoc");

#ifdef VERSION_INFO
	m.attr("__version__") = VERSION_INFO;
#else
	m.attr("__version__") = "dev";
#endif
}