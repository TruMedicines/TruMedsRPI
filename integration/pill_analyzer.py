import cv2
import numpy as np
from pylibdmtx import pylibdmtx
import torch
from torch import nn
from torchvision import transforms
from torch.autograd import Variable
import matplotlib.pyplot as plt
import time
import Cartesian2Polar
import CNNModel1
from PIL import Image
import pickle
from sklearn.neighbors import NearestNeighbors



class PillAnalyzer:
    def __init__(self):
        self.qr_image = None
        self.encoder = self.load_model()
        self.target_image_size = (64,128)
        self.transform = transforms.Compose([transforms.Resize(self.target_image_size),
                                            transforms.Grayscale(),
                                        transforms.ToTensor()])
        self.image_encoding_dict = {}
        self.image_filename_dict = {}
        self.database = []
        self.pill_index = 0
        self.nbrs = None
        self.database_created = False
    
    def decode_qr(self):
        dec = pylibdmtx.decode(self.qr_image)
        return dec
	    
    def load_model(self, model_name='models/state_dict1.pt'):
        print("Loading model")
        t0 = time.time()
        model = CNNModel1.CNN()
        model.load_state_dict(torch.load(model_name))
        model.eval()	
        t1 = time.time()
        print("Model loaded in: ", t1-t0)
        return model
		
    def get_encoding_from_src(self, src):
        return self.encode(self.convert_for_encoding(self.flatten(src)), self.encoder)
		
    def flatten(self, src):
        im = Image.open(src)
        im = im.resize((222,225))
        pim = Cartesian2Polar.project_cartesian_image_into_polar_image(im, origin=None)
        crop_height=min(150,pim.height)
        crop_width=min(10000,pim.width)
        cropped_polar_im = pim.crop(box=(0,0,crop_width,crop_height))
        return cropped_polar_im
	
    def convert_for_encoding(self, img):
        image = self.transform(img).float() # use the same transform as the test/train data
        image = Variable(image, requires_grad=True)
        image = image.unsqueeze(0) # necessary for the model to analyze the image
        return image
	
    def encode(self, img, trained_model):
        d,e = trained_model(img)
        a = nn.AvgPool2d((8,16))(e)
        a = a.squeeze()
        npa = a.detach().numpy()
        return npa
        
    def add_to_dict(self, enc):
        self.image_encoding_dict[self.pill_index] = enc
        
    def database_from_dict(self):
        i = 0
        for key, value in self.image_encoding_dict.items():
            self.image_filename_dict[i] = key
            self.database.append(value)
            i = i+1
            
    def create_knn(self):
        self.nbrs = NearestNeighbors(n_neighbors=2, algorithm='brute').fit(self.database)
        self.database_created = True
        
    def get_database_match(self, enc):
        enc = np.expand_dims(enc, axis=0)
        dist, ind = self.nbrs.kneighbors(enc)
        guess = ind[0,0]
        a = self.image_filename_dict[guess]
        return a, dist
        
    
