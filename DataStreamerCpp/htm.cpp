#include"htm.h"


HTM::HTM() {

}

void HTM::encodeData()
{
	py::scoped_interpreter guard{}; // start the interpreter and keep it alive

	py::print("Hello, World!"); // use the Python API
}

