#pragma once

#include "ap_int.h"
#include "ap_fixed.h"
#include "hls_stream.h"

//typedef ap_int<16> T;
typedef ap_fixed<16,6> T;

static const int N_IN = 72; // links
static const int N_OUT = 576; // buffered input elements of type T
static const int FRAMES = N_OUT / N_IN;

void serial2parallel( T in[N_IN] , T out[N_OUT] );
