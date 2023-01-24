import sys,os
import socket
from packet import Packet

arrival_log = []
expected_pkt_num = 0
SEQ_MODULO = 32
WINDOW_SIZE = 10
rbuffer = []
data_dict={}

def receive(filename, emulatorAddr, emuReceiveACK, client_udp_sock):
    global expected_pkt_num,data_dict
    save_data = bytearray()
    #data_dict= {}

    try:
        file = open(os.path.join(sys.path[0],filename), 'wb')
    except IOError:
        print('Unable to open', filename)
        return

    while True:
        msg, _ = client_udp_sock.recvfrom(4096)
        data_packet = Packet(msg)
        packet_type = data_packet.typ
        seq_num = data_packet.seqnum
        data = data_packet.data
        arrival_log.append(seq_num)
        #print("SEq_num from msg is : ",seq_num)
        #print(expected_pkt_num)
        # receives EOT, send EOT back and exit
        if packet_type == 2 and seq_num == expected_pkt_num % SEQ_MODULO:
            print("EOT received")
            client_udp_sock.sendto(Packet(2,seq_num,0,"").encode(), (emulatorAddr, emuReceiveACK))
            break
        
        #already acked data packet
        if seq_num < expected_pkt_num % SEQ_MODULO and seq_num in rbuffer:
            client_udp_sock.sendto(Packet(0,seq_num,0,"").encode(), (emulatorAddr, emuReceiveACK))

        # receives not acked data packet
        elif seq_num not in rbuffer and seq_num < expected_pkt_num % SEQ_MODULO + WINDOW_SIZE :
            #receives expected data packet
            if seq_num == expected_pkt_num % SEQ_MODULO:
                print("Seq_num is :",seq_num)
                print("Expected pkt num is : ",expected_pkt_num)
                rbuffer.append(seq_num)
                print("Ack sent when expected seq num received")
                client_udp_sock.sendto(Packet(0,seq_num,0,"").encode(), (emulatorAddr, emuReceiveACK))
                if seq_num < max(rbuffer,default=0) :
                    distance = max(rbuffer) - expected_pkt_num % SEQ_MODULO
                    expected_pkt_num = expected_pkt_num + distance +1
                    #already acked packets , writing to file
                    if len(data_dict)!=0:
                        for key in list(data_dict.keys()):
                            if key in rbuffer :
                                save_data.extend(data_dict[key].encode())
                                del data_dict[key]
                    else:
                        print("Something went wrong")

                else:
                    expected_pkt_num += 1
                    save_data.extend(data.encode())

            
            #receives forward packets
            elif seq_num < expected_pkt_num % SEQ_MODULO + WINDOW_SIZE :
                rbuffer.append(seq_num)
                client_udp_sock.sendto(Packet(0,seq_num,0,"").encode(), (emulatorAddr, emuReceiveACK))
                d = {seq_num : data}
                data_dict.update(d)
               
        else:
            print("Data outside reciver window")

    file.write(save_data)
    file.close()


def writeLogFile():
    # Writing to arrival.log file
    f = open(os.path.join(sys.path[0],'arrival.log'), 'w+')
    for log in arrival_log:
        f.write(str(log) + "\n")
    f.close()


def main():
    if len(sys.argv) != 5:
        print("Improper arguments")
        exit(1)

    emulatorAddr = sys.argv[1]
    emuReceiveACK = int(sys.argv[2])
    rcvrReceiveData = int(sys.argv[3])
    filename = sys.argv[4]

    client_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_udp_sock.bind(('', rcvrReceiveData))

    receive(filename, emulatorAddr, emuReceiveACK, client_udp_sock)
    writeLogFile()


if __name__ == '__main__':
    main()