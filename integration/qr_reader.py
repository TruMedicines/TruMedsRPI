from pylibdmtx import pylibdmtx
import cv2
import numpy as np
import imutils
import json
import os
from shutil import copyfile

QRDB = 'json/qrdb.json'

def find_code(src):
	
	results = []
	resultnames = ["thresh", "eroded", "dilated", "rotated1", "rotated2", "original"]

	# orig, rotated, sharp

	##### CORRECT ROTATION #####
	im = cv2.imread(src)
	im = cv2.flip(im, 1)
	gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	__, th1 = cv2.threshold(gray, 100, 255, 0)
	
	ker = np.ones((3,3))
	er = cv2.erode(th1, ker, iterations=3)
	contours = cv2.findContours(er, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
	contour_sorted = sorted(contours, key=cv2.contourArea)
	rect = cv2.minAreaRect(contour_sorted[-2])
	print(rect)
	angle = rect[2]
	
	rot = imutils.rotate(im, angle)
	rot2 = imutils.rotate(im, angle*-1)
		
	#### THRESHOLD ####
	gray = cv2.cvtColor(rot, cv2.COLOR_BGR2GRAY)
	__, th1 = cv2.threshold(gray, 100, 255, 0)
	
	#### ERODE ####
	ker = np.ones((3,3))
	er = cv2.erode(th1, ker)
	
	### DILATE ####
	dil = cv2.dilate(th1, ker)
	
	results.append(cv2.resize(th1, (0,0), fx=.5, fy=.5))
	results.append(cv2.resize(er, (0,0), fx=.5, fy=.5))
	results.append(cv2.resize(dil, (0,0), fx=.5, fy=.5))
	results.append(cv2.resize(rot, (0,0), fx=.5, fy=.5))
	results.append(cv2.resize(rot2, (0,0), fx=.5, fy=.5))
	results.append(cv2.resize(im, (0,0), fx=.5, fy=.5))

	for i, value in enumerate(results):
		code = "none"
		cv2.imwrite('images/' + resultnames[i] + '.jpg', value)
		print("testing " + resultnames[i])
		dec = pylibdmtx.decode(value)
		if len(dec) > 0:
			code = dec[0].data.decode("utf-8")
			print(resultnames[i], code)
			return code
		print("  failed")


def write_to_file(src, pill_num):
	code = find_code(src)
	in_db = False
	data = None
	if pill_num > 1:
		data = prep_file(QRDB)
	
	if data:
		for pill in data:
			if code == pill["Code"]:
				in_db = True
	
	if not in_db:	
		d = {"Pill Number" : pill_num, "Code" : code}
		f = open(QRDB, "a")
		if os.stat(QRDB).st_size == 0:
			f.write("[\n")
		else:
			f.write(",\n")
		f.writelines(json.dumps(d, indent=2))
		f.close()
	return code, in_db

def read_file(src):
	code = find_code(src)
	
	data = prep_file(QRDB)
	dic_code = "not found"
	num = "not found"
	
	for pill in data:
		dic_code = pill["Code"]
		if code == dic_code:
			num = str(pill["Pill Number"])
			print("Is this pill " + num)
			return dic_code, num
	
	return dic_code, num
			
			
def prep_file(src):
	
	if os.stat(src).st_size == 0:
		data = None
	else:
		copyfile(src, "json/tmp.json")
		f = open("json/tmp.json", "a")
		f.write(']')
		f.close()
		with open("json/tmp.json") as jfile:
			data = json.load(jfile)
	os.remove("json/tmp.json")
	return data
