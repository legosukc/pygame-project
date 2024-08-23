import pygame
#best avg fps is 1811
#current is about 272
#14.5 cpu usage

# Initialize Config
SCREEN_WIDTH = 480 * 2
SCREEN_HEIGHT = 360 * 2

# Initialize Game
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Progress Text
progress = None
def UpdateProgressText(text=str):
    progress = pygame.font.SysFont('Comic Sans MS', 20).render(text, True, (255, 255, 255))
    screen.blit(progress, (SCREEN_WIDTH-progress.get_width(), SCREEN_HEIGHT-progress.get_height()))
    pygame.display.update()
#end
        
UpdateProgressText('give me a second bud... (yes, this is comic sans)')
# Window Config
pygame.display.set_caption('platformer') #Window Caption (top left thingy)
#pygame.display.set_icon(pygame.image.load('GrassTile.bmp'))

# Initialize Modules
from pygame.locals import *
import pygameplus
import pygame.math as math
import modules.mpd as mpd

# Game Constants
Gravity = .5
DEBUG = False
FPS = pygame.display.get_current_refresh_rate() #0 = Unlimited

level = mpd.ReadLevel(open('levels\level.mpd', 'rb'))

class Camera():
    def __init__(cam):
        cam.x = 0
        cam.y = 0
        cam.offX = 0
        cam.offY = 0
        cam.lstX = cam.x
        cam.lstY = cam.y

class player(pygame.sprite.DirtySprite):
    # Player Config
    def __init__(plr):
        super().__init__()
        # Looks
        plr.image = pygame.Surface((10, 20)) # Player Size
        plr.image.fill((255, 255, 255))
        plr.rect = plr.image.get_rect()
        plr.dirty = 1
        # Position
        plr.rect.center = (SCREEN_WIDTH*.5, SCREEN_HEIGHT*.5)
        # States
        plr.grounded = False
        plr.health = 3
        plr.JumpsDone = 0
        plr.JumpHeldFrames = 0
        #Base X Cap
        plr.BaVCX = 10 #Base Airborne VX Cap
        plr.BgVCX = 5 #Base Grounded VX Cap
        #X Cap (gets changed during gameplay)
        plr.aVCX = plr.BaVCX #Airborne
        plr.gVCX = plr.BgVCX #Grounded
        #VY Cap
        plr.VCY = 10
        #Movement
        plr.accel = 1 #How Fast You Can Reach The Cap
        plr.AirAccel = .2 #Airborne Version
        plr.deccel = .2 #Basically Shoe Grippies
        plr.vx = 0
        plr.vy = 0
    #end
    
    # Player Loop
    def update(plr, keys):
        #Movement
        moveX = keys[K_d]-keys[K_a]
        if moveX == 0:
            if plr.grounded:
                plr.vx -= plr.vx * plr.deccel
                if round(plr.vx) == 0: plr.vx = 0
        else:
            plr.vx += (plr.grounded and plr.accel or plr.AirAccel) * moveX

        #Jump
        if keys[K_SPACE] and (plr.JumpHeldFrames > 0 or plr.grounded or plr.JumpsDone < 2):
            plr.JumpHeldFrames += 1
        else: plr.JumpHeldFrames = 0
        
        if (plr.grounded or plr.JumpsDone < 2) and plr.JumpHeldFrames == 1:
                plr.JumpsDone += 1
                plr.vy = plr.JumpsDone < 2 and -6 or -3

                plr.aVCX = math.clamp(abs(plr.vx), 2, plr.BaVCX)
                plr.grounded = False
        elif pygameplus.WithinRange(plr.JumpHeldFrames, 5, 8) and plr.JumpsDone > 0:            
            plr.vy -= 8/plr.JumpHeldFrames
        #end

        # Speed Cap
        plr.vx = plr.grounded and math.clamp(plr.vx, -plr.gVCX, plr.gVCX) or math.clamp(plr.vx, -plr.aVCX, plr.aVCX)
        plr.vy = math.clamp(plr.vy, -plr.VCY, plr.VCY)

        # X Collision
        plr.rect.x += plr.vx * delta
        if pygame.sprite.spritecollideany(plr, geometry):
            if plr.vx != 0:
                velDir = plr.vx > 0 and 1 or -1
                plr.rect.x = round(plr.rect.x)
                while pygame.sprite.spritecollideany(plr, geometry):
                    plr.rect.x -= velDir
                plr.vx = 0
            #end
        #end
        
        # Y Collision
        plr.rect.y += plr.vy
        if pygame.sprite.spritecollideany(plr, geometry):
            if plr.vy != 0:
                velDir = plr.vy > 0 and 1 or -1
                plr.rect.y = round(plr.rect.y)
                while pygame.sprite.spritecollideany(plr, geometry):
                    plr.rect.y -= velDir
                #end
                if plr.JumpsDone > 0 and plr.vy >= 0:
                    plr.JumpsDone = 0
                    plr.aVCX = plr.BaVCX
                #end
            if plr.vy >= 0:
                plr.grounded = True
            plr.vy = 0
        else:
            if plr.grounded:
                plr.grounded = False
                plr.aVCX = abs(plr.vx)
            plr.vy += Gravity
        #end
        
        cam.x += keys[K_RIGHT]-keys[K_LEFT]
        cam.y += keys[K_DOWN]-keys[K_UP]
        
        if DEBUG:
            print(plr.JumpsDone)
    #end
#end

# Main
if __name__ == '__main__':
    plr = player()
    cam = Camera()
    sprites = pygame.sprite.Group(plr)
    renderSprites = sprites.copy()
    Running = True
    clock = pygameplus.clock
    tileCache = mpd.CreateTileCache()
    delta = 1
    while Running:
        delta = pygameplus.GetDeltaTime()
        for event in pygame.event.get():
            Running = event.type != QUIT
        geometry, tileCache = mpd.UpdateLevel(level, SCREEN_WIDTH, SCREEN_HEIGHT, cam.x, cam.y, tileCache)
        plr.update(pygame.key.get_pressed())
        #Render
        screen.fill((0, 0, 0))
        geometry.draw(screen)
        renderSprites.draw(screen)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
#end