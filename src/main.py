import pygame
# Config
SCREEN_WIDTH = 480 * 2
SCREEN_HEIGHT = 360 * 2

# Initialize Game
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Progress Text
progress = pygame.font.SysFont('Comic Sans MS', 20).render('give me a second bud... (yes, this is comic sans)', True, (255, 255, 255))
screen.blit(progress, (SCREEN_WIDTH-progress.get_width(), SCREEN_HEIGHT-progress.get_height()))
pygame.display.update()
# Window Config
pygame.display.set_caption('platformer') #Window Caption (top left thingy)
#pygame.display.set_icon(pygame.image.load('graphics/icon.ico'))

# Import Modules
from pygame.locals import *
import pygameplus
import pygame.math as math
import mpd
# Game Constants
Gravity = .5
FPS = pygame.display.get_current_refresh_rate() #0 = Unlimited
HalfScrX = SCREEN_WIDTH//2
HalfScrY = SCREEN_HEIGHT//2

level = mpd.ReadLevel(open('map/level.mpd', 'rb'))

class Camera():
    def __init__(cam):
        cam.x = 0
        cam.y = 0

class player(pygame.sprite.Sprite):
    # Player Config
    def __init__(plr):
        super().__init__()
        # Looks
        plr.image = pygame.Surface((10, 20)) # Player Size
        plr.image.fill((255, 255, 255))
        plr.rect = plr.image.get_rect()
        # Position
        plr.rect.center = (HalfScrX, HalfScrY)
        plr.startingX = plr.rect.x
        # States
        plr.grounded = False
        plr.crouch = False
        plr.health = 3
        plr.JumpsDone = 0
        plr.JumpHeldFrames = 0
        #Base X Cap (caps revert to)
        #B = is base cap?: a/g/c/h = type (c = crouch, h = hard): VCX/Y = Velocity Cap X/Y
        plr.BaVCX = 10 #Base Airborne VX Cap
        plr.BgVCX = 5 #Base Grounded VX Cap
        plr.BcVCX = 3 #Base Crouching Cap
        #X Cap (gets changed during gameplay)
        plr.aVCX = plr.BaVCX #Airborne
        plr.gVCX = plr.BgVCX #Grounded
        plr.cVCX = plr.BcVCX #Crouched
        plr.hVCX = 20 #X Hard Cap (if vx over clamp vx no matter the state)
        #VY Cap
        plr.VCY = 10
        #Movement
        plr.accel = .4 #How Fast You Can Reach The Cap
        plr.crAccel = .2 #Acceleration while crouching
        plr.AirAccel = .2 #Airborne Acceleration
        plr.deccel = .9 #Shoe Grippies
        plr.vx = 0 #X Velocity
        plr.vy = 0 #Y Velocity
        #Sounds
        def GetAudio(filename): return pygame.mixer.Sound(f'snd/{filename}.wav')
        plr.sndjump = GetAudio('jmp')
        plr.sndland = GetAudio('lnd')
        plr.sndbonk = GetAudio('bnk')
        del GetAudio
    
    # Player Loop
    def update(plr, keys):
        def ChangeSurfaceRect(size):
            oldPos = plr.rect.center
            plr.image = pygame.Surface(size)
            plr.rect = plr.image.get_rect()
            plr.image.fill((255, 255, 255))
            plr.rect.center = oldPos
        #Crouch
        if keys[K_LSHIFT]:
            ChangeSurfaceRect((16, 16))
            if not plr.crouch:
                plr.rect.y += 8
                plr.crouch = True
        else:
            ChangeSurfaceRect((16, 32))
            if plr.crouch:
                plr.rect.y -= 8
                if pygame.sprite.spritecollideany(plr, geometry):
                    ChangeSurfaceRect((16, 16))
                    plr.rect.y += 8
                else: plr.crouch = False
        #Reset
        if keys[K_r]:
            plr.__init__()
            cam.__init__()

        # Movement
        moveX = keys[K_d]-keys[K_a]
        if moveX != 0:
            gun.dir = moveX
        def Movement(accel=int or float, cap=int or float, NoInputDeccel=True):
            #X Movement
            if moveX == 0 and NoInputDeccel: #Check if not trying to move, and 'NoInputDeccel' is true, then deccel vx.
                plr.vx *= plr.deccel
                if round(plr.vx) == 0: plr.vx = 0
            else: #Move player
                plr.vx += accel * moveX
            #Speed Cap
            plr.vx = math.clamp(plr.vx, -plr.hVCX, plr.hVCX) #Hard Cap
            plr.vx = math.clamp(plr.vx, -cap, cap) #Normal Cap

        if plr.grounded: #Grounded
            if plr.crouch: #Check crouched
                Movement(plr.crAccel, plr.cVCX) #Crouched
            else: Movement(plr.accel, plr.gVCX) #Not crouched (Grounded)
        else: Movement(plr.AirAccel, plr.aVCX, False) #Airborne
        
        #Jump
        if keys[K_SPACE] and (plr.JumpHeldFrames > 0 or plr.grounded or plr.JumpsDone < 2):
            plr.JumpHeldFrames += 1
        else: plr.JumpHeldFrames = 0
        
        if (plr.grounded or plr.JumpsDone < 2) and plr.JumpHeldFrames == 1:
                plr.JumpsDone += 1
                plr.vy = plr.JumpsDone < 2 and -6 or -3
                plr.aVCX = math.clamp(abs(plr.vx), 2, plr.BaVCX)
                plr.grounded = False
                plr.sndjump.play()
        elif pygameplus.WithinRange(plr.JumpHeldFrames, 5, 8) and plr.JumpsDone > 0:            
            plr.vy -= 8/plr.JumpHeldFrames

        # VY Cap
        plr.vy = math.clamp(plr.vy, -plr.VCY, plr.VCY)
        
        def Touching(): return pygame.sprite.spritecollideany(plr, geometry)
        def GroundedCheck():
            plr.rect.y += 1
            touch = Touching()
            plr.rect.y -= 1
            return touch
        # X Collision
        plr.rect.x += plr.vx * delta
        if Touching():
            if plr.vx != 0:
                velDir = plr.vx > 0 and 1 or -1
                while Touching():
                    plr.rect.x -= velDir
                plr.vx = 0
        # X Camera Scrolling
        cam.x += plr.rect.x - HalfScrX
        cam.x = math.clamp(cam.x, 0, 18446744073709551615)
        if cam.x != 0:
            plr.rect.x = HalfScrX
        
        # Y Collision
        plr.rect.y += plr.vy
        if Touching():
            if plr.vy != 0:
                velDir = plr.vy > 0 and 1 or -1
                while Touching():
                    plr.rect.y -= velDir

                if plr.JumpsDone > 0 and plr.vy >= 0:
                    plr.JumpsDone = 0
                    plr.aVCX = plr.BaVCX
            if plr.vy > 0 and GroundedCheck():
                plr.grounded = True
                plr.sndland.play()
                plr.vy = 0
            else: #Head bonk on ceiling
                plr.sndbonk.play()
                plr.JumpHeldFrames = 9
                plr.vy = 1
        elif GroundedCheck():
            plr.grounded = True
        else:
            plr.grounded = False
            plr.aVCX = math.clamp(abs(plr.vx), 3, plr.BaVCX)
            plr.vy += Gravity

class Gun(pygame.sprite.Sprite):
    def __init__(gun):
        super().__init__()
        gun.image = pygame.image.load('res/sprite/gun.bmp').convert_alpha()
        gun.image = pygame.transform.scale(gun.image, (20, 16))
        gun.fimage = gun.image
        gun.bimage = pygame.transform.flip(gun.image, True, False)
        gun.dir = 1
        gun.sndfire = pygame.mixer.Sound('snd/sht.wav')
        gun.rect = gun.image.get_rect()
    def update(gun):
        if gun.dir == 1:
            gun.image = gun.fimage
        else: gun.image = gun.bimage
        gun.rect.x = plr.rect.x + (10 * gun.dir)
        gun.rect.y = plr.rect.y + 5
        if ms.get_just_pressed()[0]:
            gun.sndfire.play()
            print(pygameplus.Raycast(geometry, gun.dir, gun.rect.center, ScrX=SCREEN_WIDTH))

# Main
if __name__ == '__main__':
    plr = player()
    cam = Camera()
    gun = Gun()
    sprites = pygame.sprite.Group(plr, gun)
    renderSprites = sprites.copy()
    Running = True
    clock = pygameplus.clock
    delta = 1
    ms = pygame.mouse
    geometry = mpd.LoadEntireLevel(level)
    while Running:
        #Update
        delta = pygameplus.GetDeltaTime()
        for event in pygame.event.get():
            Running = event.type != QUIT
        plr.update(pygame.key.get_pressed())
        gun.update()
        geometry.update(cam.x, cam.y)
        #Render
        screen.fill((0, 0, 0))
        geometry.draw(screen)
        renderSprites.draw(screen)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()