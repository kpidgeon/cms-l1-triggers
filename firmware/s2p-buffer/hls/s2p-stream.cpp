#include "s2p-stream.h"
#include <iostream>

void serial2parallel( hls::stream<T> in[N_IN], hls::stream<T> out[N_OUT] ){
        #pragma HLS pipeline
		//#pragma HLS interface ap_none port=out
		//#pragma HLS interface ap_ctrl_none port=return
        #pragma HLS stream variable=in depth=FRAMES
		//#pragma HLS array_reshape variable=out complete
        #pragma HLS array_partition variable=in
        #pragma HLS array_partition variable=out

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

				in[j].read(tmp[i*N_IN + j]);

			}

		}

		OutputWriteLoop:
		for(int i = 0; i < N_OUT; i++){
			#pragma HLS unroll
			out[i].write(tmp[i]);
        }
}
