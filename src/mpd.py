'''
To use this module, set the 'tilePath' variable to the folder where your tile textures are, relative to your workspace.\n
(e.g. tilePath = 'res/tile')\n
The .mpd file is a level/map hex file, in little endian.\n
The bits of the file (e.g: x64, x32) is the length (X) of the level.\n
The first 16 bytes of the file is a UInt64 (Unsigned 64 bit integer), representing the X length.\n
The height of the level (Y) is when the X chunk loops back.
'''
import pygame
pygame.init()

tilePath = 'res/tile'

# Tools
def CreateTileCache(allocatedLength=48) -> list:
    '''
    Creates and allocates space for caching tiles.
    '''
    tileCache = []
    for i in range(allocatedLength):
        tileCache.append(None)
    return tileCache

#.mpd (Level File)
def ReadLevel(level) -> list:
    '''
    Returns readable level data from a file.\n
    level = open('yourLevel.mpd, 'rb')
    '''
    level = level.read().hex()

    # Extract length from the first 16 bytes
    length = int.from_bytes(bytes.fromhex(level[:16]), 'little', signed=False) * 2
    
    readLevel = []
    chunk = []
    byte = ''
    
    for i in range(16, len(level)): # Start from the 17th byte
        byte += level[i]
        if len(byte) == 2: # Once we have 2 characters (1 byte)
            chunk.append(int(byte, 16))
            byte = ''
        # Check if we've read the expected amount of data
        if len(chunk) >= length // 2: # // 2 because length is doubled in the earlier calculation
            readLevel.append(chunk)
            chunk = []
    # Append any remaining chunk if the loop ends but chunk is not empty
    if chunk:
        readLevel.append(chunk)
    del length, level, chunk, byte
    return readLevel

def ReadLevelTuple(level) -> list:
    '''
    Returns readable level data from a file.\n
    level = open('yourLevel.mpd, 'rb')
    '''
    level = level.read().hex()

    # Extract length from the first 16 bytes
    length = int.from_bytes(bytes.fromhex(level[:16]), 'little', signed=False) * 2
    
    readLevel = []
    chunk = []
    byte = ''
    
    for i in range(16, len(level)): # Start from the 17th byte
        byte += level[i]
        if len(byte) == 4: # Once we have 4 bytes
            chunk.append(int(byte, 32))
            byte = ''
        # Check if we've read the expected amount of data
        if len(chunk) >= length // 2: # // 2 because length is doubled in the earlier calculation
            readLevel.append(chunk)
            chunk = []
    # Append any remaining chunk if the loop ends but chunk is not empty
    if chunk:
        readLevel.append(chunk)
    del length, level, chunk, byte
    return readLevel

def WriteLevel(level, file):
    '''
    Save given level data to a .mpd file.
    '''
    file.write(len(level[0]).to_bytes(8, 'little', signed=False))
    for y, chunk in enumerate(level):
        for x, tileID in enumerate(chunk):
            file.write(tileID.to_bytes(1, 'little', signed=False))

def WriteLevelTuple(level, file):
    '''
    Save given level data to a .mpd file.
    '''
    file.write(len(level[0]).to_bytes(8, 'little', signed=False))
    for y, chunk in enumerate(level):
        for x, tile in enumerate(chunk):
            file.write(tile[0].to_bytes(1, 'little', signed=False))
            file.write(tile[1].to_bytes(1, 'little', signed=False))

# Level Updating
def CreateTile(pos=tuple, image=pygame.surface.Surface, dir=0) -> pygame.sprite.Sprite:
    '''
    'dir' must be between 0 and 6, anything above than 3 will be flipped.\n
    Returns a tile, with a 'update' function to scroll it across the screen so you can call "TileGroupName".update(camx, camy) to scroll in bulk.
    '''
    class Tile(pygame.sprite.Sprite):
        def __init__(Tile):
            super().__init__()
            Tile.image = pygame.transform.rotate(image, (dir%4)*-90)
            Tile.rect = Tile.image.get_rect()
            Tile.rect.center = pos
            Tile.startingX = Tile.rect.x
            Tile.startingY = Tile.rect.y
        def update(tile, camx=0, camy=0):
            '''
            This function scrolls the tile, you can use "TileGroupName".update(camx, camy) to scroll all tiles in bulk.\n
            (sprite group returned by different function.)
            '''
            tile.rect.x = tile.startingX - camx
            tile.rect.y = tile.startingY + camy
    return Tile()

def LoadEntireLevel(level=list) -> pygame.sprite.Group:
    '''
    You should only use this when starting a level, as it is very unoptimized, use the 'UpdateLevelX'/Y functions instead, which loads columns/rows in and out.\n
    Returns on-screen tile sprites in a sprite group, given by the camera position, and the tile images used so you can store them until needed.\n
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
    The 'tile_cache' parameter is so you can keep the tile graphics in memory, so you don't waste performance reloading them again, can be left blank.\n
    You must use the 'CreateTileCache' function if you want to store the tile cache.\n
    The amount of lists in it is the 'Y' axis, and the length of the lists are the 'X' axis.\n
    Tiles are 32x32, so 15x11.25 tiles cover a 480x360 screen. 1 Screen worth height should be 12 tiles high.\n
    The X table values define what tile it is, and values that are '0' are returned as a blank sprite.\n
    Tiling starts at the top-left of the screen, so the level data's height cannot be less than 12 otherwise it will be floating a little.\n
    The 'skipChecks' parameter determines if the given values should be verified.\n
    Keep False if unsure, otherwise if you're sure the given values won't be invalid, set to True for a very slight boost of performance.
    '''
    Tiles = pygame.sprite.Group()
    tileCache = CreateTileCache()
    # Iterate through the level data to create tiles
    for y, Chunk in enumerate(level):
        for x, tileID in enumerate(Chunk):
            if tileID != 0:
                pos = (16 + x * 32, 8 + y * 32)
                if len(tileCache) < tileID or not tileCache[tileID]:
                    tileCache[tileID] = pygame.image.load(f'{tilePath}/{tileID}.bmp')
                tile = CreateTile(pos, tileCache[tileID])
                if tile: # Check if the tile creation was successful
                    Tiles.add(tile)
                else: print(f'Warning: Tile creation failed at position: {pos} with tileID: {tileID}')
    del tileCache, tile, pos
    return Tiles

def UpdateLevel(level=list, scrWidth=480, scrHeight=360, camx=0, camy=0, tileCache=[]) -> tuple[pygame.sprite.Group, list]:
    '''
    You should only use this when starting a level, as it is very unoptimized, use the 'UpdateLevelX'/Y functions instead, which loads columns/rows in and out.\n
    Returns on-screen tile sprites in a sprite group, given by the camera position, and the tile images used so you can store them until needed.\n
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
    The 'tile_cache' parameter is so you can keep the tile graphics in memory, so you don't waste performance reloading them again, can be left blank.\n
    You must use the 'CreateTileCache' function if you want to store the tile cache.\n
    The amount of lists in it is the 'Y' axis, and the length of the lists are the 'X' axis.\n
    Tiles are 32x32, so 15x11.25 tiles cover a 480x360 screen. 1 Screen worth height should be 12 tiles high.\n
    The X table values define what tile it is, and values that are '0' are returned as a blank sprite.\n
    Tiling starts at the top-left of the screen, so the level data's height cannot be less than 12 otherwise it will be floating a little.\n
    The 'skipChecks' parameter determines if the given values should be verified.\n
    Keep False if unsure, otherwise if you're sure the given values won't be invalid, set to True for a very slight boost of performance.
    '''
    Tiles = pygame.sprite.Group()
    # Iterate through the level data to create tiles
    for y, Chunk in enumerate(level):
        for x, tileID in enumerate(Chunk):
            if tileID != 0:
                pos = ((16-camx) + x * 32, (camy-8) + y * 32)
                if len(tileCache) < tileID or not tileCache[tileID]:
                    tileCache[tileID] = pygame.image.load(f'{tilePath}/{tileID}.bmp')
                tile = CreateTile(pos, tileCache[tileID])
                if tile: # Check if the tile creation was successful
                    Tiles.add(tile)
                else: print(f'Warning: Tile creation failed at position: {pos} with tileID: {tileID}')
    del tile, pos
    return Tiles, tileCache

def UpdateLevelTuple(level=list, scrWidth=480, scrHeight=360, camx=0, camy=0, tileCache=[]) -> tuple[pygame.sprite.Group, list, pygame.sprite.Group]:
    '''
    You should only use this when starting a level, as it is very unoptimized, use the 'UpdateLevelX'/Y functions instead, which loads columns/rows in and out.\n
    Returns on-screen tile sprites in a sprite group, given by the camera position, and the tile images used so you can store them until needed.\n
    Level Data Structure Reference:\n
    [\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],\n
    [(1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0)]\n
    ]\n
    The 'tile_cache' parameter is so you can keep the tile graphics in memory, so you don't waste performance reloading them again, can be left blank.\n
    It conists of a tuple with 2 parameters, the first one being the tile image ID, and the second parameter is the direction.\n
    The second parameter 
    You must use the 'CreateTileCache' function if you want to store the tile cache.\n
    The amount of lists in it is the 'Y' axis, and the length of the lists are the 'X' axis.\n
    Tiles are 32x32, so 15x11.25 tiles cover a 480x360 screen. 1 Screen worth height should be 12 tiles high.\n
    The X table values define what tile it is, and values that are '0' are returned as a blank sprite.\n
    Tiling starts at the top-left of the screen, so the level data's height cannot be less than 12 otherwise it will be floating a little.\n
    The 'skipChecks' parameter determines if the given values should be verified.\n
    Keep False if unsure, otherwise if you're sure the given values won't be invalid, set to True for a very slight boost of performance.
    '''
    Tiles = pygame.sprite.Group()
    # Iterate through the level data to create tiles
    for y, Chunk in enumerate(level):
        for x, tileID in enumerate(Chunk):
            if tileID != 0:
                pos = ((16-camx) + x * 32, (camy-8) + y * 32)
                if len(tileCache) < tileID or not tileCache[tileID]:
                    tileCache[tileID] = pygame.image.load(f'{tilePath}/{tileID}.bmp')
                tile = CreateTile(pos, tileCache[tileID])
                if tile: # Check if the tile creation was successful
                    Tiles.add(tile)
                else: print(f'Warning: Tile creation failed at position: {pos} with tileID: {tileID}')
    del tile, pos
    return Tiles, tileCache

def ExtendLevelX(level=list, copyValue=0, extendBy=1) -> list:
    '''
    Extends the given level by 'extendBy' on the X axis, setting those values to the 'copyValue'.
    '''
    for i in range(extendBy):
        for y, Chunk in enumerate(level):
            Chunk.append(copyValue)
    return level

def ExtendLevelY(level=list, copyValue=0, extendBy=1) -> list:
    '''
    Extends the given level by 'extendBy' on the Y axis, setting those values to the 'copyValue'.
    '''
    cloneList = []
    for xLength in enumerate(level[0]):
        cloneList.append(copyValue)
    for i in range(extendBy):
        level.append(cloneList)
    return level