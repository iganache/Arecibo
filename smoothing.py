import numpy as np
import rasterio
from scipy import signal
from scipy.ndimage import gaussian_filter


def smooth(file, outfile, n):
    
    inds = rasterio.open(file)
    data = inds.read(1)
    inds.close()
    
    
    # # averaging
#     mavg_filt = np.ones((n,n))/np.square(n)
#     avgdata = signal.convolve2d(data, mavg_filt)
    
    # # gaussian filtering
    avgdata = np.zeros_like(data)
    gaussian_filter(data, sigma=5, output=avgdata)
    
    outds = rasterio.open(outfile, 'w', driver='GTiff', 
                  height = avgdata.shape[0], 
                  width = avgdata.shape[1], 
                  count=1, 
                  crs = None, 
                  dtype = np.float32,
                  transform = None,
                  compress='lzw',
                  nodata = 9999)
    outds.write(avgdata, 1)
    


def main():
    file = "data2001/northS1gi4.tif"
    outfile = "data2001/northS1gi4_gau_sig5_avg.tif"
    n = 8
    
    smooth(file, outfile, n)
    
    
    
if __name__ == '__main__':
    main()
