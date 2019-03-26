import shutil

def move_results_complete():
    print("Copying files...")
    shutil.rmtree('../webrtc_dump_plotter/logs/complete_measurement/')
    shutil.copytree('../webrtc_dump_parser/parsed/', '../webrtc_dump_plotter/logs/complete_measurement/')
    print("Files copied...")