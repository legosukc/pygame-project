from pygame.locals import *
from tkinter import filedialog
import pygame
import pygame.math as math
import mpd
# Initialize Config
SCREEN_WIDTH = 480 * 2
SCREEN_HEIGHT = 360 * 2
FPS = 6

level = mpd.ReadLevel(open('map/level.mpd', 'rb'))

class SaveAs(pygame.sprite.Sprite):
    def __init__(ui):
        super().__init__()
        ui.image = pygame.image.load('gui/SaveAs.png')
        ui.rect = ui.image.get_rect()
        ui.rect.center = (ui.image.get_width()*.5, SCREEN_HEIGHT+ui.image.get_height()*.5)
    def update(ui):
        ms = pygame.mouse
        if ms.get_pressed()[0]:
            ui.image.set_alpha(200)
            if ui.rect.collidepoint(ms.get_pos()[0], ms.get_pos()[1]):
                file = filedialog.asksaveasfile('wb', confirmoverwrite=True, defaultextension='mpd', filetypes=[('Level', '.mpd')])
                if file: mpd.WriteLevel(level, file)
        else: ui.image.set_alpha(255)

# Initialize Game
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT+SaveAs().image.get_height()))
pygame.display.set_caption('The Prickly Penis') #Window Caption (top left thingy)

class Cursor(pygame.sprite.Sprite):
    def __init__(cur):
        super().__init__()
        cur.selX = 0
        cur.selY = 0
        cur.TileID = 1
        cur.selTool = 0 #0 = Build: 1 = Erase: 2 = Pick Tile
        cur.image = pygame.image.load(f'res/{cur.TileID}.bmp')
        cur.image.set_alpha(190)
        cur.rect = cur.image.get_rect()

    def update(cur, keys, lvl) -> list:
        def swapTool(image, toolID=0):
            cur.selTool = toolID
            render.remove(outline)
            cur.image = pygame.image.load(image)
            cur.rect = cur.image.get_rect()
        #end
        
        if keys[K_1]:
            swapTool(f'res/{cur.selTileID}.bmp')
            render.add(outline)
            cur.image.set_alpha(190)
        elif keys[K_2]:
            swapTool('gui/eraser.png', 1)
        elif keys[K_3]:
            swapTool('gui/picker.png', 2)
        #end
        cur.selX = math.clamp(cur.selX + keys[K_d]-keys[K_a], 0, (SCREEN_WIDTH//32)-1)
        cur.selY = math.clamp(cur.selY + keys[K_s]-keys[K_w], -1, (SCREEN_HEIGHT//32)-1)
        cur.rect.centerx = (cur.selX * 32) + 16
        cur.rect.centery = (cur.selY * 32) - 8
        
        if keys[K_SPACE]:
            if cur.selTool == 2:
                if lvl[cur.selY][cur.selX]:
                    cur.selTileID = lvl[cur.selY][cur.selX]
                    swapTool(f'res/{cur.TileID}.bmp')
                    render.add(outline)
                #end
            else: #Rubber And Build Tool
                #Write to level
                while True:
                    try:
                        lvl[cur.selY][cur.selX] = cur.selTool == 0 and cur.TileID or 0
                    except IndexError:
                        lvl = mpd.ExtendLevelLength(lvl)
                        continue
                    else: break
                #end
            #end
        #end
        
        #Build Tool Extras
        if cur.selTool == 0:
            #Cycle Tile
            cur.TileID = math.clamp(cur.TileID + keys[K_e]-keys[K_q], 1, 7)
            #Outline
            outline.rect.center = cur.rect.center
        #end
        return lvl
    #end
#end

class CursorOutline(pygame.sprite.Sprite):
    def __init__(out):
        super().__init__()
        out.image = pygame.image.load('gui/Select.png')
        out.rect = out.image.get_rect()
        out.image.set_alpha(170)
        
class Camera():
    def __init__(cam):
        cam.x = 0
        cam.y = 0
        cam.center = (cam.x, cam.y)
    def update(cam, keys):
        cam.x += keys[K_RIGHT]-keys[K_LEFT]
        cam.y += keys[K_UP]-keys[K_DOWN]
        cam.center += (keys[K_RIGHT]-keys[K_LEFT], keys[K_UP]-keys[K_DOWN])
        print(cam.center)
        
# Main
if __name__ == '__main__':
    Running = True
    cursor = Cursor()
    outline = CursorOutline()
    cam = Camera()
    clock = pygame.time.Clock()
    render = pygame.sprite.Group(outline, cursor)
    ui = pygame.sprite.Group(SaveAs())
    tileCache = mpd.CreateTileCache()
    while Running:
        for event in pygame.event.get():
            Running = event.type != QUIT
        geometry, tileCache = mpd.UpdateLevel(level, SCREEN_WIDTH, SCREEN_HEIGHT, tileCache=tileCache)
        keys = pygame.key.get_pressed()
        level = cursor.update(keys, level)
        cam.update(keys)
        ui.update()
        #Render
        screen.fill((0, 0, 0))
        geometry.draw(screen)
        render.draw(screen)
        ui.draw(screen)
        pygame.display.update()
        clock.tick(FPS)
    print(level)
    pygame.quit()
#end