#!/usr/bin/env python
import cv2
import numpy as np
from picamera import PiCamera
from time import sleep
import math

def take_pictures(time_to_pause):
	with PiCamera() as camera:
		print("Taking dark photo")
		time.sleep(1)
		camera.capture('rpi_photo.jpg')
		print("Taking bright photo")
		time.sleep(time_to_pause)
		camera.capture('lit_photo.jpg')

class PillSegmenter:
	def __init__(self):
		self.original_image = None
		self.bright_image = None
		self.save_folder ='images'
		self.thresh_thresh = 120
		self.circle_thresh = 11
		self.debug_mode = True

	def threshold_image(self, high=255):
		img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY) # better in grayscale
		ret, thresh = cv2.threshold(img, self.thresh_thresh, high, 0)
		if self.debug_mode:
			cv2.imwrite(self.save_folder + '/thresh.jpg', thresh)
		return thresh

	def do_contours(self, thresh):
		contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
		contour_sorted = sorted(contours, key=cv2.contourArea)
		if self.debug_mode:
			new_img = self.original_image.copy()
			cv2.drawContours(new_img, contour_sorted, -1, (0, 255, 0))
			cv2.imwrite(self.save_folder+'/contours.jpg', new_img)
		return contour_sorted

	def find_circles(self, cs):
		contour_list = []
		for contour in cs:
			approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
			area = cv2.contourArea(contour)
			if ((len(approx) > self.circle_thresh) & (area > 10000) & (area < 300000) ):
				contour_list.append(contour)
                
		if self.debug_mode:
			new_img2 = self.original_image.copy()
			cv2.drawContours(new_img2, contour_list, -1, (0, 255, 0))
			cv2.imwrite(self.save_folder+'/circle_contours.jpg', new_img2)
		
		circles_sorted = sorted(contour_list, key=cv2.contourArea)
		return circles_sorted

	def draw_n_contours(self, circles_sorted, index):
		new_img3 = self.original_image.copy()
		i = 0

		while cv2.contourArea(circles_sorted[index-i]) > 120000:
			x, y, w, h = self.get_bounding_rect(circles_sorted[index-i])
			cropped = self.original_image.copy()[y:y+h, x:x+w]
			lit_cropped = self.bright_image.copy()[y:y+h, x:x+w]

			if self.debug_mode:
				cv2.drawContours(new_img3, circles_sorted, index-i, (0, 255, 0))
				cv2.imwrite(self.save_folder+'/biggest_contour' + str(i) +'.jpg', new_img3)
				cv2.imwrite(self.save_folder+'/cropped_pill' + str(i) + '.jpg', cropped)
			self.crop_circle(cropped, i, lit_cropped)
			i += 1
		return i

	def get_bounding_rect(self, contour):
		x,y,w,h = cv2.boundingRect(contour)
		return x, y, w, h

	def crop_circle(self, img, i, lit_img):
		gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)

		circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,400,
			param1=51,param2=30,minRadius=0,maxRadius=0)
		mask = np.zeros(img.shape[:3], np.uint8)
		x = circles[0,0,0]
		y = circles[0,0,1]
		r = circles[0,0,2]
		
		cv2.circle(mask,(x,y),int(r),(255,255,255),-1)
		xs = int(max(math.ceil(x-r), 0))
		xe = int(max(math.ceil(x+r), img.shape[0]))
		ys = int(max(math.ceil(y-r), 0))
		ye = int(max(math.ceil(y+r), img.shape[1]))

		mask_inv = cv2.bitwise_not(mask)
		out = cv2.add(img, mask_inv)
		lit_out = cv2.add(lit_img, mask_inv)
		f1 = out[ys:ye, xs:xe]
		f2 = lit_out[ys:ye, xs:xe]
		cv2.imwrite(self.save_folder+'/finalviacirclecrop'+str(i)+'.jpg', f1)
		cv2.imwrite(self.save_folder+'/lit_pill'+str(i)+'.jpg', f2)
        
	def crop_qr(self, thresh, xl=300, xh=1500, yl=1200, yh=800):
		og_quart = self.original_image.copy()[1400:, :1500]
		ogg = cv2.cvtColor(og_quart, cv2.COLOR_BGR2GRAY)
		#th = cv2.adaptiveThreshold(ogg, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 41, 5)
		__, th = cv2.threshold(ogg, 100, 255, 0)
		cv2.imwrite(self.save_folder + '/qr_code_thresh.jpg', th)
            
		contours = cv2.findContours(th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
		contour_sorted = sorted(contours, key=cv2.contourArea)
		index = -1

		while cv2.contourArea(contour_sorted[index]) > 10000:
			x = contour_sorted[index]
			index -= 1
            
		x,y,w,h=self.get_bounding_rect(x)
		qr_img = og_quart[y-30:y+h+30, x-30:x+w+30]
		cv2.imwrite(self.save_folder + '/qr_code.jpg', qr_img)
            

	def segment_pills(self, debug_mode=True):
		self.debug_mode=debug_mode
		print("Processing images")
		cv2.imwrite(self.save_folder+'/original_image.jpg', self.original_image)
#		self.bright_image = self.original_image # DELETE THIS
		thresh = self.threshold_image()
		self.crop_qr(thresh)
		cs = self.do_contours(thresh)
		circles_sorted = self.find_circles(cs)
		index = len(circles_sorted) - 1
		num_pills = self.draw_n_contours(circles_sorted, index)
		print("Found %i pill(s)" %num_pills)
		return num_pills







