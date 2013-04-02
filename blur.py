import numpy
import math

class Types:
    PIL = 0
    PYGAME = 1

def open(source, base_type=None):
    if base_type is None:
        try:
            return loadWithPIL(source)
        except ImportError:
            try:
                return loadWithPygame(source)
            except ImportError:
                raise ImportError("Could not import PIL or Pygame.")
    elif base_type == Types.PIL:
        return loadWithPIL(source)
    elif base_type == Types.PYGAME:
        return loadWithPygame(source)
    
    return None

def export(matrix, base_type=None):
    if base_type is None:
        try:
            return exportToPIL(matrix)
        except ImportError:
            try:
                return exportToPygame(matrix)
            except ImportError:
                raise ImportError("Could not import PIL or Pygame.")
    elif base_type == Types.PIL:
        return exportToPIL(matrix)
    elif base_type == Types.PYGAME:
        return exportToPygame(matrix)
    
    return None

def loadWithPIL(source):
    try:
        from PIL import Image
    except:
        raise ImportError("Could not import PIL.")
    else:
        image = Image.open(source)
        return BlurringMatrix(numpy.array(image, dtype='uint8'))

def loadWithPygame(source):
    try:
        import pygame
    except:
        raise ImportError("Could not import Pygame.")
    else:
        image = pygame.image.load(source)
        pygame.surfarray.use_arraytype("numpy")
        return BlurringMatrix(pygame.surfarray.array3d(image))
    
def exportToPIL(matrix):
    try:
        from PIL import Image
    except:
        raise ImportError("Could not import PIL.")
    else:
        return Image.fromarray(matrix.matrix.astype('uint8'))

def exportToPygame(matrix, surface=None):
    try:
        import pygame
    except:
        raise ImportError("Could not import Pygame.")
    else:
        if surface is None:
            surface = pygame.Surface(matrix.shape[0:2])
        pygame.surfarray.blit_array(surface, matrix.matrix.astype('uint8'))
        return surface

class BlurringMatrix:
    matrix = None
    pixels_per_degree = None
    
    def __init__(self, matrix, pixels_per_degree=None):
        self.matrix = matrix.astype('float64')
        self.pixels_per_degree = pixels_per_degree
    def calcPixelsPerDegree(self, resolution, display_size, visual_distance):
        pixel_size = (float(display_size[0]) / resolution[0], float(display_size[1]) / resolution[1])
        double_vdist = 2.0 * visual_distance
        to_radians = 180.0/math.pi
        degrees_per_pixel = (2.0*(math.atan(pixel_size[0]/double_vdist))*to_radians, 2.0*math.atan(pixel_size[1]/double_vdist)*to_radians)
        
        assert(degrees_per_pixel[0] == degrees_per_pixel[1])
        
        self.pixels_per_degree = 1.0 / degrees_per_pixel[0]
        
        return self #chainable method
    def copy(self):
        return BlurringMatrix(self.matrix.copy(), self.pixels_per_degree)
    def resolutionIsCalculated(self):
        return (self.pixels_per_degree is not None)
    
    """
    Applies a low pass blurring filter, allowing a maximum of the given cycles per degree of visual angle.
    """
    def applyLowPassFilter(self, cyclesPerDegree):
        if(not self.resolutionIsCalculated()):
            raise RuntimeError("The pixels_per_degree must be set before a low-pass filter can be applied.")
        
        if(self.matrix.shape[2] != 3):
            raise NotImplementedError("Filtering can only operate on RGB images (3-channel) at this time. Input has {0} channels.".format(self.matrix.shape[2]))
        
        rows, cols = self.matrix.shape[:2]
        
        (u, v) = dftuv(rows, cols)
        D = numpy.sqrt(u**2 + v**2)
        sigma = (self.pixels_per_degree * float(cyclesPerDegree)) / 2.0
        f = numpy.exp(-(D**2)/((sigma**2)))
        
        fftR = numpy.fft.fft2(self.matrix[:,:,0])
        fftG = numpy.fft.fft2(self.matrix[:,:,1])
        fftB = numpy.fft.fft2(self.matrix[:,:,2])
        
        lowFFTr = fftR*f;
        lowFFTg = fftG*f;
        lowFFTb = fftB*f;
        
        out = numpy.zeros(self.matrix.shape)
        out[:,:,0] = numpy.real(numpy.fft.ifft2(lowFFTr))
        out[:,:,1] = numpy.real(numpy.fft.ifft2(lowFFTg))
        out[:,:,2] = numpy.real(numpy.fft.ifft2(lowFFTb))
        
        return BlurringMatrix(numpy.clip(out, 0, 255).astype('float64'), self.pixels_per_degree)

def dftuv(m, n):
    u = numpy.arange(0, m)
    v = numpy.arange(0, n)
    
    idx = (u > m/2.0).nonzero()
    u[idx] = u[idx] - m
    idy = (v > n/2.0).nonzero()
    v[idy] = v[idy] - n
    
    [v,u] = numpy.meshgrid(v, u)
    return (u, v)
