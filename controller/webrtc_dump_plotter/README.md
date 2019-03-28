# WebRTC plotter

Small plotting utility for WebRTC logfiles parsed by the webrtc_dump_parser.
Contains sample data.

## complete_measurement
If the directory structure of the GitHub repository is preserved, running the dump parser will place the parsed files in the 'logs/complete_measurement' subdirectory.

Then, by running webrtc_plotter.py a series of plots is created. In the directory 'plots/complete_measurement/'.

## single_session
A second option is to modify webrtc_plotter.py and uncommenting line 6. This will create plots for a single measurement. The data for this plots must be placed in the directory 'logs/single_session'.
Suitable data can be copied from 'logs/complete_measurement/bw_XY/pick_any_folder/'. Simply copy the contents of the folder (4 or 5 elements) to the 'logs/single_session' directory.
Plots for single measurements are placed directly in 'plots/'.
