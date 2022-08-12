#!/usr/bin/env python

from PIL import Image
import argparse

# Usage: image-to-ascii.py [ -r ] [ IMAGE FILE ]

#CHARLIST = ["@","%","#","*","+","=","-","/","."," "]
#CHARLIST = ["@","#","$","%","&","8","E","H","W","0","*","F","L","T","w","h","e","o","c","t","f","l","~","+","=","-","."," "," "]
CHARLIST = ["@","#","$","%","&","8","B","M","W","*","m","w","q","p","d","b","k","h","a","o","Q","0","O","Z","X","Y","U","J","C","L","t","f","j","z","x","n","u","v","c","r","[","]","{","}","1","(",")","|","\\","/","?","I","l","!","i","<",">","+","_","-","~",";","\"",":","^",",","`","'","."," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "]

# Resize image according to new width
def resize_img(img, new_width):
    width, height = img.size
    ratio = height / width
    new_height = int(new_width * ratio) // 2
    return img.resize((new_width, new_height))

# Convert image to greyscale
def greyscale(img):
    grey_img = img.convert("L")
    return grey_img

# Map pixel data to character list
def pixels_to_ascii(img):
    pixels = img.getdata()
    grades = -(-256 // len(CHARLIST))
    chars = "".join([CHARLIST[pixel // grades] for pixel in pixels])
    return chars

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='image-to-ascii.py', description='Converts images to ascii art.')
    parser.add_argument('-r', '--reverse', action='store_true', help='Color Negative: Reverses the character list.')
    parser.add_argument('-w', '--width', default=125, type=int, help='Specify desired character width of ascii art.')
    parser.add_argument('path', help='Path to image file. Use jpg/png files for best results.')
    args = parser.parse_args()

    if args.reverse:
        CHARLIST.reverse()
    width = args.width

    path = args.path
    try:
        img = Image.open(path)
        img.load()
    except:
        print(f"{path} is an invalid path.")

    # Convert image to ascii
    new_img_data = pixels_to_ascii(greyscale(resize_img(img, width)))

    # format
    pixel_count = len(new_img_data)
    ascii_img = "\n".join(new_img_data[i:(i+width)] for i in range(0, pixel_count, width))

    print(ascii_img)
