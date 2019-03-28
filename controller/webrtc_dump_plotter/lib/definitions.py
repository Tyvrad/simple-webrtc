import os
from pathlib import Path

__all__ = ["PATH_OUTPUT", "PATH_DATA_SINGLE", "PATH_DATA_COMPLETE", "PATH_OUTPUT_COMPLETE_MULTIPLE",
           "PATH_OUTPUT_COMPLETE", "PATH_OUTPUT_COMPLETE_CDF", "dict_lookup"]

PATH_OUTPUT = Path("/home/christian/masterarbeit/messungen/webrtc_dump_plotter/plots/")
PATH_OUTPUT_SINGLE = PATH_OUTPUT / "single_session/"
PATH_OUTPUT_COMPLETE = PATH_OUTPUT / "complete_measurement/"
PATH_OUTPUT_COMPLETE_CDF = PATH_OUTPUT_COMPLETE / "cdf/"
PATH_OUTPUT_COMPLETE_MULTIPLE = PATH_OUTPUT_COMPLETE / "multiple/"

PATH_DATA = Path("/home/christian/masterarbeit/messungen/webrtc_dump_plotter/logs/")
PATH_DATA_SINGLE = PATH_DATA / "single_session/"
PATH_DATA_COMPLETE = PATH_DATA / "complete_measurement/"

dict_lookup = {
    "audio_bitsReceivedPerSecond":                  "Average Bits Recv. per Second",
    "audio_bitsSentPerSecond":                      "Average Bits Sent per Second",
    "audio_googRtt":                                "RTT (ms)",
    "audio_packetsSentPerSecond":                   "Total Packets sent per Second",
    "bweforvideo-googAvailableReceiveBandwidth":    "Bandwidth Estimation Receive (kbit/s)",
    "bweforvideo-googAvailableSendBandwidth":       "Bandwidth Estimation Send (kbit/s)",
    "bweforvideo-googBucketDelay":                  "Video Codec Bucket Delay (ms)",
    # Make sure to transform the data to kbits when using the data
    "audio_recv_bitsReceivedPerSecond":             "Bitrate Recv. Audio (kbit/s)",
    "video_recv_bitsReceivedPerSecond":             "Bitrate Recv. Video (kbit/s)",
    "audio_recv_googCurrentDelayMs":                "Delay Audio (ms)",
    "video_recv_googCurrentDelayMs":                "Delay Video (ms)",
    "video_recv_googDecodeMs":                      "Video Decode Time (ms)",
    "video_recv_googFrameHeightReceived":           "Recv. Frame Height (px)",
    "video_recv_googFrameRateReceived":             "Recv. Frames per Second",
    "video_recv_googFrameRateOutput":               "Output Frames per Second",
    "video_recv_googFrameWidthReceived":            "Recv. Frame Width (px)",
    "video_recv_googInterframeDelayMax":            "Recv. Inteframe Delay Max (ms)",
    "audio_recv_googJitterBufferMs":                "Recv. Jitter Buffer Audio (ms)",
    "video_recv_googJitterBufferMs":                "Recv. Jitter Buffer Video (ms)",
    "audio_recv_googJitterReceived":                "Recv. Jitter Audio (ms)",
    "video_recv_googPlisSent":                      "Recv. Picture Loss Index",
    "audio_recv_googPreferredJitterBufferMs":       "Preferred Recv. Jitter Buffer Audio (ms)",
    "audio_recv_packetsReceivedPerSecond":          "Packets Recv. Per Second Audio",
    "audio_send_packetsSentPerSecond":              "Packets Sent Per Second Audio",
    "video_recv_packetsReceivedPerSecond":          "Packets Recv. Per Second Video",
    "video_send_packetsSentPerSecond":              "Packets Sent Per Second Video",
    "video_recv_resolutionChangesReceived":         "Resolution Changes Received",
    # Make sure to transform the data to kbits when using the data
    "audio_send_bitsSentPerSecond":                 "Bitrate Sent Audio (kbit/s)",
    "video_send_bitsSentPerSecond":                 "Bitrate Sent Video (kbit/s)",
    "video_send_googEncodeUsagePercent":            "CPU Usage (%)",
    "video_send_googFrameHeightSent":               "Sent Frame Height (px)",
    "video_send_googFrameRateSent":                 "Sent Frames per Second",
    "video_send_googFrameWidthSent":                "Sent Frame Width (px)",
    "audio_send_googJitterReceived":                "Recv. Jitter Buffer (ms)",
    "audio_send_googRtt":                           "Sent Audio RTT",
    "video_send_googRtt":                           "Sent Video RTT",
    "audio_send_packetsLost":                       "Sent Audio Packets Lost",
    "video_send_packetsLost":                       "Sent Video Packets lost",
    "video_send_resolutionChangesSent":             "Resolution Changes Sent",
    "timestamp":                                    "Timestamp",
    "video_bitsReceivedPerSecond":                  "Video Stream Bits Recv. Per Second",
    "video_bitsSentPerSecond":                      "Video Stream Bits Sent Per Second",
    "video_packetsSentPerSecond":                   "Video Stream Packets Sent Per Second",
    "video_googRtt":                                "Video RTT",
    "meta_audio_send_add":                          "Audio synchronity sent added",
    "meta_audio_send_mul":                          "Audio synchronity sent multiplied",
    "meta_audio_recv_add":                          "Audio synchronity recv added",
    "meta_audio_recv_mul":                          "Audio synchronity recv multiplied",
    # Utility
    "1_way_delay_audio_send":                       "Audio One-Way Delay (ms)",
    "ear_ear_delay_audio_send":                     "Audio Mounth-Ear Delay (ms)",
    "eye_eye_delay_video_send":                     "Video Eye-Eye Delay (ms)",
    "audio_recv_kbitsReceivedPerSecond":            "Bitrate Recv. Audio (kbit/s)",
    "video_recv_kbitsReceivedPerSecond":            "Bitrate Recv. Video (kbit/s)",
    "audio_packet_loss_percentage_send":            "Audio Send Packet Loss (%)",

    # KPI Audiosync
    "e_model_audio_send":                           "E-Model Audio R-factor",
    "kpi_audio_synchronization":                    r"$KPI_{audiosync}$",

    # KPI Videosync
    "1_way_delay_video_send":                       "Video One-Way Delay (ms)",
    "kpi_video_synchronization":                    r"$KPI_{videosync}$",

    # KPI AVsync
    "av_delay_send":                                "Audio-Video delay difference (ms)",
    "kpi_av_synchronization":                       r"$KPI_{avsync}$",

    # KPI Resolution stability
    "kpi_resolution_stability":                     r"$KPI_{resolution}$",
    "max_resolution_percentage":                    "Time on highest resolution (%)",
    "kpi_resolution_stability_norm":                r"$KPI_{resolution}$ Cut",
    "max_resolution_percentage_norm":               "Time on highest resolution (%) Cut",

    # KPI Fps
    "kpi_fps_stability":                            r"$KPI_{fps}$",
    
    # KPI QAudio
    "kpi_q_audio":                                  r"$KPI_{Qaudio}$",

    # KPI QVideo
    "kpi_q_video":                                  r"$KPI_{Qvideo}$",
    
    # FINAL Step
    "qoe_simple_normal":                            r"$QoE_{simple}$",
    "qoe_simple_smooth":                            r"$QoE_{simple}$ (No $KPI_{Qaudio}$)"
}


# linestyles = ['solid', 'dashed', 'dotted', 'dashdot']
# dashList = [(3, 3, 2, 2), (5, 2, 20, 2), (2, 2), (3, 4), (10, 2)]
# colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6']