open_project s2p-array
set_top serial2parallel

add_files ./hls/s2p-array.cpp
add_files ./hls/s2p-array.h
add_files -tb ./hls/event_3_3_3.txt
add_files -tb ./hls/tb-s2p-array.cpp

open_solution "ku15p"
set_part {xcku15p-ffva1760-2-e} -tool vivado
create_clock -period 4.16666667 -name default

config_export -format ip_catalog -rtl vhdl
csim_design -clean
csynth_design
cosim_design -rtl vhdl
export_design -flow syn -rtl vhdl -format ip_catalog
