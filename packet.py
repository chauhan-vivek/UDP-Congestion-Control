import struct

class Packet:
    """
        Constructs a Packet either by specifying the fields, or providing a byte encoded Packet constructed by encode
        Construction by fields:
            Packet(type, seqnum, length, data)
                type - the type of packet, 0 = ACK, 1 = data, 2 = EOT
                seqnum - the seqeunce number mod 32
                length - the length of data AT MOST 500
                data - the data being sent
        Construction by encoded Packet
            Packet(encoded_packet)
                encoded_packet - a packet encoded as a bytes object
    """
    def __init__(self, *args):
        if len(args) == 1:
            if not isinstance(args[0], bytes):
                raise RuntimeError("Received one argument and expect bytes. Got={}\n".format(type(args[0])))
            self.typ, self.seqnum, self.length, self.data = struct.unpack('!iii{}s'.format(len(args[0]) - 12), args[0])
            _, _, _, self.data = struct.unpack('!iii{}s'.format(self.length), args[0])
            self.data = self.data.decode('ASCII')[0:self.length]
        else:
            if len(args[3]) > 500:
                raise RuntimeError("messages to be sent should be at most 500 characters long")
            self.typ = int(args[0])
            self.seqnum = int(args[1])
            self.length = int(args[2])
            self.data = args[3]

    """
        Returns self encoded as a bytes object to be sent over the network
    """
    def encode(self):
        encoded_data = self.data.encode('ASCII')
        return struct.pack('!iii{}s'.format(self.length), self.typ, self.seqnum, self.length, encoded_data)

    """
        Returns the type, seqnum, length, and data of a packet
    """
    def decode(self):
        return int(self.typ), int(self.seqnum), int(self.length), self.data

    """
        Returns a string representation of a packet
    """
    def __repr__(self):
        ret = "Type=" + str(self.typ) + "\n"
        ret += "Seqnum=" + str(self.seqnum) + "\n"
        ret += "Length=" + str(self.length) + "\n"
        ret += "Data=" + self.data
        return ret

if __name__ == '__main__':
    testmsg = "testmsg"
    packet1 = Packet(0, 1, len(testmsg), testmsg)
    print(packet1)
    packet1_enc = packet1.encode()
    print(packet1_enc)
    packet2 = Packet(packet1_enc)
    print(packet2)
