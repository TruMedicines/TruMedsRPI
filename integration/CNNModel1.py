import torch
from torch import nn
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
       
        #self.fc_dims = fc_dims
       
        self.layer1 = nn.Sequential(
            nn.Conv2d(1,16,kernel_size=5, stride=2, padding=2),
            nn.ReLU(inplace=True) )
           
        self.layer2 = nn.Sequential(
            nn.Conv2d(16,32,kernel_size=3, stride=2, padding=1),
            nn.ReLU(inplace=True) )
           
        self.encoded = nn.Sequential(
            nn.Conv2d(32,128,kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, padding=0, ceil_mode=False) )
           
        self.up1 = nn.Sequential(
            nn.Conv2d(128,128,kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=2) )
       
        self.up2 = nn.Sequential(
            nn.Conv2d(128,32,kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=2) )
       
        self.up3 = nn.Sequential(
            nn.Conv2d(32,16,kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=2) )
       
        self.decoded = nn.Sequential(
            nn.Conv2d(16,1,kernel_size=3, padding=1),
            nn.Sigmoid() )
       
        # conv fc
        #self.fc11 = nn.Linear(16384, 128) # mu
        #self.fc12 = nn.Linear(128, self.fc_dims) # logvar
       
        # deconv fc
        #self.fc2  = nn.Linear(128, 16384)
   
   
    def encode(self, x):
        y = self.layer1(x)
        y = self.layer2(y)
        enc = self.encoded(y)
        #print(enc.shape)
       
        #enc = enc.view(-1, 16384)
        #mu = self.fc11(enc)
        #logvar = self.fc12(enc)
        return enc
   
    def decode(self, z):
        #deconv_input = F.relu(self.fc2(z))
        deconv_input = z.view(-1, 128, 8, 16) # world models: [-1, 1, 1, 1024]
        y = self.up1(deconv_input)
        y = self.up2(y)
        y = self.up3(y)
        dec = self.decoded(y)
        return dec
   
    def reparameterize(self, mu, logvar):
        std = torch.exp(logvar * 0.5)
        eps = torch.rand_like(std)
        z = eps.mul(std).add(mu)
        return z
   
    def forward(self, x):
        enc = self.encode(x)
        #z = self.reparameterize(mu, logvar)
        dec = self.decode(enc)
        return dec, enc
