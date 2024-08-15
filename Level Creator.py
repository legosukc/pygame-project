from pygame.locals import *
from tkinter import filedialog
import pygame
import pygame.math as math
import mpd
# Initialize Config
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 360
FPS = 6

level = mpd.ReadLevel(open('level.mpd.bz2', 'rb'))

class SaveAs(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('SaveAs.png')
        self.rect = self.image.get_rect()
        self.rect.center = (self.image.get_width()*.5, SCREEN_HEIGHT+self.image.get_height()*.5)
    def update(self):
        mouse = pygame.mouse
        if mouse.get_pressed()[0]:
            self.image.set_alpha(200)
            if self.rect.collidepoint(mouse.get_pos()[0], mouse.get_pos()[1]):
                file = filedialog.asksaveasfile('w', confirmoverwrite=True, defaultextension='mpd', filetypes=[('Level', '.mpd')])
                mpd.WriteLevel(level, file)
        else: self.image.set_alpha(255)

# Initialize Game
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT+SaveAs().image.get_height()))
pygame.display.set_caption('The Prickly Penis') #Window Caption (top left thingy)

class Cursor(pygame.sprite.WeakSprite):
    def __init__(self):
        super().__init__()
        self.selectedSpaceX = 0
        self.selectedSpaceY = 0
        self.selectedTileID = 1
        self.selTool = 0 #0 = Build; 1 = Erase; 2 = Pick Tile
    def update(self, keys):
        def MoveTile():
            self.selectedSpaceX = math.clamp(self.selectedSpaceX + keys[K_d]-keys[K_a], 0, 14)
            self.selectedSpaceY = math.clamp(self.selectedSpaceY + keys[K_s]-keys[K_w], -1, 10)
            self.rect.centerx = (self.selectedSpaceX * 32) + 16
            self.rect.centery = (self.selectedSpaceY * 32) + 24
        if keys[K_1]:
            self.selTool = 0
            render.remove(outline)
            render.add(outline)
        elif keys[K_2]:
            self.selTool = 1
            render.remove(outline)
        elif keys[K_3]:
            self.selTool = 2
            render.remove(outline)
        # Build
        if self.selTool == 0:
            #Cycle Tile
            self.selectedTileID = math.clamp(self.selectedTileID + keys[K_e]-keys[K_q], 1, 7)
            self.image = pygame.image.load(f'{self.selectedTileID}.bmp')
            self.image.set_alpha(190)
            self.rect = self.image.get_rect()
            MoveTile()
            #Outline
            outline.rect.center = self.rect.center
            #Write Tile To Level
            if keys[K_SPACE]:
                level[self.selectedSpaceY+1][self.selectedSpaceX] = self.selectedTileID
        #Eraser
        elif self.selTool == 1:
            self.image = pygame.image.load('eraser.png')
            self.rect = self.image.get_rect()
            MoveTile()
            if keys[K_SPACE]:
                level[self.selectedSpaceY+1][self.selectedSpaceX] = 0
        elif self.selTool == 2:
            self.image = pygame.image.load('picker.png')
            self.rect = self.image.get_rect()
            MoveTile()
            if keys[K_SPACE]:
                if level[self.selectedSpaceY+1][self.selectedSpaceX] != None:
                    self.selectedTileID = level[self.selectedSpaceY+1][self.selectedSpaceX]
                    self.selTool = 0
                    render.add(outline)
            #end
        #end
    #end
#end

class CursorOutline(pygame.sprite.WeakSprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('Select.png')
        self.rect = self.image.get_rect()
        self.image.set_alpha(170)

# Main
if __name__ == '__main__':
    Running = True
    cursor = Cursor()
    outline = CursorOutline()
    clock = pygame.time.Clock()
    render = pygame.sprite.Group(outline, cursor)
    ui = pygame.sprite.Group(SaveAs())
    while Running:
        for event in pygame.event.get():
            Running = event.type != QUIT
        cursor.update(pygame.key.get_pressed())
        #Render
        screen.fill((0, 0, 0))
        mpd.UpdateLevel(level, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).draw(screen)
        render.draw(screen)
        ui.update()
        ui.draw(screen)
        pygame.display.update()
        clock.tick(FPS)
    print(level)
    pygame.quit()
#end