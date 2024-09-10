from pygame.locals import *
from tkinter import filedialog
import pygame
import pygame.math as math
import mpd
# Initialize Config
SCREEN_WIDTH = 480 * 2
SCREEN_HEIGHT = 360 * 2
FPS = 60
#Get Tile Count
tileCount = 0
import os
for i, name in enumerate(os.listdir('res/tile/')):
    if name == f'{i+1}.bmp':
        tileCount += 1
del os
# Constants
level = mpd.ReadLevel(open('map/level.mpd', 'rb'))
BackgroundColor = (0, 0, 0)

class SaveAs(pygame.sprite.Sprite):
    def __init__(ui):
        super().__init__()
        ui.image = pygame.image.load('res/gui/SaveAs.png')
        ui.rect = ui.image.get_rect()
        ui.rect.center = (ui.image.get_width()//2, SCREEN_HEIGHT+ui.image.get_height()//2)
    def update(ui):
        if ms.get_pressed()[0]:
            ui.image.set_alpha(200)
            if ui.rect.collidepoint(ms.get_pos()):
                file = filedialog.asksaveasfile('wb', confirmoverwrite=True, defaultextension='mpd', filetypes=[('Level', '.mpd')])
                if file:
                    mpd.WriteLevel(level, file)
                file.close()
        else: ui.image.set_alpha(255)

# Initialize Game
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT+SaveAs().image.get_height()))
pygame.display.set_caption('Level Creator') #Window Caption (top left thingy)
pygame.display.set_icon(pygame.image.load('res/icon.png'))

class Cursor(pygame.sprite.Sprite):
    def __init__(cur):
        super().__init__()
        cur.selX = 0
        cur.selY = 0
        cur.TileID = 1
        cur.selTool = 0 #0 = Build: 1 = Erase: 2 = Pick Tile
        cur.image = pygame.image.load(f'res/tile/{cur.TileID}.bmp')
        cur.image.set_alpha(190)
        cur.rect = cur.image.get_rect()
        cur.cooldwn = (0, 0)
        cur.flip = False

    def update(cur, keys, lvl) -> list:
        def swapTool(image, toolID=0):
            cur.selTool = toolID
            render.remove(outline)
            cur.image = pygame.image.load(image)
            cur.rect = cur.image.get_rect()

        if cur.cooldwn[0] >= 0:
            cur.cooldwn = (cur.cooldwn[0]-1, cur.cooldwn[1])
        else: cur.cooldwn = (0, 0)

        #Build Tool Extras
        if cur.selTool == 0:
            #Cycle Tile
            if cur.cooldwn[0] <= 0 or cur.cooldwn[1] != 1:
                if cur.TileID + keys[K_e]-keys[K_q] != cur.TileID:
                    cur.TileID = math.clamp(cur.TileID + keys[K_e]-keys[K_q], 1, tileCount)
                    swapTool(f'res/tile/{cur.TileID}.bmp')
                    render.add(outline)
                    cur.image.set_alpha(190)
                    cur.cooldwn = (10, 1)

        if keys[K_1]:
            swapTool(f'res/tile/{cur.TileID}.bmp')
            render.add(outline)
            cur.image.set_alpha(190)
        elif keys[K_2]:
            swapTool('res/gui/eraser.png', 1)
        elif keys[K_3]:
            swapTool('res/gui/picker.png', 2)

        cur.selX = math.clamp((cam.x+ms.get_pos()[0])//32, 0, (cam.x+SCREEN_WIDTH//32)-1)
        cur.selY = math.clamp((ms.get_pos()[1]-cam.y)//32, 0, (SCREEN_HEIGHT-cam.y)//32)
        cur.rect.centerx = (cur.selX * 32) + 16 - cam.x
        cur.rect.centery = (cur.selY * 32) - 8 + cam.y
        outline.rect.center = cur.rect.center
        if keys[K_f]:
            cur.flip = not cur.flip
            pos = cur.rect.center
            cur.image = pygame.transform.flip(cur.image, True, False)

        if ms.get_pressed()[0]:
            if cur.selTool == 2:
                if lvl[cur.selY][cur.selX]:
                    cur.TileID = lvl[cur.selY][cur.selX]
                    swapTool(f'res/tile/{cur.TileID}.bmp')
                    render.add(outline)
            else: #Rubber And Build Tool
                while True:
                    try: #Tile Editing Code
                        if cur.selTool == 0: #Building
                            lvl[cur.selY][cur.selX] = cur.TileID
                        else: #Erasing
                            lvl[cur.selY][cur.selX] = 0
                    except IndexError: #Extend Level Bounds
                        if len(lvl) <= abs(cur.selY):
                            lvl = mpd.ExtendLevelY(lvl)
                        elif len(lvl[cur.selY]) <= cur.selX:
                            lvl = mpd.ExtendLevelX(lvl)
                        else:
                            raise IndexError('Could not extend level dimension/s.')
                        continue
                    else: break
        return lvl

class CursorOutline(pygame.sprite.Sprite):
    def __init__(out):
        super().__init__()
        out.image = pygame.image.load('res/gui/Select.png')
        out.rect = out.image.get_rect()
        out.image.set_alpha(170)

class Camera():
    def __init__(cam):
        cam.x = 0
        cam.y = 0
    def update(cam, keys):
        cam.x = math.clamp(cam.x + (keys[K_RIGHT]-keys[K_LEFT])*32, 0, 18446744073709551615)
        cam.y = math.clamp(cam.y + (keys[K_UP]-keys[K_DOWN])*32, -18446744073709551615, 0)

# Main
if __name__ == '__main__':
    Running = True
    ms = pygame.mouse
    cursor = Cursor()
    outline = CursorOutline()
    cam = Camera()
    clock = pygame.time.Clock()
    render = pygame.sprite.Group(outline, cursor)
    ui = pygame.sprite.Group(SaveAs())
    tileCache = mpd.CreateTileCache()
    pygame.mouse.set_visible(False)
    while Running:
        for event in pygame.event.get():
            Running = event.type != QUIT
        #Update
        keys = pygame.key.get_pressed()
        level = cursor.update(keys, level)
        cam.update(keys)
        ui.update()
        geometry, tileCache = mpd.UpdateLevel(level, SCREEN_WIDTH, SCREEN_HEIGHT, cam.x, cam.y, tileCache)
        #Render
        screen.fill(BackgroundColor)
        geometry.draw(screen)
        render.draw(screen)
        ui.draw(screen)
        pygame.display.update()
        clock.tick(FPS)
    print(level)
    pygame.quit()