import sys
import socket
import os
from packet import *
import datetime
import time

# Variables
time1 = time.time()
eAdd = sys.argv[1]
ePort = int(sys.argv[2])
sendPort = int(sys.argv[3])
fileName = sys.argv[4]
seqNum = 0
base = 0
window = 10
maxData = 500
packets = []
modulo = 32

# open necessary files

slog = open('segnum.log', 'w')
alog = open('ack.log', 'w')
f = open(fileName, 'r')


# Helper Functions

def sendOnePacket(pack):
    sendData = pack.get_udp_data()
    sock.sendto(sendData, (eAdd, ePort))


# Initialize socket for sender, don't bind sender

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.bind(('', sendPort))

#Send first window
for x in range(window):
    data = f.read(500)
    if data == '':
        break
    newPacket = packet.create_packet(seqNum, data)
    sendOnePacket(newPacket)
    slog.write(str(seqNum) + '\n')
    if x == 0:
        sock2.settimeout(0.1)
    seqNum += 1
    packets.append(newPacket)

while len(packets) > 0:

    try:
        (ack, otheradd) = sock2.recvfrom(2048)
    except socket.timeout as e:
		#Timeout
        for packet in packets:
            sendOnePacket(packet)
            slog.write(str(seqNum) + '\n')
            if packet == packets[0]:
                sock2.settimeout(0.1)
        continue
	#Data Recieved
    receivedPacketData = packet.parse_udp_data(ack)
    ack = receivedPacketData.seq_num
    alog.write(str(ack) + '\n')
    base = packets[0].seq_num
    numAcking = ack - base + 1

    if base > ack:
        numAcking = numAcking + 32

	#Make sure the Ack is in the window
    if numAcking > 0 and numAcking <= 10:
    	for x in range(numAcking):
            packets.pop(0)
            if x == 0:
                sock2.settimeout(0.1)
            data = f.read(500)
            if data == "":
                continue
            newPacket = packet.create_packet(seqNum, data)
            sendOnePacket(newPacket)
            slog.write(str(seqNum) + '\n')	
            packets.append(newPacket)
            seqNum = (1 + seqNum) % 32

	#Invalid Ack, so ignore
    else:
        continue

newPacket = packet.create_eot(seqNum)
sendOnePacket(newPacket)

while True:
    try:
        (ack, otheradd) = sock2.recvfrom(2048)
        break
    except:
        continue


sock.close()
sock2.close()
slog.close()
alog.close()
f.close()
t = time.time()
timelog = open('time.log', 'w')
timelog.write(str(t-time1))
timelog.close()