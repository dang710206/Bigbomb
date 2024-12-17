import pygame,sys
from pygame.locals import *
pygame.init()
screen=pygame.display.set_mode((670,564))
pygame.display.set_caption('Game thầy Dũng')
fpsClock=pygame.time.Clock()
#tạo biến cho nhân vật
moving_left=False
moving_right=False
def bg():
    color1=(144,201,120)
    screen.fill(color1)
class Solider(pygame.sprite.Sprite):
    def __init__ (self,x,y,scale,speed):
        pygame.sprite.Sprite.__init__(self)
        self.speed=speed
        self.direction=1
        self.flip=False
        img=pygame.image.load('player.gif')
        self.img=pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale)))
        self.rect=self.img.get_rect()
        self.rect.center=(x,y)
    #Hàm di chuyển
    def move(self,moving_left,moving_right):
        dx=0
        dy=0
        if moving_left:
            dx=-self.speed
            self.flip=True
            self.direction=-1
        if moving_right:
            dy=self.speed
            self.flip=False
            self.direction=1
        self.rect.x+=dx
        self.rect.x+=dy
    def draw(self):
        screen.blit(pygame.transform.flip( self.img,self.flip,False),self.rect)
    

player=Solider(200,200,3,5)
while True:
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
        #Di chuyển
        if event.type==KEYDOWN:
            if event.key==pygame.K_a:
                moving_left=True
            if event.key==pygame.K_d:
                moving_right=True
        if event.type==KEYUP:
            if event.key==pygame.K_a:
                moving_left=False
            if event.key==pygame.K_d:
                moving_right=False
    bg()
    player.draw()
    player.move(moving_left,moving_right)
    
    
    fpsClock.tick(60)
    pygame.display.update()