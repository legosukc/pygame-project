import pygame

#best avg fps is 1811
#current is about 272

# Initialize Config
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 360

# Initialize Game
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Progress Text
progress = None
def UpdateProgressText(text=str):
    progress = pygame.font.SysFont('Comic Sans MS', 30).render(f'{text}...', True, (255, 255, 255))
    screen.blit(progress, (SCREEN_WIDTH-progress.get_width(), SCREEN_HEIGHT-progress.get_height()))
    pygame.display.update()
#end
UpdateProgressText('give me a second bud')
# Window Config
pygame.display.set_caption('The Prickly Penis') #Window Caption (top left thingy)
#pygame.display.set_icon(pygame.image.load('GrassTile.bmp'))

# Initialize Modules
from pygame.locals import *
import pygameplus
import pygame.math as math
import modules.mpd as mpd

# Game Config
Gravity = .5
DEBUG = False
FPS = pygame.display.get_current_refresh_rate() #0 = Unlimited

level = mpd.ReadLevel(open('levels\level.mpd', 'rb'))

class player(pygame.sprite.Sprite):
    # Player Config
    def __init__(plr):
        super().__init__()
        # Looks
        plr.image = pygame.Surface((10, 10)) # Player Size
        plr.image.fill((255, 255, 255))
        plr.rect = plr.image.get_rect()
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
        #X Cap (changeable)
        plr.aVCX = plr.BaVCX #Airborne
        plr.gVCX = plr.BgVCX #Grounded
        #VY Cap
        plr.VCY = 10
        #Movement
        plr.accel = 1 #How Fast You Can Reach The Cap
        plr.AirAccel = .2 #Airborne Version
        plr.deccel = .2 #Basically Shoe Grippies :)
        plr.JumpBoost = 1 #1.2
        plr.vx = 0
        plr.vy = 0
    #end
    
    # Player Loop
    def update(plr, keys):
        #Movement
        moveX = keys[K_d]-keys[K_a]
        if moveX == 0 and plr.grounded:
            plr.vx -= plr.vx * plr.deccel
        else:
            plr.vx += (plr.grounded and plr.accel or plr.AirAccel) * moveX

        #Jump
        if keys[K_SPACE] and (plr.JumpHeldFrames > 0 or plr.grounded or plr.JumpsDone < 2):
            plr.JumpHeldFrames += 1
        else: plr.JumpHeldFrames = 0
        
        if (plr.grounded or plr.JumpsDone < 2) and plr.JumpHeldFrames == 1:
                plr.JumpsDone += 1
                if plr.JumpsDone < 2:
                    plr.vy = -6
                else:
                    plr.vy = -3
                
                plr.vx *= plr.JumpBoost
                plr.aVCX = math.clamp(abs(plr.vx), 1, plr.BaVCX * plr.JumpBoost)
                plr.grounded = False
        elif pygameplus.WithinRange(plr.JumpHeldFrames, 5, 8, True, True) and plr.JumpsDone > 0:            
            plr.vy -= 8/plr.JumpHeldFrames
        #end

        # Speed Cap
        if plr.grounded:
            plr.vx = math.clamp(plr.vx, -plr.gVCX, plr.gVCX)
        else: plr.vx = math.clamp(plr.vx, -plr.aVCX, plr.aVCX)
        plr.vy = math.clamp(plr.vy, -plr.VCY, plr.VCY)

        # X Collision
        plr.rect.x += plr.vx * deltaTime
        if pygame.sprite.spritecollideany(plr, geometry):
            if plr.vx != 0:
                velDir = plr.vx > 0 and 1 or -1
                while pygame.sprite.spritecollideany(plr, geometry):
                    plr.rect.x -= velDir
                plr.vx = 0
            #end
        #end
        
        # Y Collision
        plr.rect.y += plr.vy * deltaTime
        if pygame.sprite.spritecollideany(plr, geometry):
            if plr.vy != 0:
                velDir = plr.vy > 0 and 1 or -1
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
        
        if DEBUG:
            print(plr.JumpsDone)
    #end
#end

def GetLevel(tileCache):
    geometry = mpd.UpdateLevel(level, SCREEN_WIDTH, SCREEN_HEIGHT, tileCache=tileCache)
    return geometry[0], geometry[1]

# Main
if __name__ == '__main__':
    plr = player()
    sprites = pygame.sprite.Group(plr)
    renderSprites = sprites.copy()
    Running = True
    clock = pygame.time.Clock()
    tileCache = []
    deltaTime = 1
    while Running:
        for event in pygame.event.get():
            Running = event.type != QUIT
        geometry, tileCache = GetLevel(tileCache)
        plr.update(pygame.key.get_pressed())
        #Render
        screen.fill((0, 0, 0))
        geometry.draw(screen)
        renderSprites.draw(screen)
        pygame.display.update()
        #Delta Time
        deltaTime = clock.get_fps() / FPS
        clock.tick(FPS)
    pygame.quit()
#end