#include "s2p-array.h"
#include <iostream>

void serial2parallel( T in[N_OUT], T out[N_OUT] ){
        #pragma HLS pipeline
		#pragma HLS interface ap_none port=out
		#pragma HLS interface ap_fifo port=in
//        #pragma HLS stream variable=in depth=FRAMES
		#pragma HLS array_reshape variable=out complete
        #pragma HLS array_partition variable=in cyclic factor=N_IN

//        #pragma HLS array_partition variable=out

        T tmp[N_OUT];
        #pragma HLS array_partition variable=tmp

        SerialLoop:
		for(int i = 0; i < FRAMES; i++){

			ParallelLoop:
			for(int j = 0; j < N_IN; j++){
				#pragma HLS unroll

				#ifndef __SYNTHESIS__
					std::cout << "Reading frame " << i << " from link " << j << "\n";
				#endif

//				in[j].read(tmp[i*N_IN + j]);
				tmp[i*N_IN + j] = in[i*N_IN + j];

			}

		}

		OutputWriteLoop:
		for(int i = 0; i < N_OUT; i++){
			#pragma HLS unroll
			out[i] = tmp[i];
        }
}
