import string

import pylibftdi
from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver
import os
import time
import sys


class AtlasDevice(Device):

	def __init__(self, sn):
		Device.__init__(self, mode='t', device_id=sn)


	def read_line(self, size=0):
		"""
		taken from the ftdi library and modified to 
		use the ezo line separator "\r"
		"""
		lsl = len('\r')
		line_buffer = []
		while True:
			next_char = self.read(1)
			if next_char == '' or (size > 0 and len(line_buffer) > size):
				break
			line_buffer.append(next_char)
			if (len(line_buffer) >= lsl and
					line_buffer[-lsl:] == list('\r')):
				break
		return ''.join(line_buffer)
	
	def read_lines(self):
		"""
		also taken from ftdi lib to work with modified readline function
		"""
		lines = []
		try:
			while True:
				line = self.read_line()
				if not line:
					break
					self.flush_input()
				lines.append(line)
			return lines
		
		except FtdiError:
			print "Failed to read from the sensor."
			return ''		

	def send_cmd(self, cmd):
		"""
		Send command to the Atlas Sensor.
		Before sending, add Carriage Return at the end of the command.
		:param cmd:
		:return:
		"""
		buf = cmd + "\r"     	# add carriage return
		try:
			self.write(buf)
			return True
		except FtdiError:
			print "Failed to send command to the sensor."
			return False
			
			
			
def get_ftdi_device_list():
	"""
	return a list of lines, each a colon-separated
	vendor:product:serial summary of detected devices
	"""
	dev_list = []
	
	for device in Driver().list_devices():
		# list_devices returns bytes rather than strings
		dev_info = map(lambda x: x.decode('latin1'), device)
		# device must always be this triple
		vendor, product, serial = dev_info
		dev_list.append(serial)
	return dev_list


if __name__ == '__main__':

	print "Discovered FTDI serial numbers:"

	devices = get_ftdi_device_list()
	cnt_all = len(devices)
	CondReading = 0
	
	#print "\nIndex:\tSerial: "
	for i in range(cnt_all):
		print  "\nIndex: ", i, " Serial: ", devices[i]
		
		if devices[i] == 'DB00ZB76':
                    index = i
		
	print "==================================="
	
	#index = 0
            
	while True:
		

		try:
                        #use device at index 0 is default
                        #but we will be manually defining the device for compatibiliity with AP3
			dev = AtlasDevice(devices[index])
			print "Using device at index: " + str(index) #explain device used
			break
		except pylibftdi.FtdiError as e:
			print "Error, ", e
			print "Please input a valid index"

	print ""
	print">> Opened device ", devices[int(index)]
	print">> Any commands entered are passed to the board via FTDI:"

	time.sleep(1)
	dev.flush()
	
	while True:
		#input_val = raw_input("Enter command: ")
                input_val = 'R'
		delaytime = 10			
		# get the information of the board you're polling
		print("Polling sensor every %0.2f seconds, press ctrl-z to exit" % delaytime)
	
		try:
                    time.sleep(2)
                    dev.send_cmd('R')
                    time.sleep(1.3)
                    lines = dev.read_lines()
                    
                    
                    
                    cleanlines = [line for line in lines if not line.startswith('*OK')]
                    for i in range(len(cleanlines)):
			print cleanlines[i]
			condline = cleanlines[i]
			
                        CondReading = int(float(condline)*100)/100 #take away decimal
                        CondReading = str(CondReading)
                        f=open('conductivityout.txt','w')
                        f.write(CondReading)
                        f.close()
                    lines = dev.read_lines()
                    for i in range(len(lines)):
			print lines[i]
			if lines[i][0] != '*':
				print "Response: " , lines[i]
		    
		    time.sleep(delaytime)
	
                except KeyboardInterrupt: 		# catches the ctrl-c command, which breaks the loop above
                    print("Continuous polling stopped")
                    sys.exit()

		