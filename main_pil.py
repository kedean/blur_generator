import blur
import time
import os
import argparse
import numpy

from PIL import PngImagePlugin, BmpImagePlugin, JpegImagePlugin, TiffImagePlugin, GifImagePlugin

parser = argparse.ArgumentParser(description="Takes in a file and applies a low-pass blur filter. Supported formats are tif, jpg, png, bmp, and gif.")
parser.add_argument("cycles_per_degree", type=float, help="The lower bound cycles per degree of the filter.")
parser.add_argument("source_file", help="Filename of the image to apply the filter to.")
parser.add_argument("destination_file", nargs="?", default=None, help="Filename to write the filtered image to. If not given, the image is display on screen.")
parser.add_argument("-concurrent, -c", dest="concurrent", action="store_true", help="If set, the blur will be generated concurrently. Only supported under Python 3.x and up.")

args = parser.parse_args()

image_prompt = "Filename or directory to blur: "
cpd_prompt = "CPD Bound: "
save_prompt = "Filename or directory to save to: "
saving_error_msg = "Could not save to the indicated path, please make sure the output filename is a valid image format. Exiting."

cpd = args.cycles_per_degree
filename = args.source_file
savedir = args.destination_file
saved_to_dir = False

if savedir is not None:
    if os.path.isfile(savedir):
        saved_to_dir = False
    elif os.path.isdir(savedir):
        saved_to_dir = True
    else:
        if "." not in savedir:
            saved_to_dir = True
            try:
                os.makedirs(savedir)
            except:
                print("Could not create the destination directory. Exiting.")
                exit(-1)

try:
    generator = blur.open(filename, blur.Types.PIL)
except IOError:
    print("Could not open {0} as an image. Exiting.".format(filename))
    exit(-1)

print("Applying filter of {0:f} cycles per degree to {1}".format(cpd, filename))

generator.calcPixelsPerDegree((1024, 768), (36, 27), 61)
try:
    generator = generator.lowPassFilter(cpd, concurrent=args.concurrent)
except ImportError:
    print("Unable to import concurrency libraries. Ensure you are using Python 3.x or higher. Continuing normally.")
    generator = generator.lowPassFilter(cpd, concurrent=False)
output = blur.exportToPIL(generator)

if savedir is not None:
    if saved_to_dir:
        savepath = os.path.join(savedir, filename)
        print("Saving {0} to {1}".format(filename, savepath))
        try:
            output.save(savepath)
        except:
            print(saving_error_msg)
            exit(-1)
    else:
        print("Saving {0}".format(savedir))
        try:
            output.save(savedir)
        except:
            print(saving_error_msg)
            exit(-1)
else:
    output.show()
