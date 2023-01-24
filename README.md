Congestion-controlled Pipelined RDT Protocol over UDP
==============================
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a>
    <img src="readme-assets/intro.png" alt="Logo" width="240" height="240">
  </a>
</div>

A Congestion-controlled Pipelined RDT protocol is implemented over UDP to transfer a text file from one host to another across an unreliable network. The sender sends packets to a network emulator, which may randomly discard or reorder them before forwarding them to the receiver. The receiver also sends SACKs to the sender through the same network emulator

Usage
------------
1. Clone the repo
	```
	git clone https://github.com/chauhan-vivek/UDP_Congestion_Control.git
	```
2. Create virtual environment.
	```make
	make create_environment
	```
3. Activate virtual environment.

4. Download and install all required packages.

5. Run Network Emulator
	```make
	python network_emulator.py <arg1> <arg2> <arg3> <arg4> <arg5> <arg6> <arg7> <arg8> <arg9> 
	```
	<br />
	To run nEmulator, supply following CLI arguments:
	<br />
	where:<br />
	<arg1> : <emulator's receiving UDP port number in the forward (sender) direction>, <br />
	<arg2> : <receiver's network address>, <br />
	<arg3> : <receiver's receiving UDP port number>, <br /> 
	<arg4> : <emulator's receiving UDP port number in the backward (receiver) direction>, <br />
	<arg5> : <sender's network address>,  <br />
	<arg6> : <sender's receiving UDP port number>, <br />
	<arg7> : <maximum delay of the link in units of millisecond>, <br />
	<arg8> : <packet discard probability>, <br />
	<arg9> : <verbose-mode> (Boolean: Set to 1, the network emulator will output its internal processing, one per line, e.g. receiving Packet seqnum/SACK seqnum, discarding Packet seqnum /SACK seqnum, forwarding Packet seqnum /SACK seqnum). <br />

6. Run Sender
	```make	
	python sender.py <arg1> <arg2> <arg3> <arg4> <arg5>
	```
	<br />
	To run Sender, supply following CLI arguments:
	<br />
	where:<br />
	<arg1> : <host address of the network emulator>,<br />
	<arg2> : <UDP port number used by the emulator to receive data from the sender>,<br />
	<arg3> : <UDP port number used by the sender to receive SACKs from the emulator>,<br />
	<arg4> : <timeout interval in units of millisecond>, and<br />
	<arg5> : <name of the file to be transferred> <br />
	<br />
	
7. Run Receiver
	```make
	python receiver.py <arg1> <arg2> <arg3> <arg4>
	```
	<br />
	To run Sender, supply following CLI arguments:
	<br />
	where:<br />
	<arg1> : <hostname for the network emulator>,<br />
	<arg2> : <UDP port number used by the link emulator to receive ACKs from the receiver>,<br />
	<arg3> : <UDP port number used by the receiver to receive data from the emulator>, and <br />
	<arg4> : <name of the file into which the received data is written><br />


Example run: <br />
python ./network_emulator.py 45970 host2 50970 50971 host3 45971 1 0.0 1 <br />
python ./receiver.py host1 50971 50970 output.txt <br />
python ./sender.py host1 45970 45971 0.5 input.txt <br />
 
------------
