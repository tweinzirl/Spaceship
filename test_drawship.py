#! /usr/bin/env python
#draw ship, set color for thrust
#test rotation of ship
#test ship movement; movement wraps around screen

import pygame
from pygame.locals import *
from gameobjects.vector2 import Vector2
from math import *
from sys import exit
import numpy

pygame.init()
SCREENSIZE=(640,480)
font = pygame.font.SysFont("liberationsans", 14);
font_height = font.get_linesize()

class Ship(pygame.sprite.Sprite):
    def __init__(self,x=SCREENSIZE[0]/2., y=SCREENSIZE[1]/2., s=40):

        pygame.sprite.Sprite.__init__(self)
        self.health=100
        self.thrust=0
        self.speed=Vector2()
        self.rotate=0
        self.rotation_speed=120 #degrees per second
        self.heading=Vector2()

        self.projectiles={} #dict for projectiles
        self.n_projectile=0 #id of next bullet fired
       
        #define vertices -> store vertices as matrix or 2D list
        self.position=Vector2(x,y) 
        dx,dy = int(s*sin(30*pi/180)), int(s*cos(30*pi/180))
        self.dx,self.dy=dx,dy
        self.p0=Vector2(dx,0)
        #self.cannonh=0.3*dy #length of cannons
        self.cannonh=0.325*dy #length of cannons
        self.p1 = self.p0 + Vector2(-dx,dy)
        self.p2 = self.p0 + Vector2(dx,dy)
        self.p3 = self.p0 + Vector2(0,1/2.*dy)
        '''
        self.p4 = Vector2(0.5*dx,0.5*dy) #bottom of left blaster
        self.p5 = Vector2(1.5*dx,0.5*dy) #bottom of right blaster
        self.p6 = Vector2(0.5*dx,0.5*dy-self.cannonh) #top of left blaster
        self.p7 = Vector2(1.5*dx,0.5*dy-self.cannonh) #top of right blaster
        '''
        self.p4 = Vector2(0.25*dx,0.75*dy) #bottom of left blaster
        self.p5 = Vector2(1.75*dx,0.75*dy) #bottom of right blaster
        self.p6 = Vector2(0.25*dx,0.75*dy-self.cannonh) #top of left blaster
        self.p7 = Vector2(1.75*dx,0.75*dy-self.cannonh) #top of right blaster
        self.V = numpy.matrix([[self.p0.x,self.p1.x,self.p2.x,self.p3.x,self.p4.x,self.p5.x,self.p6.x,self.p7.x], [self.p0.y,self.p1.y,self.p2.y,self.p3.y,self.p4.y,self.p5.y,self.p6.y,self.p7.y], [1,1,1,1,1,1,1,1]]) #matrix of vertices; V[:,0]=p0, V[:,7]=p7
        self.A1 = numpy.matrix([[1,0,-dx], [0,1,-0.5*dy], [0,0,1]]) #matrix to change origin to center of image from upper upper left-hand corner, keeping y axis pointing in same downward direction

        #draw two surfaces, one for thrust, one for no thrust, and store
        self.surf_thrust=pygame.Surface( (2*self.dx, self.dy), SRCALPHA ).convert_alpha() #surface for thrust version
        self.initDraw(self.surf_thrust,thrust=1)
        self.surf_nothrust=pygame.Surface( (2*self.dx, self.dy), SRCALPHA ).convert_alpha() #surface for no thrust version
        self.initDraw(self.surf_nothrust,thrust=0)

        #assign self.image, self.rect from Sprite
        self.image=self.surf_nothrust
        self.rect=self.image.get_rect()
    
    def initDraw(self,surf,thrust=0):
        surf.lock()
        pygame.draw.line(surf, (255,255,255), self.p0, self.p1, 2)
        pygame.draw.line(surf, (255,255,255), self.p0, self.p2, 2)
        pygame.draw.line(surf, (255,127,36), self.p4, self.p4-Vector2(0,self.cannonh), 2) #left blaster
        pygame.draw.line(surf, (255,127,36), self.p5, self.p5-Vector2(0,self.cannonh), 2) #right blaster
        if not thrust:
            pygame.draw.line(surf, (255,255,255), self.p1, self.p3, 2)
            pygame.draw.line(surf, (255,255,255), self.p2, self.p3, 2)
        else:
            pygame.draw.line(surf, (255,69,0), self.p1, self.p3, 2)
            pygame.draw.line(surf, (255,69,0), self.p2, self.p3, 2)
        surf.unlock()

    def wrap(self):
        #update orientation
        if self.thrust:
            self.image=pygame.transform.rotate(self.surf_thrust, self.rotate)
        else:
            self.image=pygame.transform.rotate(self.surf_nothrust, self.rotate)

        w,h=self.image.get_size()
        self.rect=self.image.get_rect()

        #wrap ship around screen if out of bounds
        if self.position[0] < -w: self.position[0]=SCREENSIZE[0]
        elif self.position[0] > SCREENSIZE[0]: self.position[0]= -w #right edge of image is at x=0
        if self.position[1] < -h: self.position[1]=SCREENSIZE[1]
        elif self.position[1] > SCREENSIZE[1]: self.position[1]= -h #bottom edge at y=0

        #finally update self.rect from position 
        self.rect.center=(self.position.x,self.position.y)

    def move(self,time_pass_sec): #update heading and position
        self.heading=Vector2(cos((self.rotate+90)*pi/180.),sin((self.rotate+90)*pi/180.))
        #heading is not used directly for movement if thrust is on, then heading is added to self.speed
        if self.thrust: 
            self.speed.x+=self.heading.x
            self.speed.y-=self.heading.y #minus means up on screen is decreasing y
        self.position+=self.speed*time_pass_sec

    def update(self,time_pass_sec):
        self.wrap()
        self.move(time_pass_sec)

    def shoot(self): 
        theta=(-self.rotate)*pi/180 #reverse sign for cc-wise rotation
        A2 = numpy.matrix([[cos(theta),-sin(theta),0], [sin(theta),cos(theta),0], [0,0,1]]) #rotation matrix for ship
        A3 = numpy.matrix([[1,0,self.position.x], [0,1,self.position.y], [0,0,1]]) #translate ship to current position
        V2=A3*A2*self.A1*self.V #composite transformation taking into account coordinate translation, rotation, and final translation
         
        #print 'theta: ',theta*180/pi, ' left cannon top:\n', V2[:,6] 
        #print 'theta: ',theta*180/pi, ' right cannon top:\n', V2[:,7]

        #calculate position of canons
        p1_origin = Vector2((V2[0,6], V2[1,6]))
        p2_origin = Vector2((V2[0,7], V2[1,7]))

        #make/store projectiles
        self.projectiles[self.n_projectile]=p1=Projectile(p1_origin,self.speed,self.heading) #left cannon
        self.n_projectile+=1
        self.projectiles[self.n_projectile]=p2=Projectile(p2_origin,self.speed,self.heading) #right cannon
        self.n_projectile+=1
        return p1,p2

    def explode(self): #?
        pass

class Projectile(pygame.sprite.Sprite):
    def __init__(self,position,speed,heading,r=2):

        pygame.sprite.Sprite.__init__(self)
        self.position=Vector2(position.x,position.y) #origin should be blaster that fired
        self.speed=Vector2(speed.x,speed.y) #speed should be ship speed + some boost
        self.heading=Vector2(heading.x,heading.y) 
        self.radius=r #projectile radius
        self.age=0 #age in sec

        #add boost to speed, parallel to heading
        v=200 #pix/sec
        self.speed.x += v*heading.x
        self.speed.y -= v*heading.y #minus means up on screen is decreasing y

        #assign self.image, self.rect from Sprite
        self.image=pygame.Surface( (2*self.radius, 2*self.radius), SRCALPHA ).convert_alpha()
        self.rect=self.image.get_rect()

        #draw object
        #pygame.draw.circle(self.image,(0,255,255),(self.radius,self.radius),self.radius)
        pygame.draw.circle(self.image,(000,255,100),(self.radius,self.radius),self.radius)

        print 'New Projectile fired at position: ',self.position, ' with speed: ', self.speed, ' with heading: ',self.heading

    def wrap(self):
       w=h=2*self.radius

       #wrap around screen
       if self.position[0] < -w: self.position[0] = SCREENSIZE[0]
       elif self.position[0] > SCREENSIZE[0]: self.position[0] = -w #right edge of image is at x=0
       elif self.position[1] < -h: self.position[1] = SCREENSIZE[1]
       elif self.position[1] > SCREENSIZE[1]: self.position[1] = -h #bottom edge at y=0

       #finally update self.rect from position 
       self.rect.center=(self.position.x,self.position.y)

    def move(self,time_pass_sec):
        self.position+=self.speed*time_pass_sec
    
    def update(self,time_pass_seec):
        self.wrap()
        self.move(time_pass_sec)
        self.age+=time_pass_sec
        #if age>age_threshold, kill bullet --> the World should track kill bullets


if __name__ == '__main__':

  screen=pygame.display.set_mode(SCREENSIZE,0,32)
  screen.fill((0,0,0))
  pygame.display.update() #important to set initial background; necessary if using background image

  background = pygame.Surface(SCREENSIZE)
  background.fill((0, 0, 0))
  clock = pygame.time.Clock()

  player=Ship()
  #RenderUpdates group
  pobjects=pygame.sprite.RenderUpdates()
  pobjects.add(player)

  while True:

      for event in pygame.event.get():
          if event.type == QUIT: exit()
          if event.type == KEYDOWN and event.key == K_q: exit()
          if event.type == KEYDOWN and event.key == K_SPACE: pobjects.add(player.shoot())

      time_pass_sec = clock.tick(60)/1000. #time passed in seconds between frames

      #check age of Projectiles  eliminate those w/ age>threshold
      for p in pobjects:
          if isinstance(p,Projectile):
              if p.age > 3: pobjects.remove(p)

      #check keyboard input and update ship rotate and thrust
      pressed_keys = pygame.key.get_pressed()
      if pressed_keys[K_UP]: player.thrust=1.
      else: player.thrust=0
      if pressed_keys[K_LEFT]: player.rotate+=player.rotation_speed*time_pass_sec
      elif pressed_keys[K_RIGHT]: player.rotate-=player.rotation_speed*time_pass_sec
      if pressed_keys[K_s]: player.speed=Vector2()

      #draw player objects: ship, bullets
      screen.set_clip(0,0,SCREENSIZE[0],SCREENSIZE[1]-font_height)
      pobjects.update(time_pass_sec)
      rectlist=pobjects.draw(screen)
      pygame.display.update(rectlist)
      pobjects.clear(screen,background)
   
      #text display
      clip=screen.set_clip(0,SCREENSIZE[1]-font_height,SCREENSIZE[0],font_height)
      text='Heading: (%.3f,%.3f)    Orientation: %.1f degrees    Velocity: (%.1f,%.1f)    Mouse: (%d,%d)'%(player.heading.x,player.heading.y, player.rotate+90, player.speed.x,player.speed.y, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
      screen.blit(background,(0,SCREENSIZE[1]-font_height),(0,SCREENSIZE[1]-font_height,SCREENSIZE[0],font_height))
      screen.blit( font.render(text, True, (255, 255, 255)), (10, SCREENSIZE[1]-font_height) )
      pygame.display.update(screen.get_clip())
