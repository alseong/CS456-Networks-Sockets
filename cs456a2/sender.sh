#!/bin/bash

#Run script for sender distributed as part of 
#Assignment 2
#Computer Networks (CS 456)
#Number of parameters: 4
#Parameter:
#    $1: host address of the network emulator
#    $2: UDP port number used by the emulator to receive data from the sender
#    $3: UDP port number used by the sender to receive ACKs from the emulator
#    $4: name of the file to be transferred


#For Python implementation
python3 sender.py $1 $2 $3 $4