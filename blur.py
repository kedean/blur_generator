import numpy

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
        return numpy.array(image, dtype='uint8')

def loadWithPygame(source):
    try:
        import pygame
    except:
        raise ImportError("Could not import Pygame.")
    else:
        image = pygame.image.load(source)
        pygame.surfarray.use_arraytype("numpy")
        return pygame.surfarray.array3d(image)
    
def exportToPIL(matrix):
    try:
        from PIL import Image
    except:
        raise ImportError("Could not import PIL.")
    else:
        return Image.fromarray(matrix)

def exportToPygame(matrix, surface=None):
    try:
        import pygame
    except:
        raise ImportError("Could not import Pygame.")
    else:
        if surface is None:
            surface = pygame.Surface(matrix.shape[0:2])
        pygame.surfarray.blit_array(surface, matrix)
        return surface


"""
Applies a low pass blurring filter, allowing a maximum of the given cycles per degree of visual angle.
"""
def lowPassFilter(self, matrix, cyclesPerDegree):
    pass


"""
Cuts out a circular window of the given radius (in pixels).
If no position is specified, the window is placed at the image center.
"""
def cutWindow(self, matrix, radius, position=None):
    if position is None:
        position = BlurGenerator.CENTER
    pass
    
