from packet import Packet
import random
import time
from queue import Queue
import threading
import argparse
import socket
# initialize to dumby values for sanity checking purposes
max_delay = None # max delay a packet can be delayed by in milliseconds

forward_recv_port = None # the port to listen on to get messages from the sender
backward_recv_port = None # emulator's receiving UDP port from receiver

receiver_addr = None # receiver's network address
receiver_recv_port = None # receiver's receiving UDP port

sender_addr = None # sender's network address
sender_recv_port = None # the sender's receiving UDP port number

prob_discard = None # the probability a packet is discarded

verbose = False 

data_buff = Queue()
ack_buff = Queue()


def processPacket(packet, fromSender):
    global prob_discard
    if not isinstance(packet, bytes):
        raise RuntimeError("processPacket can only process a packet encoded as bytes")
    recvd_packet = Packet(packet)
    typ, seqnum, length, data = recvd_packet.decode()
    if verbose: print("Packet being processed: Type={}, seqnum={}, length={}, data={}".format(typ, seqnum, length, data))
    if typ == 2: # if type == EOT
        if fromSender:
            while not data_buff.empty():
                # delay for longest possible delay and check again.
                delayThread(max_delay)
            if verbose: print("Sending packet: Type={}, seqnum={}, length={}, data={}".format(typ, seqnum, length, data))
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(packet, (receiver_addr, receiver_recv_port))
        else:
            while not ack_buff.empty():
                # delay for longest possible delay and check again.
                delayThread(max_delay)
            if verbose: print("Sending packet: Type={}, seqnum={}, length={}, data={}".format(typ, seqnum, length, data))
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(packet, (sender_addr, sender_recv_port))
    else:
        if not randomTrue(prob_discard):
            # process packet
            if fromSender:
                if typ == 0:
                    raise RuntimeError("Received an Ack from the sender")
                    pass
                if verbose: print("Adding packet to data buffer: Type={}, seqnum={}, length={}, data={}".format(typ, seqnum, length, data))
                data_buff.put(packet)
            else:
                if typ == 1:
                    raise RuntimeError("Received data from the receiver")
                if verbose: print("Adding packet to ack buffer: Type={}, seqnum={}, length={}, data={}".format(typ, seqnum, length, data))
                ack_buff.put(packet)
            delay = random.randint(0, max_delay)
            delayThread(delay)
            if fromSender:
                data_buff.get(block=False)
            else:
                ack_buff.get(block=False)
            if verbose: print("Sending packet: Type={}, seqnum={}, length={}, data={}".format(typ, seqnum, length, data))
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if fromSender:
                s.sendto(packet, (receiver_addr, receiver_recv_port))
            else:
                s.sendto(packet, (sender_addr, sender_recv_port))
        else:
            if verbose: print("Dropped packet: Type={}, seqnum={}, length={}, data={}".format(typ, seqnum, length, data))



def forwardFlow():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', forward_recv_port))
    while True:
        packet = sock.recv(1024)
        if verbose: print("Received a packet from from sender")
        new_thread = threading.Thread(target=processPacket, args=(packet, True,))
        new_thread.start()

def backwardFlow():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', backward_recv_port))
    while True:
        packet = sock.recv(1024)
        if verbose: print("Received a packet from receiver")
        new_thread = threading.Thread(target=processPacket, args=(packet, False,))
        new_thread.start()

def delayThread(delay):
    # need to convert milliseconds to seconds for time.sleep()
    s_delay = delay / 1000.0
    if verbose: print("Packet delayed by {} milliseconds".format(delay))
    time.sleep(s_delay)



def randomTrue(probability):
    return random.random() < probability


if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("<Forward receiving port>", help="emulator's receiving UDP port number in the forward (sender) direction")
    parser.add_argument("<Receiver's network address>")
    parser.add_argument("<Reciever’s receiving UDP port number>")
    parser.add_argument("<Backward receiving port>", help="emulator's receiving UDP port number in the backward (receiver) direction")
    parser.add_argument("<Sender's network address>")
    parser.add_argument("<Sender's receiving UDP port number>")
    parser.add_argument("<Maximum Delay>", help="maximum delay of the link in units of millisecond")
    parser.add_argument("<drop probability>", help="packet discard probability")
    parser.add_argument('<verbose>', nargs='?', default=0)
    args = parser.parse_args()
    # set up sockets to be listening on
    args = args.__dict__ # A LAZY FIX
    max_delay = int(args["<Maximum Delay>"])
    forward_recv_port = int(args["<Forward receiving port>"])
    backward_recv_port = int(args["<Backward receiving port>"])
    receiver_addr = str(args["<Receiver's network address>"])
    receiver_recv_port = int(args["<Reciever’s receiving UDP port number>"])
    sender_addr = str(args["<Sender's network address>"])
    sender_recv_port = int(args["<Sender's receiving UDP port number>"])
    prob_discard = float(args["<drop probability>"])
    if prob_discard < 0 or prob_discard > 1:
        raise RuntimeError("Probability of discarding a packet should be between 0 and 1")

    verbose = (1 == int(args["<verbose>"]))


    # start a thread for both forward and backword network flow
    forwardThread = threading.Thread(target=forwardFlow)
    backwardThread = threading.Thread(target=backwardFlow)
    if verbose: print("Starting network emulator, and waiting to receive something...")
    forwardThread.start()
    backwardThread.start()
    while not forwardThread.is_alive():
        pass
    forwardThread.join()
    while not backwardThread.is_alive():
        pass
    backwardThread.join()
