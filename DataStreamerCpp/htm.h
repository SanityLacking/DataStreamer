#pragma once
#include "pybind11/embed.h" // everything needed for embedding
namespace py = pybind11;


class HTM {


public:
	HTM();

	//convert data to sparse data distribution
	void encodeData();


	void compute();

	//
	void prediction();


	//score the predictions
	void scoring();


private:


};