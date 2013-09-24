import blur
import math
import numpy as np
import pygame
import time
import os
import argparse

#creates a list of samples for drawing the window. The first item in the list is the expected cpd, the rest are distributed along a curve
#for maximum effectiveness (low cpd images are easier to distinguish than high cpd images of the same cpd apart)
def make_window_prereqs(cpd, filename, num_samples=7, concurrent=False):
    try:
        generator = blur.open(filename, blur.Types.PYGAME)
    except IOError:
        print("Could not open {0} as an image. Exiting.".format(filename))
        exit(-1)
    generator.calcPixelsPerDegree((1024, 768), (36, 27), 61)

    cpd_values = [value / 100.0 for value in range(4000, 50, -1)]
    num_valid = sum([1 for value in cpd_values if value > cpd])
    
    samples = [cpd]
    
    for x in range(0, num_samples+1):
        y = num_valid * math.sqrt((1 - ((x*x) / float(num_samples*num_samples))))
        if int(y) < len(cpd_values):
                samples.append(cpd_values[int(y)])

    maker = generator.lowPassFilterBatch(samples, concurrent=concurrent, supress=True)

    return [blur.exportToPygame(s) for s in maker]

#Given a screen, list of samples, radius, and position, a clear window is drawn with a gradient edge
def window(screen, samples, window_radius, position):
    (pos_x, pos_y) = position

    radius = window_radius - (len(samples) * 2) #start the radius as smaller than the real radius, it will work out

    #Set up the initial values of the output surface.
    #For efficiency we pass in the actual screen as an argument, instead we could initialize a new surface and draw and return that
    screen.set_colorkey((0,0,0)) #colorkey is the replaced value
    screen.blit(samples[-1], (pos_x - radius, pos_y - radius), (pos_x - radius, pos_y - radius, radius*2, radius*2)) #this copies only the relavent portion of the clearest image. Since its the smallest, the smaller square comes out

    #loop over each sample but the blurriest, draw a circle of transparency, and paste it over the output surface
    for index in range(2, len(samples) - 1):
        radius += 2
        dubradius = radius*2
        noutput = pygame.Surface((dubradius, dubradius)) #needs a new surface for a) effiency and b) so that the samples are not altered
        noutput.blit(samples[-index], (0,0), (pos_x - radius, pos_y - radius, dubradius, dubradius)) #again only copy the relavent area, its alot faster than the whole thing
        noutput.set_colorkey((0,0,0), pygame.RLEACCEL)
        pygame.draw.circle(noutput, (0,0,0), (radius, radius), radius) #since the box is only radius*2 in each dimension, the circle is positioned at its center, or (radius, radius)
        screen.blit(noutput, (pos_x - radius, pos_y - radius))

    #now do it again for the blurriest image, samples[0], except this time the entire image is used
    radius += 2
    noutput = samples[0].copy() #thus we copy instead of blitting
    pygame.draw.circle(noutput, (0,0,0), position, radius) #and the circle is now at the input position, since its full sized instead of a cutout
    noutput.set_colorkey((0,0,0), pygame.RLEACCEL)
    screen.blit(noutput, (0,0))

def main():
    parser = argparse.ArgumentParser(description="Takes in a file and applies a low-pass blur filter. Supported formats are tif, jpg, png, bmp, and gif.")
    parser.add_argument("cycles_per_degree", type=float, help="The lower bound cycles per degree of the filter.")
    parser.add_argument("source_file", help="Filename of the image to apply the filter to.")
    parser.add_argument("-concurrent, -c", dest="concurrent", action="store_true", help="If set, the blur will be generated concurrently. Only supported under Python 3.x and up.")

    args = parser.parse_args()

    cpd = args.cycles_per_degree
    filename = args.source_file

    pygame.init()

    samples = make_window_prereqs(cpd, filename, concurrent=args.concurrent)
    
    screen = pygame.display.set_mode((1024,768))

    screen.blit(samples[0], (0,0))

    running = True
    frame_times = []
    print("average frame time: 0ms")
    while running:
        t1 = time.time()
        window(screen, samples, 300, pygame.mouse.get_pos())
        t2 = time.time()
        frame_times.append((t2 - t1) * 1000.0)
        pygame.display.flip()
        
        print("\raverage frame time: {0}ms".format(sum(frame_times)/len(frame_times)))

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and (e.key == pygame.K_q or e.key == pygame.K_ESCAPE):
                running = False
            elif e.type == pygame.QUIT:
                running = False

if __name__ == "__main__":
    main()