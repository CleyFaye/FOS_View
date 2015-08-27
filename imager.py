#!/usr/bin/env python

from datahandle import Vault
from PIL import Image

def main():
    vault = Vault('data/Vault1.sav')
    image = Image.new('RGB', (800, 600))
    image.save('output.png', 'PNG')

if __name__ == '__main__':
    main()

