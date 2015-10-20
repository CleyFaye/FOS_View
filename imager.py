#!/usr/bin/env python

import argparse
from fosfile import Vault
from PIL import Image, ImageDraw

def getCoordinates(col, row, width, config):
    x1 = col * (config['roomWidth'] + config['roomSpaceX']) + config['roomOffsetX']
    x2 = x1 + width * (config['roomWidth'] + config['roomSpaceX']) - config['roomSpaceX']
    y1 = row * (config['roomHeight'] + config['roomSpaceY']) + config['roomOffsetY']
    y2 = y1 + config['roomHeight']
    return ((x1, y1), (x2, y2))

def enlargeRect(rect, point):
    if point[0] < rect[0]:
        rect[0] = point[0]
    if point[0] > rect[2]:
        rect[2] = point[0]
    if point[1] < rect[1]:
        rect[1] = point[1]
    if point[1] > rect[3]:
        rect[3] = point[1]

def main(config):
    vault = Vault(config['input'])
    rect = [0, 0, 0, 0]
    for room in vault.vault.rooms:
        pos = getCoordinates(room.col, room.row, room.getRoomWidth(), config)
        enlargeRect(rect, pos[0])
        enlargeRect(rect, pos[1])
    for rock in vault.vault.rocks:
        pos = getCoordinates(rock.c, rock.r, 2, config)
        enlargeRect(rect, pos[0])
        enlargeRect(rect, pos[1])
    img = Image.new('RGB', (rect[2], rect[3]))
    drawer = ImageDraw.Draw(img)
    for room in vault.vault.rooms:
        pos = getCoordinates(room.col, room.row, room.getRoomWidth(), config)
        drawer.rectangle(pos, fill='red', outline='white')
    for rock in vault.vault.rocks:
        pos = getCoordinates(rock.c, rock.r, 2, config)
        drawer.ellipse(pos, outline = 'white', fill='gray')
    img.save(config['output'], 'PNG')

def parseCli():
    parser = argparse.ArgumentParser(description = 'Produce a picture showing the rooms layout')
    parser.add_argument('--input', type=argparse.FileType('rb'), required=True, help='Path to the vault file')
    parser.add_argument('--output', type=argparse.FileType('wb'), default='output.png', help='Path for the output PNG file')
    parser.add_argument('--roomWidth', type=int, default=30, help='Width of an elevator, in pixel (=1/3 or a room)')
    parser.add_argument('--roomHeight', type=int, default=60, help='Height of a room, in pixel')
    parser.add_argument('--roomSpaceX', type=int, default=3, help='Horizontal spacing between rooms')
    parser.add_argument('--roomSpaceY', type=int, default=3, help='Vertical spacing between rooms')
    parser.add_argument('--roomOffsetX', type=int, default=0, help='X Offset to start putting the rooms on the output')
    parser.add_argument('--roomOffsetY', type=int, default=0, help='Y Offset to start putting the rooms on the output')
    return vars(parser.parse_args())

if __name__ == '__main__':
    main(parseCli())

