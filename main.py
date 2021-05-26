#!/usr/bin/python

import shutil
import sys
import os
from pathlib import Path
import subprocess
import cv2
import re 
import glob
import argparse

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", required=True)
parser.add_argument("-f", "--filename", required=True)
args = parser.parse_args()

# For Natural Sort in filenames used in image paths
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
    
jpglist = Path(args.filename + "/out/").rglob('*.jpg')

#If path does not exist, proceed    
if not os.path.exists(args.filename):
    Path(args.filename + "/out").mkdir(parents=True, exist_ok=True)

    #Multiple tools to go from video to images of tabs, avoiding duplicates and bnw images
    downloader = "youtube-dl -o ./" + args.filename+ "/" +args.filename + " " + args.url
    cropper = "ffmpeg -i ./" + args.filename + "/" + args.filename + ".mkv -filter:v \"crop=1920:400:0:900\" ./" + args.filename + "/out.mkv"
    framer = "ffmpeg -i ./" + args.filename + "/out.mkv -filter:v fps=1 " + args.filename + "/out/out%02d.jpg"
    duper = "findimagedupes ./" + args.filename + "/out/ > ./" + args.filename + "/dupes.txt"

    for path in jpglist:
        bnwdetector = "convert " + str(path) + " -colorspace HSL -channel g -separate +channel -format \"%[fx:mean]\" info:"
        result = subprocess.check_output(bnwdetector, shell=True, text=True)
        if result == "0":
            os.remove(path)


    os.system(downloader)
    os.system(cropper)
    os.system(framer)
    os.system(duper)

    #Deleting duplicate images
    with open(args.filename + "/dupes.txt") as f:
        lines = []
        for line in f:
            line = line.strip()
            mylist = line.split(" ")
            mylist.sort(key=natural_keys)
            mylist.pop(0)
            for elements in mylist:
                os.remove(elements)

    #Making a list of final images to concatenate
    jpgArr = []
    for p in glob.glob(args.filename + "/out/*.jpg"):
        jpgArr.append(p)
    
    jpgArr.sort(key=natural_keys)
    cv_img = []
    for elem in jpgArr:
        n = cv2.imread(elem)
        cv_img.append(n)
    

    im_v = cv2.vconcat(cv_img)
    bigpath = args.filename + "/tabs.jpg"
    cv2.imwrite(bigpath, im_v)
    
    shutil.rmtree(args.filename + "/out/")
    os.remove(args.filename + "/out.mkv")
    os.remove(args.filename + "/dupes.txt")
else:
    print("Already exists, rare case. wtf.")