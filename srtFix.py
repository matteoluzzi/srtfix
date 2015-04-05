#!/usr/bin/env python

import sys
import os
import re
import argparse


def fixFile(filepath, offset):

		print "Goint to modify the time of " + filepath + " by this offset " + offset + "\n"

		with open(filepath, 'r') as input:
			with open(createOutputFileName(filepath), 'w') as output:
				file = input.read()
				off = parseOffset(offset)
				blocks = file.split("\n")
				for line in blocks:
					#print line
					if keyStructure(line):
							start, end = line.split(" --> ")
							#print "off, ", off
							newStart = modifyTime(start, off)
							newEnd = modifyTime(end, off)
							#print newStart, newEnd
							output.write(formatTime(newStart) + " --> " + formatTime(newEnd) + "\n")
					else:
						output.write(line + "\n")
		#return createOutputFileName(filepath)
		print "conversion completed! the output file is " + createOutputFileName(filepath)


def createOutputFileName(inputPath):
	head, tail = os.path.splitext(inputPath)
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
			
class Error:

	ARGUMENTS = 1
	OFFSET = 2
	FILENAME = 3
	SUBTRACTION = 4

if __name__ == "__main__":


	parser = argparse.ArgumentParser()

	
	parser.add_argument("filename", help="valid path to the .srt or .txt file to modify")
	parser.add_argument("offset", help="valid offset written in the form of +xxhxxmxxsxxxms to add time or -xxhxxmxxsxxxms to subtract time (x it's a [0-9] digit)")
	args = parser.parse_args()
    
	filename = args.filename
	offset = args.offset

	if not validateOffset(offset):
		print_error(Error.OFFSET)
 		exit()

	if os.path.isfile(filename):
 		fixFile(filename, offset)
 	else:
 		print_error(Error.FILENAME)
 		exit()



