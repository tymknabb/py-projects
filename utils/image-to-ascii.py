#!/usr/bin/env python

from PIL import Image
import argparse

# Usage: image-to-ascii.py [ -r ] [ IMAGE FILE ]

BRT_INTERVAL = 5
charlist = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '.', "'", '`', ',', '^', ':', '"', ';', '~', '-', '_', '+', '>', '<', 'i', '!', 'l', 'I', '?', '/', '\\', '|', ')', '(', '1', '}', '{', ']', '[', 'r', 'c', 'v', 'u', 'n', 'x', 'z', 'j', 'f', 't', 'L', 'C', 'J', 'U', 'Y', 'X', 'Z', 'O', '0', 'Q', 'o', 'a', 'h', 'k', 'b', 'd', 'p', 'q', 'w', 'm', '*', 'W', 'M', 'B', '8', '&', '%', '$', '#', '@']

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
    grades = -(-256 // len(charlist))
    chars = "".join([charlist[pixel // grades] for pixel in pixels])
    return chars

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='image-to-ascii.py', description='Converts images to ascii art.')
    parser.add_argument('-r', '--reverse', action='store_true', help='Photo negative: Reverses the character list. Higher brightness levels will make the image dimmer.')
    parser.add_argument('-w', '--width', default=125, type=int, help='Specify desired character width of ascii art. Default: 125.')
    parser.add_argument('-b', '--brightness', default=0, type=int, choices=range(0,11), help='Specify desired brightness level from 0-10 inclusive. Default: 0.')
    parser.add_argument('path', help='Path to image file. Use jpg/png files for best results.')
    args = parser.parse_args()

    if args.reverse:
        charlist.reverse()
    width = args.width

    for idx in range(args.brightness):
        for idx in range(BRT_INTERVAL):
            del charlist[0]

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
