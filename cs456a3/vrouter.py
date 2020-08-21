import sys
import struct
import socket

# Global Variables
nfeAddress = sys.argv[1]
nfePort = int(sys.argv[2])
addPort = (nfeAddress, nfePort)
mainRouter = int(sys.argv[3])
topoFile = "topology_" + str(mainRouter) + ".out"
routeFile = "routingtable_" + str(mainRouter) + ".out"
cost = {}
prevRoutes = {}
network = {k: [] for k in range(1,8)}

def printHelper(typeString, SID, SLID, RID, RLID, LC):
    print(typeString + ':SID(' + str(SID) + "),SLID(" + str(SLID) + "),RID(" + str(RID) + "),RLID(" + str(RLID) + "),LC(" + str(LC) + ')')\

def topPrint(topoFile):
    tFile = open(topoFile,'a')
    tFile.write('\nTOPOLOGY\n')
    for router in network:
        for lst in network[router]:
            if lst[2]:
                toWrite = "router:"+str(router)+",router:"+str(lst[2])+",linkid:"+str(lst[0])+",cost:"+str(lst[1])+'\n'
                tFile.write(toWrite)

def routePrint(routeFile):
    routingFile = open(routeFile, 'a')
    routingFile.write('\nROUTING\n')
    for router in cost:
        if cost[router] != 999999:
                nextHop = router
                while prevRoutes[prevRoutes[nextHop]] != 999998:
                    nextHop = prevRoutes[nextHop]
                routingFile.write(str(router)+':'+str(nextHop)+','+str(cost[router]) + '\n')

def sendHelper(int1, int2, int3, int4, int5, int6):
    message = struct.pack('!iiiiii', int1, int2, int3, int4, int5, int6)
    mainSocket.sendto(message, addPort)


# Initialize Socket
mainSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send init message
initMsg = struct.pack('!ii',1,mainRouter)
mainSocket.sendto(initMsg, addPort)

# Wait for init reply from NFE
(message, addr) = mainSocket.recvfrom(4096)

#Try to recieve a reply
try:
    messageType = struct.unpack("!i", message[:4])[0]
    if messageType != 4:
        raise Exception
except Exception:
    print("Invalid Message!")

#Unpack the reply message
numLinks = struct.unpack("!i", message[4:8])[0]
listTemp = []
byte = 8
for i in range(numLinks):
    link_id = struct.unpack("!i",message[byte:byte+4])[0]
    link_cost = struct.unpack("!i",message[byte+4:byte+8])[0]
    byte = byte + 8
    listTemp.append([link_id,link_cost])

# Update network
for lst in listTemp:
    lst.append(None) 
    network[mainRouter].append(lst)

#Initially let direct neighbouring routes about this router
for link1 in network[mainRouter]:
    sendHelper(3,mainRouter,link1[0],mainRouter,link1[0],link1[1])
    printHelper("Sending(E)", mainRouter, link1[0], mainRouter, link1[0], link1[1])

# Listen for messages from neighbors & entering Forward Phase
while True:
    (message, addr) = mainSocket.recvfrom(4096)

    #Try getting the right LSA message
    try:
        messageType = struct.unpack("!i", message[:4])[0]
        if messageType != 3:
            raise Exception
    except Exception:
        print("Invalid Message!")

    # Unpack LSA message
    senderID = struct.unpack("!i",message[4:8])[0]
    senderLinkID = struct.unpack("!i",message[8:12])[0]
    routeID = struct.unpack("!i",message[12:16])[0]
    routeLinkID = struct.unpack("!i",message[16:20])[0]
    routeLinkCost = struct.unpack("!i",message[20:24])[0]
    printHelper("Received", senderID, senderLinkID, routeID, routeLinkID, routeLinkCost)

    # update network with new information
    corresponding_router = None
    breaking = False
    for router in network:
        if router == routeID:  
            continue
        for lst in network[router]:
            if lst[0]==routeLinkID: 
                if lst[2]!=None: 
                    printHelper("Dropping", senderID, senderLinkID, routeLinkCost, routeLinkID, routeLinkCost)
                    breaking = True
                    break
                else:
                    lst[2] = routeID 
                    corresponding_router = router 
    if breaking:
        continue

    entry_found = False
    for lst in network[routeID]:
        if lst[0]==routeLinkID:
            entry_found = True
            lst[2] = corresponding_router

    if entry_found==False:
        network[routeID].append([routeLinkID,routeLinkCost,corresponding_router])

    topPrint(topoFile)

    #Start to apply the dijkstra's algorithm 
    cost = {k: 999999 for k in range(1,8)}
    prevRoutes = {k: None for k in range(1,8)}
    del cost[mainRouter]
    prevRoutes[mainRouter] = 999998

    for lst in network[mainRouter]:
        if lst[2] is None:
            continue
        cost[lst[2]] = lst[1]
        prevRoutes[lst[2]] = mainRouter

    notSeen = [*cost]
    while len(notSeen):
        source = min(notSeen, key=lambda k: cost[k])
        curr = cost[source]
        i = 0
        while i < len(network[source]):
            lst = network[source][i]
            temp = curr+lst[1]
            if (lst[2] and lst[2] in notSeen and cost[lst[2]]>temp):
                cost[lst[2]] = temp
                prevRoutes[lst[2]] = source
            i +=1
        notSeen.remove(source)

    routePrint(routeFile)

    #Send more information to its neighbours
    for lst in network[mainRouter]:
        if lst[0] != senderLinkID:
            sendHelper(3,mainRouter,lst[0],routeID,routeLinkID,routeLinkCost)
            printHelper("Sending(F)", mainRouter, lst[0], routeID, routeLinkID, routeLinkCost)


