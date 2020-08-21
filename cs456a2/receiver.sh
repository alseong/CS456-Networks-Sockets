#!/bin/bash

#Run script for receiver distributed as part of 
#Assignment 2
#Computer Networks (CS 456)
#Number of parameters: 4
#Parameter:
#    $1: host address of the network emulator
#    $2: UDP port number used by the emulator to receive data from the receiver
#    $3: UDP port number used by the receiver to receive ACKs from the emulator
#    $4: name of the file to be transferred


#For Python implementation
python3 receiver.py $1 $2 $3 $4