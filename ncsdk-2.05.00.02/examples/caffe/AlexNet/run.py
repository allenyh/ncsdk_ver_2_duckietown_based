#! /usr/bin/env python3

# Copyright 2018 Intel Corporation.
# The source code, information and material ("Material") contained herein is  
# owned by Intel Corporation or its suppliers or licensors, and title to such  
# Material remains with Intel Corporation or its suppliers or licensors.  
# The Material contains proprietary information of Intel or its suppliers and  
# licensors. The Material is protected by worldwide copyright laws and treaty  
# provisions.  
# No part of the Material may be used, copied, reproduced, modified, published,  
# uploaded, posted, transmitted, distributed or disclosed in any way without  
# Intel's prior express written permission. No license under any patent,  
# copyright or other intellectual property rights in the Material is granted to  
# or conferred upon you, either expressly, by implication, inducement, estoppel  
# or otherwise.  
# Any license under such intellectual property rights must be express and  
# approved by Intel in writing. 

from mvnc import mvncapi as mvnc 
import sys
import numpy
import cv2
import time
import csv
import os
import sys

dim=(227,227)
EXAMPLES_BASE_DIR='../../'

# ***************************************************************
# get labels
# ***************************************************************
labels_file=EXAMPLES_BASE_DIR+'data/ilsvrc12/synset_words.txt'
labels=numpy.loadtxt(labels_file,str,delimiter='\t')

# ***************************************************************
# configure the NCS
# ***************************************************************
mvnc.global_set_option(mvnc.GlobalOption.RW_LOG_LEVEL, 2)

# ***************************************************************
# Get a list of ALL the sticks that are plugged in
# ***************************************************************
devices = mvnc.enumerate_devices()
if len(devices) == 0:
	print('No devices found')
	quit()

# ***************************************************************
# Pick the first stick to run the network
# ***************************************************************
device = mvnc.Device(devices[0])

# ***************************************************************
# Open the NCS
# ***************************************************************
device.open()

network_blob='graph'

#Load blob
with open(network_blob, mode='rb') as f:
	blob = f.read()

graph = mvnc.Graph('graph')
graph.allocate(device, blob)

# ***************************************************************
# Load the image
# ***************************************************************
ilsvrc_mean = numpy.load(EXAMPLES_BASE_DIR+'data/ilsvrc12/ilsvrc_2012_mean.npy').mean(1).mean(1) #loading the mean file
img = cv2.imread(EXAMPLES_BASE_DIR+'data/images/nps_electric_guitar.png')
img=cv2.resize(img,dim)
img = img.astype(numpy.float32)
img[:,:,0] = (img[:,:,0] - ilsvrc_mean[0])
img[:,:,1] = (img[:,:,1] - ilsvrc_mean[1])
img[:,:,2] = (img[:,:,2] - ilsvrc_mean[2])

# ***************************************************************
# Initialize Fifos
# ***************************************************************
fifoIn = mvnc.Fifo("fifoIn0", mvnc.FifoType.HOST_WO)
fifoOut = mvnc.Fifo("fifoOut0", mvnc.FifoType.HOST_RO)

descIn = graph.get_option(mvnc.GraphOption.RO_INPUT_TENSOR_DESCRIPTORS)
descOut = graph.get_option(mvnc.GraphOption.RO_OUTPUT_TENSOR_DESCRIPTORS)

fifoIn.allocate(device, descIn[0], 2)
fifoOut.allocate(device, descOut[0], 2)

# ***************************************************************
# Send the image to the NCS
# ***************************************************************
graph.queue_inference_with_fifo_elem(fifoIn, fifoOut, img, 'user object')

# ***************************************************************
# Get the result from the NCS
# ***************************************************************
output, userobj = fifoOut.read_elem()

# ***************************************************************
# Print the results of the inference form the NCS
# ***************************************************************
order = output.argsort()[::-1][:6]
print('\n------- predictions --------')
for i in range(0,5):
	print ('prediction ' + str(i) + ' (probability ' + str(output[order[i]]*100) + '%) is ' + labels[order[i]] + '  label index is: ' + str(order[i]) )


# ***************************************************************
# Clean up the graph and the device
# ***************************************************************
fifoIn.destroy()
fifoOut.destroy()
graph.destroy()
device.close()
    



