'''
The .mpd file is a level/map hex file.\n
The bits of the file (e.g: x64, x32) is the length (X) of the level.\n
How we will know this is that the first 8 bytes is a UInt64 (Unsigned x64 integer), representing the length.\n
The height of the level (Y) is when the X chunk loops back.\n
The file is compressed in the bz2 format at max compression.
'''
import pygame
import bz2
import os
pygame.init()

def ReadLevel(level):
    '''
    Returns readable level data from a file.
    level = open('yourFile.mpd', 'rb')
    '''
    level = bz2.decompress(level.read()).hex()
        
    # Extract length from the first 16 bytes
    length = int.from_bytes(bytes.fromhex(level[:16]), 'little', signed=False) * 2
    
    readLevel = []
    chunk = []
    byte = ''
    
    for i in range(16, len(level)): # Start from the 17th character
        byte += level[i]
        if len(byte) == 2: # Once we have 2 characters (1 byte)
            chunk.append(int(byte, 16))
            byte = ''
        # Check if we've read the expected amount of data
        if len(chunk) == length // 2:  # // 2 because length is doubled in the earlier calculation
            readLevel.append(chunk)
            chunk = []
    # Append any remaining chunk if the loop ends but chunk is not empty
    if chunk:
        readLevel.append(chunk)
    return readLevel
#end

def WriteLevel(level, file):
    bufferFile = open(file, 'wb')
    for y, chunk in enumerate(level):
        for x, tileID in enumerate(chunk):
            bufferFile.write(int.to_bytes(tileID, 1, 'little', signed=False))

    with open(file, 'rb') as f_in:  # Open the input file in binary read mode
        with bz2.open(file, 'wb', 9) as f_out:  # Open the output file in binary write mode
            f_out.writelines(f_in)  # Write the content to the .bz2 file

def UpdateLevel(level=list, camx=int or float, camy=int or float, scrWidth=int, scrHeight=int, skipChecks=bool):
    '''
    Returns on-screen tile sprites in a sprite group, given by the camera position.\n
    Level Data Structure Reference:\n
    [\n
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],\n
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],\n
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]\n
    ]\n
    The amount of lists in it is the 'Y' axis, and the length of the lists are the 'X' axis.\n
    Tiles are 32x32, so 15x11.25 tiles cover a 480x360 screen. 1 Screen worth height should be 12 tiles high.\n
    The X table values define what tile it is, and values that are '0' are returned as a blank sprite.]\n
    Tiling starts at the top-left of the screen, so the level data's height cannot be less than 12 otherwise it will be floating a little.\n
    The 'skipChecks' parameter determines if the given values should be verified.\n
    Keep False if unsure, otherwise if you're sure the given values won't be invalid, set to True for a very slight boost of performance.
    '''
    if not skipChecks:
        if not (isinstance(level, list) and isinstance(camx, (int, float)) and isinstance(camy, (int, float)) and isinstance(scrWidth, int) and isinstance(scrHeight, int)):
            print('One of the given values are invalid!')
            return TypeError
        #end
    #end

    def CreateTile(pos, image):
        class Tile(pygame.sprite.WeakSprite):
            def __init__(Tile):
                super().__init__()
                Tile.image = image
                Tile.rect = Tile.image.get_rect()
                Tile.rect.center = pos
            #end
        #end
        return Tile()
    #end
        
    tile_cache = []
    for i in range(48):
        tile_cache.append(None)
    #end
    Tiles = pygame.sprite.Group()
    # Iterate through the level data to create tiles
    for y, Chunk in enumerate(level):
        for x, tileID in enumerate(Chunk):
            if tileID != 0:
                position = (16 + x * 32, -8 + y * 32)
                if tile_cache.__len__() < tileID or tile_cache[tileID] == None:
                    tile_cache.__setitem__(tileID, pygame.image.load(os.path.join('tiles', f'{tileID}.bmp')))
                #end
                tile = CreateTile(position, tile_cache[tileID])
                if tile: # Check if the tile creation was successful
                    Tiles.add(tile)
                else: print(f"Warning: Tile creation failed at position: {position} with tileID: {tileID}")
            #end
        #end
    #end
    return Tiles
#end
