# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 20:39:54 2020

@author: Indujaa
"""

import numpy as np
import os
import re
import matplotlib.pyplot as plt
from PIL import Image
import rasterio
from scipy import signal


def getValue(line, var):
    expr = var+" = \w+"
    result = re.findall(expr, line)[0]
    val = int(result.split('=')[-1])
    return val


def getDataInfo(file):
    ### Get byte offset of data 
    f = open(file, 'rb')
    i = 1
    while i > 0:
        l = f.readline()
        try: 
            line = l.decode("utf-8")
            if "xnum" in line:
                ncols = getValue(line, "xnum")
            if "ynum" in line:
                nrows = getValue(line, "ynum")
            byte_offset = f.tell()
        except: 
            break  
    f.close()
    return byte_offset, nrows, ncols


def extractData(file, byteoffset, nrows, ncols):
    # data = np.fromfile(file, dtype=np.float32, offset=byte_offset).reshape((nrows,ncols))               ### don't use - reads in as little endian
    
    num_data_bytes=os.path.getsize(file)
    ### Sepcify big endian float data type
    dt = np.dtype("float32")
    dt = dt.newbyteorder('>')
    
    with open(file,'rb') as fin:
        header = fin.read(byteoffset)
        data_str = fin.read(num_data_bytes)
        # data_arr = np.fromstring(data_str, dtype='>f4').reshape((nrows,ncols))                           ### don't use - numpy fromstring is deprecated
        data_arr = np.frombuffer(data_str, dtype=dt).reshape((nrows,ncols))
        # data_tuple = struct.unpack('f',data_str)
#     return 10 * np.log10(data_arr)
    return data_arr
    

def main():
    S1file = "data1999/north99.S1.gi32"
    S2file = "data1999/north99.S2.gi32"
    S3file = "data1999/north99.S3.gi32"
    S4file = "data1999/north99.S4.gi32"
    
    files = [S1file, S2file, S3file, S4file]
    
    _, nrows, ncols = getDataInfo(S1file)
    data = np.zeros((4, nrows, ncols), dtype = np.float32)
    
    for i, file in enumerate(files):

        headeroffset, nrows, ncols = getDataInfo(file)
        data[i, :, :] = extractData(file, headeroffset, nrows, ncols)
#         print(np.count_nonzero(data[i, :, :] != np.nan))

#     plt.imshow(data)
#     plt.show()


    outds = rasterio.open("/home/indujaa/Arecibo/data1999/northS1gi32.tif", 'w', driver='GTiff', 
                  height = nrows, 
                  width = ncols, 
                  count=1, 
                  crs = None, 
                  dtype = np.float32,
                  transform = None,
                  compress='lzw',
                  nodata = 9999)
    outds.write(data[0], 1)
    
    
    cpr = np.zeros_like(data[0])
    dlp = np.zeros_like(data[0])
    
    cond = np.abs(data[0])!= np.inf
    
    cpr[cond] = np.abs(data[0][cond]-data[3][cond]) / (data[0][cond]+data[3][cond])
    cpr[cpr>10]= 1
    cpr[cpr<0]= 0
    outds = rasterio.open("/home/indujaa/Arecibo/data1999/northCPRgi32.tif", 'w', driver='GTiff', 
                  height = nrows, 
                  width = ncols, 
                  count=1, 
                  crs = None, 
                  dtype = np.float32,
                  transform = None,
                  compress='lzw',
                  nodata = 9999)
    outds.write(cpr, 1)
    print(np.nanmin(cpr), np.nanmax(cpr), np.nanmean(cpr))
    
    dlp[cond] = np.sqrt(data[1][cond]**2 + data[2][cond]**2) / data[0][cond]
    dlp[dlp>1] = 1
    dlp[dlp<0] = 0
    outds = rasterio.open("/home/indujaa/Arecibo/data1999/northDLPgi32.tif", 'w', driver='GTiff', 
                  height = nrows, 
                  width = ncols, 
                  count=1, 
                  crs = None, 
                  dtype = np.float32,
                  transform = None,
                  compress='lzw',
                  nodata = 9999)
    outds.write(dlp, 1)
    print(np.nanmin(dlp), np.nanmax(dlp), np.nanmean(dlp))
#     plt.imshow(dlp)
#     plt.show()

if __name__ == '__main__':
    main()
