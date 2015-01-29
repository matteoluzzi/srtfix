#!/usr/bin/env python

import sys
import os
import re
from Tkinter import *
from tkFileDialog import askopenfilename


def fixFile(filepath, offset):
		with open(filepath, 'r') as input:
			with open(createOutputFileName(filepath), 'w') as output:
				file = input.read()
				off = parseOffset(offset)
				blocks = file.split("\n")
				for line in blocks:
					print line
					if keyStructure(line):
							start, end = line.split(" --> ")
							print "off, ", off
							newStart = modifyTime(start, off)
							newEnd = modifyTime(end, off)
							print newStart, newEnd
							output.write(formatTime(newStart) + " --> " + formatTime(newEnd) + "\n")
					else:
						output.write(line + "\n")
		return createOutputFileName(filepath)




def createOutputFileName(inputPath):
	head, tail = os.path.splitext(inputPath)
	print head + "_fixed" + tail
	return head + "_fixed" + tail

def keyStructure(str):
	return str.find(" --> ") != -1

def parseOffset(offset):

	off = {"direction": "+", "hours":00, "minutes":00, "seconds":00, "mseconds":000}
	off['direction'] = offset[0]
	offset = offset[1:]
	if offset.find("h") != -1:
		off['hours'] = offset[offset.find("h")-2:offset.find("h")]
	if offset.find("m") != -1:
		off['minutes'] = offset[offset.find("m")-2:offset.find("m")]
	if offset.find("s") != -1:
		off['seconds'] = offset[offset.find("s")-2:offset.find("s")]
	if offset.find("ms") != -1:
		off['mseconds'] = offset[offset.find("ms")-3:offset.find("ms")]
	return off
		


def validateOffset(offset):
	regex = re.compile("([\+\-])((\d{2})[h])((\d{2})[m])((\d{2})[s])((\d{3})(ms))")
	return regex.match(offset)


def modifyTime(time, o):
	off_hours = int(o['hours'])
	off_minutes = int(o['minutes'])
	off_seconds = int(o['seconds'])
	off_mseconds = int(o['mseconds'])
	off_direction = o['direction']
	head, mill = time.split(",")
	head = head.split(":")
	for i in range(len(head)):
		head[i] = int(head[i])
	mill = int(mill)
	newMS = 0
	newS = 0
	newM = 0
	newH = 0
	if off_direction == "+":
		msCarry, newMS = msSum(off_mseconds, mill)
		sCarry, newS = sum(int(off_seconds) + int(msCarry), head[2])
		mCarry, newM = sum(int(off_minutes) + int(sCarry), head[1])
		hCarry, newH = sum(int(off_hours) + int(mCarry), head[0])
	else:

		print head[0], head[1], head[2], mill

		if head[0] < off_hours:
			print_error(Error.SUBTRACTION)			
			exit()
		else:
			newH = head[0] - off_hours

		if head[1] < off_minutes:
			if newH > 0:
				newH -= 1
				head[1] += 60
				newM = head[1] - off_minutes
			else:
				print_error(Error.SUBTRACTION)
				exit()			
		else:
			newM = head[1] - off_minutes

		if head[2] < off_seconds:
			if newM > 0:
				newM -= 1	
				head[2] += 60
				newS = head[2] - off_seconds			
			elif newH > 0:
				newH -= 1
				newM += 59
				head[2] += 60
				newS = head[2] - off_seconds
			else:
				print_error(Error.SUBTRACTION)
				exit()
		else:
			newS = head[2] - off_seconds

		if mill < off_mseconds:
			if newS > 0:
				newS -= 1
				mill += 1000
				newMS = mill - off_mseconds
			elif newM > 0:
				newM -= 1
				newS -= 59
				mill += 1000
				newMS = mill - off_mseconds
			elif newH > 0:
				newH -= 1
				newM += 59
				newS += 59
				mill += 1000
				newMS = mill - off_mseconds
			else:
				print_error(Error.SUBTRACTION)
				exit()

		else:
			newMS = mill - off_mseconds



	return newH, newM, newS, newMS





def msSum(x, y):
	out = int(x) + int(y)
	if out > 999:
		return int(int(out)/1000), int(out) - int(int(out)/1000) * 1000
	else:
		return 0, out


def sum(x, y):
	out = int(x) + int(y)
	if out > 59:
		return int(int(out)/60), int(out) - int(int(out)/60) * 60
	else:
		return 0, out

def formatTime(time):
	print time
	if len(str(time[0])) < 2:
		f_hours = "0" + str(time[0])
	else:
		f_hours = str(time[0])
	if len(str(time[1])) < 2:
		f_minutes = "0" + str(time[1])
	else:
		f_minutes = str(time[1])
	if len(str(time[2])) < 2:
		f_seconds = "0" + str(time[2])
	else:
		f_seconds = str(time[2])
	if len(str(time[3])) == 1:
		f_mseconds = "00" + str(time[3])
	elif len(str(time[3])) == 2:
		f_mseconds = "0" + str(time[3])	
	else:
		f_mseconds = str(time[3])	
	return f_hours + ":" + f_minutes + ":" + f_seconds + "," + f_mseconds


def print_error(err_type):

	appendix = " type strFix.py -h for help"

	if err_type == 1: 
		print "Invalid arguments," + appendix
	elif err_type == 2:
		print "Invalid offset," + appendix
	elif err_type == 3:
		print "Invalid filename," + appendix 
	elif err_type == 4:
		print "Offset is bigger than starting time, " + appendix
			
		

def printInstructions():
	print "Usage: strFix 'filename' 'offset'\nwhere 'filename' must be a valid path to a .str or .txt file and 'offset' must be in the form +xxhxxmxxsxxxms to add time or -xxhxxmxxsxxxms to subtract time (x it's a [0-9] digit)"
	print "For any information contact matteo(dot)luzzi(at)gmail(dot)com"			

class Error:

	ARGUMENTS = 1
	OFFSET = 2
	FILENAME = 3
	SUBTRACTION = 4

class GUI:

	def __init__(self, master):

		self.main_frame = Frame(master)
		self.main_frame.pack()

		self.filename = ""
		self.offset = ""

		self.file_opts = {}
		self.file_opts['filetypes'] = [('srt files', '*.srt')]


		# self.load_button = Button(self.main_frame, text="Load sub file", command=self.openfile)
		# self.load_button.grid(row=0, column=1)

		# self.textArea = Text(self.main_frame)
		# self.textArea.grid(row=1, column=2)

		# self.offset_frame = Frame(self.main_frame)
		# self.offset_frame.grid(row=0, column=2)

		# self.execute_button = Button(self.main_frame, text="Execute", command=self.execute)
		# self.execute_button.grid(row=0, column=3)
		
		self.inputFileTextArea = Text(self.main_frame)
		self.inputFileTextArea.grid(row=0, column=1)

		self.outputFileTextArea = Text(self.main_frame)
		self.outputFileTextArea.grid(row=0, column=2)

		# self.direction = Spinbox(self.offset_frame, values=("+", "-"))
		# self.direction.pack()

		# self.hh_label = Label(self.offset_frame, text="H offset")
		# self.hh_label.pack()

		# self.hh_offset = Spinbox(self.offset_frame, from_=0, to = 99)
		# self.hh_offset.pack()

		# self.hh_label = Label(self.offset_frame, text="M offset")
		# self.hh_label.pack()

		# self.mm_offset = Spinbox(self.offset_frame, from_=0, to = 99)
		# self.mm_offset.pack()

		# self.hh_label = Label(self.offset_frame, text="S offset")
		# self.hh_label.pack()

		# self.ss_offset = Spinbox(self.offset_frame, from_=0, to = 99)
		# self.ss_offset.pack()

		# self.hh_label = Label(self.offset_frame, text="MS offset")
		# self.hh_label.pack()

		# self.ms_offset = Spinbox(self.offset_frame, from_=0, to = 999)
		# self.ms_offset.pack()
		

	def createOffset(self):
	
		offset = self.direction.get()
		if len(self.hh_offset.get()) < 2:
			offset +=  "0" + self.hh_offset.get()
		else:
			offset += self.hh_offset.get()
		if len(self.mm_offset.get()) < 2:
			offset +=  "h0" + self.mm_offset.get()
		else:
			offset += "h" + self.mm_offset.get()
		if len(self.ss_offset.get()) < 2:
			offset +=  "m0" + self.ss_offset.get()
		else:
			offset += "m" + self.ss_offset.get()
		if len(self.ms_offset.get()) == 1:
			offset +=  "s00" + self.ss_offset.get()
		elif len(self.ms_offset.get()) == 2:
			offset +=  "s0" + self.ss_offset.get()
		else:
			offset += "s" + self.ms_offset.get()
		offset += "ms"



		if validateOffset(offset):	
			return offset
		else:
			print offset
			exit()
			


	def openfile(self):

		filename = askopenfilename(**self.file_opts)
		self.textArea.insert(INSERT, filename + " loaded\n")
		self.filename = filename

		f = open(self.filename, 'r')

		text = f.read()
		self.inputFileTextArea.insert(INSERT, text)

		print self.filename

	def execute(self):

		self.offset = self.createOffset()

		print self.offset
		if self.filename == "":
			self.textArea.insert(INSERT, "Aborted! missing filepath\n")

		else:
			outFile = fixFile(self.filename, self.offset)
			self.textArea.insert(INSERT, "Success! file fixed!\n")
			text = open(outFile, 'r').read()
			self.outputFileTextArea.insert(INSERT, text)






if __name__ == "__main__":

	# root = Tk()
	# root.title("strFix")

	# app = GUI(root)



	# root.mainloop()
	if len(sys.argv) == 3: 

		filename = sys.argv[1]
		offset = sys.argv[2]

		if not validateOffset(offset):
			print_error(Error.OFFSET)
			exit()

		if os.path.isfile(filename):
			fixFile(filename, offset)
		else:
			print_error(Error.FILENAME)

	elif len(sys.argv) == 2 and sys.argv[1] == "-h":
		
		printInstructions()
		exit()

	else:
		
		print_error(Error.ARGUMENTS)
		exit()




