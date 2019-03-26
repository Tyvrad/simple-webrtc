import os, time, paramiko, shutil

# Path to your ssh id
KEYFILE = "/home/user/.ssh/id_rsa"
HOME_DIR = "/home/user"

# Client IPs
ips = [
    "YOUR_IP_HERE"
    ]

# Measurement bandwidths
bandwidths = [0.25, 0.5, 1, 2, 3, 4, 5, 15, 30, 50]
# bandwidths = [0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 1]

# Iterations
iterations = 5

# Duration is the actual measurement time. The actual measurement takes around 25 seconds longer (setup + waiting time)
duration = 120

# 
switchBw = False
setBwTime = 0

def collect_data(bw, setBwTime):
    # SSH to each client, scp the data and delete the directory

    if not os.path.exists("{0}/webrtc-logs/{1}".format(HOME_DIR, bw)):
        os.makedirs("{0}/webrtc-logs/{1}".format(HOME_DIR, bw))

    if not os.path.exists("{0}/webrtc-logs/bw_{1}".format(HOME_DIR, bw)):
        os.makedirs("{0}/webrtc-logs/bw_{1}".format(HOME_DIR, bw))

    for ip in ips:
        if not os.path.exists("{0}/webrtc-logs/{1}/{2}".format(HOME_DIR, bw, ip)):
            os.makedirs("{0}/webrtc-logs/{1}/{2}".format(HOME_DIR, bw, ip))

        os.system("scp -r -o StrictHostKeyChecking=no {0}:/home/webrtc/apprtc-logs/* {1}/webrtc-logs/{2}/{0}/".format(ip, HOME_DIR, bw))

        os.system("ssh -o StrictHostKeyChecking=no {0} 'rm -r /home/webrtc/apprtc-logs/*'".format(ip))

        for folder in os.listdir("{0}/webrtc-logs/{1}/{2}".format(HOME_DIR, bw, ip)):
            if not os.path.isdir("{0}/webrtc-logs/{1}/{2}/{3}".format(HOME_DIR, bw, ip, folder)):
                continue
            for file in os.listdir("{0}/webrtc-logs/{1}/{2}/{3}".format(HOME_DIR, bw, ip, folder)):
                l_ip = ""
                if file.startswith("10."):
                    l_ip = file

                if os.path.exists("{0}/webrtc-logs/{1}/{2}/{3}/webrtc_internals_dump.txt".format(HOME_Dir, bw, ip, folder)) and l_ip != "":
                        if not os.path.exists("{0}/webrtc-logs/bw_{1}/{2}".format(HOME_DIR, bw, folder)):
                            os.makedirs("{0}/webrtc-logs/bw_{1}/{2}".format(HOME_DIR, bw, folder))
                        if switchBw:
                            os.rename(
                                "{0}/webrtc-logs/{1}/{2}/{3}/webrtc_internals_dump.txt".format(HOME_DIR, bw, ip, folder),
                                "{0}/webrtc-logs/bw_{1}/{2}/webrtclog_{4}_{3}.log".format(HOME_DIR, bw, folder, l_ip, setBwTime))
                            break
                        else:
                            # Rename downloaded dump file to webrtclog_ip.log
                            os.rename(
                                "{0}/webrtc-logs/{1}/{2}/{3}/webrtc_internals_dump.txt".format(HOME_DIR, bw, ip, folder),
                                "{0}/webrtc-logs/bw_{1}/{2}/webrtclog_{3}.log".format(HOME_DIR, bw, folder, l_ip))
                            break

    shutil.rmtree("{0}/webrtc-logs/{1}".format(HOME_DIR, bw))

def setBw(ip, bw):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key = paramiko.RSAKey.from_private_key_file(KEYFILE)
    client.connect(ip, 22, pkey=key)

    global setBwTime
    setBwTime = int(round(time.time()))
    print("Time: {0}".format(setBwTime))

    client.exec_command('sudo tc qdisc del dev eth0 root')

    # HBT
    client.exec_command("sudo tc qdisc add dev eth0 root handle 1:0 htb default 1")
    client.exec_command("sudo tc class add dev eth0 parent 1:0 classid 0:1 htb rate {0}mbit ceil {0}mbit".format(bw))

    return setBwTime


def resetBw(ip):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key = paramiko.RSAKey.from_private_key_file(KEYFILE)
    client.connect(ip, 22, pkey=key)

    client.exec_command('sudo tc qdisc del dev eth0 root')
    client.exec_command('sudo pkill tcpdump')

def mySleep(seconds):
    print("Sleeping a total of {0} seconds".format(seconds))
    while seconds > 5:
        time.sleep(5)
        seconds = seconds - 5
        print("{0} remaining".format(seconds))
    time.sleep(seconds)

def launch():
    i_total_measurements = len(bandwidths) * iterations
    i_current_iteration = 1

    print("Starting measurement")
    print("\t" + str(bandwidths))
    print("\t Iterations: {0}".format(iterations))
    print("Total measurements: {0}".format(str(i_total_measurements)))

    for bw in bandwidths:
        print("Beginning measurement with bandwidth {0}mbit/s".format(bw))

        # For each measurement do:
        for x in range(iterations):
            print("Measurement {0}/{1}".format(str(i_current_iteration), str(i_total_measurements)))
            i_current_iteration += 1

            setBwTimestamp = 0

            #Launch
            for ip in ips:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                key = paramiko.RSAKey.from_private_key_file(KEYFILE)
                client.connect(ip, 22, pkey = key)

                # Netem
                setBwTimestamp = setBw(ip, bw)

                # Launch measurement
                client.exec_command('nohup /home/webrtc/webrtc-deployment/launch_measurement 123 {0} >/dev/null 2>&1 &'.format(duration))

            # Sleep if selected
            print("Measurement launched, sleeping")
            time.sleep(duration + 90) # add some extra time to ensure complete stop of measurement at client. DONT USE LESS!

            # Reset
            print("Resetting clients")
            for ip in ips:
                resetBw(ip)

            print("Iteration {0} complete".format(x))

            # After each measurement run, collect data
            print("Organizing data")

            dirname = bw
            collect_data(dirname, setBwTimestamp)

def reset():
    for ip in ips:
        print('Resetting ip {0}'.format(ip))

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key = paramiko.RSAKey.from_private_key_file(KEYFILE)
        client.connect(ip, 22, pkey=key)

        client.exec_command('sudo pkill java')
        client.exec_command('sudo pkill chromium')
        client.exec_command('sudo pkill chromedriver')

        client.exec_command('sudo rm -r /home/webrtc/apprtc-logs/*')
        client.exec_command('sudo rm -r /home/webrtc/tcpdump')
        client.exec_command('sudo tc qdisc del dev eth0 root')

        print('Resetting ip {0} done'.format(ip))

# reset()
launch()
