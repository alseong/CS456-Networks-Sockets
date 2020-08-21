import socket
import sys
import pickle

# save values needed to talk to server
serverAddress = sys.argv[1] 
uport = int(sys.argv[2]) 
rcode = sys.argv[3] #request code
msg = sys.argv[4]

# start tcp socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverAddress,uport))
clientSocket.send(rcode.encode())
rport = clientSocket.recv(2048)
if int(rport) == 0:
    print("Invalid req_code.")
    sys.exit(1)
#close tcp connection
clientSocket.close()
clientSocket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket1.sendto("GET".encode(),(serverAddress, int(rport)))
modifiedMessage, serverAddress_1 = clientSocket1.recvfrom(2048)
f = open("client.txt", "a")
f.write("r_port: " + rport + "\n")
f.write(modifiedMessage + "\n")
print(modifiedMessage)
#now need to send msg
clientSocket1.sendto(msg,(serverAddress, int(rport)))
clientSocket1.close()




