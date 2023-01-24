#importing libraries
import sys,os
import socket
import threading
import time
from packet import Packet
import math

#variables
WINDOW_SIZE = 10
DATA_SIZE = 500 
SEQ_MODULO = 32 
NUM_OF_PACKETS = 0
lock = threading.Lock()  

N=1
base=0
current_seqnum=0
seq_num = 0
terminate = False #to keep track of end of packet
unack_pkt = [] #to track unacked packet
ack_pkt = [] #to track acked packet
timer_dict = {} #to keep track of timers assocaited with every packet

#log files 
seq_num_log = []
ack_log = []
n_log = []
n_log.append(N)

def sendPacket(packets, emulatorAddr, emuReceiveData, client_udp_sock,timeoutInterval):
    global current_seqnum, base, N, timer_dict

    #initializing thread 
    ack_thread = threading.Thread(target=receiveACK, args=(client_udp_sock,))
    #starting thread
    ack_thread.start()


    #print("Total packets are : ",len(packets))

    while not terminate:
        if ((len(set(ack_pkt)) == len(packets)-1) and (len(unack_pkt) == 0)):
            print("EOT packet sent")
            client_udp_sock.sendto(packets[current_seqnum].encode(), (emulatorAddr, emuReceiveData))
            seq_num_log.append("EOT")
        
        
        elif len(timer_dict) != 0:
            for key in list(timer_dict.keys()):
                #print("key and timer dict are ",key,timer_dict[key])
                try:
                    #print("first try")
                    if time.time() - timer_dict.get(key) > timeoutInterval :
                        #print("Timeout")
                        #print("Seq number that timed out is :",timer_dict[key])
                        if key == base :
                            lock.acquire()
                            #print("Base Timeout")
                            #current_seqnum = base
                            #print("Current seq no. is ", current_seqnum)
                            timer_dict[key] = time.time()
                            client_udp_sock.sendto(packets[key].encode(), (emulatorAddr, emuReceiveData))
                            #print("Timer dict is :",timer_dict)
                            N = 1
                            n_log.append(N)
                            print("N decreased due to timeout at base",N)
                            #print("base is :",base)
                            lock.release()
                        else:
                            lock.acquire()
                            #print("Other then base Timed out")
                            #print("Current seq no. is ", current_seqnum)
                            #timer_dict[key] = time.time()
                            #print("Timer dict is :",timer_dict)
                            N = 1
                            n_log.append(N)
                            #current_seqnum = base
                            print("N decreased due to timeout other than at base",N)
                            #print("base is :",base)
                            lock.release()
                except:
                    print("except pass")
                    pass
                
        else:
            if len(unack_pkt) <= min(N,len(packets)) :
            #if base + len(unack_pkt) <= min(N,len(packets)) :
                #print("Current sequence number is :",current_seqnum)
                client_udp_sock.sendto(packets[current_seqnum].encode(), (emulatorAddr, emuReceiveData))
                #print("Sent data")
                seq_num_log.append(packets[current_seqnum].seqnum)
                lock.acquire()
                d={current_seqnum:time.time()}
                timer_dict.update(d)
                unack_pkt.append(current_seqnum)
                #print("Unacked packets are",unack_pkt)
                base= current_seqnum
                #print("Base :",base)
                current_seqnum = (current_seqnum + 1) % 32
                #print("Updated current seqnum is ", current_seqnum)
                lock.release()
        


def receiveACK(client_udp_sock):
    global terminate, base, N, timer_dict, ack

    while not terminate:
        msg, _ = client_udp_sock.recvfrom(4096)
        #print(msg)
        ack_packet = Packet(msg)
        ack_seq_num = ack_packet.seqnum
        ack_type = ack_packet.typ

        if ack_type == 0:
            if ack_seq_num in unack_pkt :
                #print("ack_seq_num ",ack_seq_num)
                if ack_seq_num == base :
                    lock.acquire()
                    #print(ack_seq_num)
                    #print("Deleted seq no timer ",timer_dict[ack_seq_num])
                    del timer_dict[ack_seq_num]
                    #print(timer_dict)
                    #timer_list[ack_seq_num].stop()
                    #print("N before update",N)
                    N = min(N+1, WINDOW_SIZE)
                    print("N increased when base seq no received ",N)
                    unack_pkt.remove(ack_seq_num)
                    ack_pkt.append(ack_seq_num)
                    #print("ack_pkt is ",ack_pkt)
                    lock.release()
                else:
                    lock.acquire()
                    #print("Deleted seq no timer ",timer_dict[ack_seq_num])
                    del timer_dict[ack_seq_num]
                    #print(timer_dict)
                    #print("N before update",N)
                    N = min(N+1, WINDOW_SIZE)
                    print("N inreased to  :",N)
                    #timer_list[seq_num].stop()
                    unack_pkt.remove(ack_seq_num)
                    ack_pkt.append(ack_seq_num)
                    lock.release()
            else:
                print("Already received ack")

        # if data received from receiver, not expected scenario
        if ack_type == 1 :
            sys.stderr.write("Got data from receiver. Exiting")
            raise SystemExit

        # if received an acknowledgement for EOT packet, set terminate flag to True
        if ack_type == 2 :
            lock.acquire()
            terminate = True
            print("EOT received")
            #seq_num_log.append("EOT")
            ack_log.append("EOT")
            lock.release()
            break
        
        n_log.append(N)
        ack_log.append(ack_packet.seqnum)
                   





def fileToPacket(filename):
    global NUM_OF_PACKETS
    packets = []
    file = open(os.path.join(sys.path[0],filename), "rb").read().decode()

    NUM_OF_PACKETS = math.ceil(len(file) / DATA_SIZE) + 1  # all data packets + 1 EOT packet

    for i in range(0, NUM_OF_PACKETS - 1):
        data = file[i * DATA_SIZE:min((i + 1) * DATA_SIZE, len(file))]
        #print(data)
        seq_num = i % SEQ_MODULO
        packets.append(Packet(1, seq_num, len(data), str(data)))

    packets.append(Packet(2, NUM_OF_PACKETS - 1, 0, ""))  # last packet is the EOT packet
    return packets



def writeLogFile():
    # Writing to the log files (ack.log, seqnum.log, N.log)

    # seqnum.log
    f = open(os.path.join(sys.path[0],'seqnum.log'), 'w+')
    for i in range(len(seq_num_log)):
        f.write("t="+ str(i) +" " + str(seq_num_log[i]) + "\n")
    #for log in seq_num_log:
     #   f.write(str(log) + "\n")
    f.close()

    # ack.log
    f = open(os.path.join(sys.path[0],'ack.log'), 'w+')
    for i in range(len(ack_log)):
        f.write("t="+ str(i) +" " + str(ack_log[i]) + "\n")
    #for log in ack_log:
    #    f.write(str(log) + "\n")
    f.close()

    # N.log
    f = open(os.path.join(sys.path[0],'N.log'), 'w+')
    for i in range(len(n_log)):
        f.write("t="+ str(i) +" " + str(n_log[i]) + "\n")
    #f.write(str(n_log) + "\n")
    f.close()


def main():
    #Checking for expected length of CLI arguments
    if len(sys.argv) != 6:
        print("Improper arguments")
        exit(1)

    emulatorAddr = sys.argv[1]
    emuReceiveData = int(sys.argv[2])
    senderReceiveACK = int(sys.argv[3])
    timeoutInterval = float(sys.argv[4])
    filename = sys.argv[5]

    #Creating packets in proper format based on packet class
    packets = fileToPacket(filename)

    #creating UDP socket
    client_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_udp_sock.bind(('', senderReceiveACK))

    #sending packets, handling timeout and acknowledgements
    sendPacket(packets, emulatorAddr, emuReceiveData, client_udp_sock, timeoutInterval)

    #writing to log files
    writeLogFile()


if __name__ == '__main__':
    main()