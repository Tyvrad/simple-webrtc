This directory contains the measurement script required to launch WebRTC measurements at an instance.

'java_source/' contains the source code for the Java measurement controller. It uses maven as build system. In order to create a new build from scratch, run is using the goals "clean" and "install". 
Upon success, a new build is placed in 'target/WebRTCTest/'. The contents of the directory must then be copied to the clients.

Steps to start from 0 to deploying the client in Google Cloud:
1. Create VM with at least 6 cores & 4GB of RAM (Fewer RAM not allowed by Google)
	- Use meaningful instance name
	- Pick any zone, preferably one with low latency
	- Leave the rest of the configuration as it is
Optional: Under Compute Engine -> Metadata -> SSH keys add your public key as authorized key for the project. This makes working with the instances easier, as you can connect to the instance from your terminal instead of having to use the Google Cloud Webinterface.
	
2. Connect to the instance
	- perform the following commands
	- sudo useradd webrtc
	- sudo passwd webrtc # password:password1
	- sudo mkdir /home/webrtc
	- sudo chown webrtc:webrtc /home/webrtc
	- sudo chmod 777 /home/webrtc
	- usermod -a -G google-sudoers webrtc
	- su webrtc && mkdir /home/webrtc/ && cd ~
	- LOCAL: copy the contents from this directory + 'deployment/' to '/home/webrtc/webrtc-deployment' at the instance and ensure correct permissions
	- run "sudo webrtc-deployment/initialSetup_runasoot.sh"
	- reboot
	
3. Use ssh-keygen to create a keypair and add it to the authorized_keys of user webrtc
	- Add the contents of the generated id_rsa.pub to ~/.ssh/authorized_keys

4. Instance template creation
The instance was prepared in the previous step.
Next, create an instance template which can be launched multiple times. Open the cloud console.
	- Images -> Create
	- Some meaningful name + description, source drive: drive of the instance
	- Instance template -> Create
	- Meaningful name, 6 CPUs, 5.5GB of RAM
	- Boot Drive -> Change -> Custom Image. Select the image you just created
	
To create an instance using this template click on the arrow next to "Create Instance" and select "from template". You can customize the instance name + zone before launch.
- To increase the ease of conducting measurements, assign a static IP to each instance
- These can be reserved via VPC-Network -> External IP-Addresses
