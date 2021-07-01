#include "s2p-array.h"
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include "ap_int.h"
#include "ap_fixed.h"
#include <math.h>
#include <bitset>
#include <iomanip>
#include <cassert>

typedef unsigned long long ull_t;

static const unsigned int W = 16;
static const unsigned int I = 6;
//typedef ap_fixed<W,I> ldata_t;
//typedef float ldata_t;
typedef ap_uint<W> ldata_int_t;


/*
 * Unpack a fixed-point representation <W_, I_> value from a hex string.
 * This is irrelevant at the hardware level, since the W_-bit string
 * will be interpreted as a <W_, I_> fixed-point value, but to be able
 * to view it at the software level we need to shift the binary point
 * to go from an integer representation of W_ bits, to a <W_, I_>
 * representation.
 * */
template<unsigned int W_, unsigned int I_>
ap_fixed<W_, I_> hexWordConverter(std::string hexWord){

	const unsigned int fracWidth = W_ - I_;

	// Create bit mask
	ull_t mask = 0;
	for ( int i = 0; i <= W_; i++ ){
		mask ^= 1 << i;
	}

	// Translate entire 64-bit word from a link
	ull_t word;
	word = std::stoull(hexWord, nullptr, 0);

	// Only want the bottom W_ bits
	word &= mask;

	// Somewhere to hold the data temporarily - this is the maximum size
	// needed to unpack fixed-point values from the 64-bit word, I think...
	// At this point, temp is essentially still an integer of W_ bits.
	ap_fixed<128,64> temp = word;

	// Unpack the desired fixed-point value and cast
	// as required
	ap_fixed<W_, I_> ret = (temp >> fracWidth);

	return ret;

}



void parsePatternFile( std::string path, std::vector<std::string>& out){

	std::ifstream fs(path);

	// Ignore first 3 lines of pattern file
	std::string dummy;
	std::getline(fs, dummy);
	std::getline(fs, dummy);
	std::getline(fs, dummy);

	while( fs ){

		std::string frame;
		std::getline(fs, frame);

		std::istringstream frameStream(frame);

		// Ignore frame number
		std::getline(frameStream, dummy, ' ');
		std::getline(frameStream, dummy, ' ');
		std::getline(frameStream, dummy, ' ');

		std::string link;
		while ( std::getline(frameStream, link, ' ') ){

			// Form hex string, ignoring valid bit
			std::string hexVal;
			hexVal += "0x";
			for ( int i = 2; i < 18; i++ ) hexVal.push_back(link[i]);

			out.push_back(hexVal);

		}

	}

}






int main(){


	// Check tb is working by converting some floats
	// to fixed-point repr by shifting binary point and
	// keeping integer bits only. Then pack as hex string
	// as would be done for links in pattern file.
	std::cout << "Check TB is functioning correctly:\n";
	for ( float v = 0; v < 0.1; v+=0.01 ){

		const unsigned int F = W - I;
		ull_t temp = v * std::pow(2, F);

		std::cout << "FLP value: " << std::setw(5) << v;
		std::cout << "    <" << W << "," << I << ">" << " value to pack: " << std::setw(11) << std::internal
				 << static_cast<T>(v);
		std::cout << "    Hex: ";

		std::stringstream ss;
		ss << "0x" << std::setfill('0') << std::setw(sizeof(ull_t)*2) << std::hex << temp;
		std::cout << ss.str();

		std::cout << "    Unpacked <" << W << "," << I << "> value: "
					<< hexWordConverter<W,I>(ss.str()) << "\n";

	}
	std::cout << "\n";


	// Parse a pattern file, outputting the binary string reprs,
	// and corresponding fixed-point-interpreted values.
	std::vector<std::string> hexStringBuffer;
	parsePatternFile("event_3_3_3.txt", hexStringBuffer);

	for ( std::string val : hexStringBuffer ){

		std::cout << "Hex string: " << val << "   Bitstring: ";
		std::bitset<sizeof(ull_t)*8> bWord( std::stoull(val, nullptr, 0) );
		std::cout << bWord << "   ";
		std::cout << "<" << W << "," << I << "> value: " << hexWordConverter<W,I>(val) << "\n";

	}


	// Push link data to link streams
	std::cout << "Pushing " << N_OUT << " elements to input FIFOs.\n";
//	hls::stream<T> in[N_IN];
	T comp[N_OUT];
	T in[N_OUT];
	T out[N_OUT];
	std::cout << "\nFrame " <<
						std::setw(4) << std::setfill('0') <<
						std::internal << 0 << "  ";
	for ( size_t i = 0; (i < N_OUT) && (i < hexStringBuffer.size()); i++){

//		in[i%N_IN].write(hexWordConverter<W,I>( hexStringBuffer.at(i) ));
		in[i] = hexWordConverter<W,I>( hexStringBuffer.at(i) );
		comp[i] = hexWordConverter<W,I>( hexStringBuffer.at(i) );

		std::cout << std::setw(10) << std::setfill(' ') << in[i] << " ";
		if ( ((i+1)%N_IN == 0) && (i != N_OUT - 1) ){
			std::cout << "\nFrame " <<
					std::setw(4) << std::setfill('0') <<
					std::internal << i / N_IN + 1<< "  ";
		}

	}

	serial2parallel(in, out);


	std::cout << "\nFrame " <<
							std::setw(4) << std::setfill('0') <<
							std::internal << 0 << "  ";
	int counter = 0;
	for ( size_t i = 0; i < N_OUT; i++ ){

		std::cout << std::setw(10) << std::setfill(' ') << out[i] << " ";
		if ( ((i+1)%N_IN == 0) && (i != N_OUT - 1) ){
					std::cout << "\nFrame " <<
							std::setw(4) << std::setfill('0') <<
							std::internal << i / N_IN + 1 << "  ";
		}

		if ( comp[i] != out[i] ){
			int link = i % N_IN;
			int frame = i / N_IN;
			std::cout << "Input and output elements differ at: Frame=" + std::to_string(frame)
									+ ", Link=" + std::to_string(frame);


		}
		assert(comp[i] == out[i] && "Data mismatch.");

		counter++;

	}
	std::cout << "\n\nOutput buffer contains " << counter << " elements.\n\n";
	assert(counter == N_OUT && "Output buffer does not contain all data from input streams.");

	std::cout << "** Test bench passed. Output buffer contains correct elements. **\n\n";


}
