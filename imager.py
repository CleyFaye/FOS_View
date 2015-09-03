#!/usr/bin/env python

from datahandle import Vault
from PIL import Image, ImageDraw

def getCoordinates(col, row, width, config):
    x1 = col * (config['roomWidth'] + config['roomSpaceX']) + config['roomOffsetX']
    x2 = x1 + width * (config['roomWidth'] + config['roomSpaceX']) - config['roomSpaceX']
    y1 = row * (config['roomHeight'] + config['roomSpaceY']) + config['roomOffsetY']
    y2 = y1 + config['roomHeight']
    return ((x1, y1), (x2, y2))

def enlargeRect(rect, point):
    print rect
    print point
    if point[0] < rect[0]:
        rect[0] = point[0]
    if point[0] > rect[2]:
        rect[2] = point[0]
    if point[1] < rect[1]:
        rect[1] = point[1]
    if point[1] > rect[3]:
        rect[3] = point[1]

def main(config):
    vault = Vault('data/Vault1.sav')
    rect = [0, 0, 0, 0]
    for room in vault.vault.rooms:
        pos = getCoordinates(room.col, room.row, room.getRoomWidth(), config)
        enlargeRect(rect, pos[0])
        enlargeRect(rect, pos[1])
    for rock in vault.vault.rocks:
        pos = getCoordinates(rock.c, rock.r, 1, config)
        enlargeRect(rect, pos[0])
        enlargeRect(rect, pos[1])
    img = Image.new('RGB', (rect[2], rect[3]))
    drawer = ImageDraw.Draw(img)
    for room in vault.vault.rooms:
        pos = getCoordinates(room.col, room.row, room.getRoomWidth(), config)
        drawer.rectangle(pos, fill='red', outline='white')
    for rock in vault.vault.rocks:
        pos = getCoordinates(rock.c, rock.r, 1, config)
        drawer.ellipse(pos, outline = 'white', fill='gray')
    img.save('output.png', 'PNG')

    with open('test.dot', 'w') as out:
        out.write('digraph A {\n')
        for dweller in vault.dwellers.dwellers:
            out.write('dweller_%s [label="%s"];\n' % (dweller.serializeId, dweller.getFullName()))
            parents = dweller.relations.getParents()
            if parents:
                out.write('dweller_%s -> dweller_%s;\n' % (parents[0].serializeId, dweller.serializeId))
                out.write('dweller_%s -> dweller_%s;\n' % (parents[1].serializeId, dweller.serializeId))
        out.write('}\n')

if __name__ == '__main__':
    config = {
            'roomWidth': 30,
            'roomHeight': 60,
            'roomSpaceX': 3,
            'roomSpaceY': 3,
            'roomOffsetX': 0,
            'roomOffsetY': 0
            }
    main(config)

