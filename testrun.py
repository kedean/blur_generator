import blur
import pygame
import time

pygame.init()
disp = pygame.display.set_mode((1024, 768))
cpd = None

try:
    cpd = raw_input("CPD Bound: ")
except:
    cpd = input("CPD Bound: ")

try:
    cpd = float(cpd)
except:
    print("CPD must be a valid decimal number.")
else:
    image = ""
    try:
        image = raw_input("Path of image: ")
    except:
        image = input("Path of image: ")
    print("")
    s = time.time()
    gen = blur.open(image, blur.Types.PYGAME)
#    print "loading took {0}".format((time.time() - s) * 1000.0)
    s2 = time.time()
    gen.calcPixelsPerDegree((1024, 768), (36, 27), 61)
#    print "calc took {0}".format((time.time() - s2) * 1000.0)
    s2 = time.time()
    gen =  gen.applyLowPassFilter(cpd, concurrent=True)
    print("filter took {0}".format((time.time() - s2) * 1000.0))
    s2 = time.time()
    out = blur.exportToPygame(gen)
#    print "export took {0}".format((time.time() - s2) * 1000.0)
    s2 = time.time()
    disp.blit(out, (0,0))
    pygame.display.flip()
#    print "blit took {0}".format((time.time() - s2) * 1000.0)
#    print "all took {0}".format((time.time() - s) * 1000.0)
    running = True
    while(running):
        pygame.display.flip()
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False
            elif evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_ESCAPE:
                    running = False
                    
