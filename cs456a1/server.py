import socket
import sys
import pickle

# Variables for request code, and messages that clients send
requestcode = sys.argv[1]
messageList = ""
count = 0 

# Start udp socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sock.bind(('', 0))

#Store Negotiating Port number
nport = sock.getsockname()[1]

print("SERVER_PORT: " + str(nport) + "\n")
f = open("server.txt", "w+")
f.write("SERVER_PORT: " + str(nport) + "\n")
rport = None

sock.listen(1)

var1 = True
# listen for msgs 
while var1:
  connectionSocket, addr = sock.accept()
  message = connectionSocket.recv(2048)
  if (message == requestcode):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('', 0))
    rport = serverSocket.getsockname()[1]
    connectionSocket.send(str(rport))
  else:
    connectionSocket.send(str(0))
    connectionSocket.close()
    continue
  var = True
  while var:
    msg, clientAddress = serverSocket.recvfrom(2048)
    if msg == "GET":
      if count == 0:
        serverSocket.sendto("NO MSG\n", clientAddress)
        count = count + 1
      else:
        serverSocket.sendto(messageList + "NO MSG \n", clientAddress)
    elif msg == "TERMINATE":
      var = False
      var1 = False
      connectionSocket.close()
      serverSocket.close()
    else:
      messageList = messageList + str(rport) + ": " + str(msg) + "\n"
      var = False
sock.close()
sys.exit(1)


    

      





  