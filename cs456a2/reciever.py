from socket import *
import sys
import string
from packet import *

eName = str(sys.argv[1])
ePort = int(sys.argv[2])
recvPort = int(sys.argv[3])
writeFile = str(sys.argv[4])
expected = 0
alog = open('arrival.log', 'w')
#absolute path?
f = open(writeFile, 'w')

# Initiate Socket
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', recvPort))

#Recieve until eot packet
var = True
while var:

	#Try to receive
    try: 
        (recv, otheradd) = sock.recvfrom(512)
    except: 
        continue
    recieve = packet.parse_udp_data(recv)
    snum = recieve.seq_num
    data = recieve.data
    
	#I get a Data Packet
    if recieve.type == 1:
        alog.write(str(snum) + '\n')
        if recieve.seq_num == expected:
            f.write(str(data))
            ack = packet.create_ack(expected)
            sock.sendto(ack.get_udp_data(), (eName, ePort))
            expected = (expected + 1) % 32
        else:
            ack = packet.create_ack(expected-1)
            sock.sendto(ack.get_udp_data(), (eName, ePort))
	#I get a EOT packet
    if recieve.type == 2:
        ack = packet.create_eot(expected)
        sock.sendto(ack.get_udp_data(), (eName, ePort))
        var = False

sock.close()
f.close()
alog.close()