#!/usr/bin/env python
### A simple script to generate cube objects in simulation

__version__ = "0.1"

from PIL import (Image,
                 ImageDraw,
                 ImageFont
                 )
import io
import sys, os, getopt
from os.path import join as pjoin
from shutil import copyfile
from xml.etree import ElementTree as et

def generate_cube(name, r, g, b, a=None):
    """
    Takes input: alphabet, red, green, blue channels
    """
    if a:
        cube_name = '{}_{}'.format(name, a)
    else:
        cube_name = name

    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 200, encoding="unic")
    # text_width, text_height = verdana_font.getsize(alphabet)
    # create a blank canvas with extra space between lines
    canvas = Image.new('RGB', (256, 256), (r, g, b))

    # draw the text onto the text canvas, and use black as the text color
    draw = ImageDraw.Draw(canvas)
    if a:
        draw.text((70, 20), str(a), font=font, fill="#000000")

    # save the blank canvas to a file
    canvas.save('{}.png'.format(cube_name), 'PNG')

    urdf_name = '{}.urdf'.format(cube_name)
    copyfile('templates/cube-small.urdf', urdf_name)

    new_mtl('templates/cube.mtl', cube_name)
    new_obj('templates/cube.obj', cube_name)

    tree = et.parse(urdf_name)
    element = tree.find('.//mesh')
    element.set('filename', '{}.obj'.format(cube_name))
    tree.write(urdf_name)

def new_mtl(origin, new):
    f1 = open(origin, 'r')
    f2 = open('{}.mtl'.format(new), 'w')
    for line in f1:
        f2.write(line.replace('cube.png', '{}.png'.format(new)))
    f1.close()
    f2.close()

def new_obj(origin, new):

    f1 = open(origin, 'r')
    f2 = open('{}.obj'.format(new), 'w')
    for line in f1:
        f2.write(line.replace('mtllib cube.mtl',
            'mtllib {}.mtl'.format(new)))
    f1.close()
    f2.close()

def run(argv):

    # Assume 200 users
    r, g, b = 255, 255, 255
    # One minute of data
    a = None

    try:
        opts, args = getopt.getopt(argv,
                                   'ha:r:g:b:n:', ['help', 'alphabet=', 'red=', 'green=', 'blue=', 'name='])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            sys.exit(0)
        elif opt in ('-r', '--red'):
            r = int(arg)
        elif opt in ('-a', '--alphabet'):
            a = arg
        elif opt in ('-g', '--green'):
            g = int(arg)
        elif opt in ('-b', '--blue'):
            b = int(arg)
        elif opt in ('-n', '--name'):
            n = arg
    generate_cube(n, r, g, b, a)

if __name__ == '__main__':
    run(sys.argv[1:])
