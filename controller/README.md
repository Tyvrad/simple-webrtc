# Controller
This directory contains different scripts to be used at the control pc

## Parser
'webrtc_dump_parser/' contains a parser for the dumps generated by the measurement script.
Place the directories in the 'logs/' dir and run the parser. Output is generated in 'parsed/'

## Plotter
'webrtc_dump_plotter/' contains a small plotting utility. Refer to the README.md file for additional information.

## Measurement Script
'webrtc_measurement_script/' contains a simple measurement script.
Inside the file, specify the path to your ssh id_rsa and the ips of the clients.
Also, you can define the measurement bandwidths, number of iterations as well as the measurement duration.
After each iteration, data is collected and placed in the directory '~/webrtc-logs'
