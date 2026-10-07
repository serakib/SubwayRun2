import pygame
import random
import json
import math
from pathlib import Path

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
FPS = 60
SAVE_FILE = Path("runway_rush_save.json")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Runway Rush - Pygame")
clock = pygame.time.Clock()

FONT_BIG = pygame.font.Font(None, 70)
FONT = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)

WHITE=(240,248,255)
CYAN=(68,220,255)
DARK=(5,12,22)
PANEL=(11,25,41)
MUTED=(130,153,175)
RED=(235,75,75)
GOLD=(255,211,70)
ROAD=(39,45,55)
SKY_TOP=(7,19,39)
SKY_BOTTOM=(205,112,65)

def load_save():
    default={"best_score":0,"total_coins":0,"games":0,"sound":True}
    try:
        data=json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        for k,v in default.items():
            if k not in data:
                data[k]=v
        return data
    except (OSError, json.JSONDecodeError):
        return default

save=load_save()

def persist():
    try:
        SAVE_FILE.write_text(json.dumps(save, indent=2), encoding="utf-8")
    except OSError:
        pass

def beep(freq=600, duration=0.045):
    if not save["sound"]:
        return
    try:
        sample_rate=44100
        n=int(sample_rate*duration)
        buf=bytearray()
        for i in range(n):
            value=int(10000*math.sin(2*math.pi*freq*i/sample_rate))
            buf.extend(int(value).to_bytes(2,"little",signed=True))
        sound=pygame.mixer.Sound(buffer=bytes(buf))
        sound.play()
    except Exception:
        pass

class Player:
    def __init__(self):
        self.lane=1
        self.y=0.0
        self.vy=0.0
        self.jumping=False
        self.sliding=False
        self.slide_timer=0.0

    def reset(self):
        self.__init__()

    def move(self,direction):
        self.lane=max(0,min(2,self.lane+direction))

    def jump(self):
        if not self.jumping:
            self.jumping=True
            self.sliding=False
            self.vy=1.18
            beep(520)

    def slide(self):
        if not self.jumping:
            self.sliding=True
            self.slide_timer=0.48

    def update(self,dt):
        self.y += self.vy*dt*2.7
        self.vy -= 2.65*dt
        if self.y<=0:
            self.y=0
            self.vy=0
            self.jumping=False
        if self.sliding:
            self.slide_timer-=dt
            if self.slide_timer<=0:
                self.sliding=False

class Object:
    def __init__(self,lane,kind,z=1.05):
        self.lane=lane
        self.kind=kind
        self.z=z
        self.collected=False

class Game:
    def __init__(self):
        self.player=Player()
        self.state="menu"
        self.score=0.0
        self.coins=0
        self.speed=0.34
        self.distance=0.0
        self.spawn_timer=0.0
        self.objects=[]

    def start(self):
        self.state="playing"
        self.score=0
        self.coins=0
        self.speed=0.34
        self.distance=0
        self.spawn_timer=0
        self.objects.clear()
        self.player.reset()
        save["games"]+=1
        persist()

    def game_over(self):
        self.state="gameover"
        self.score=int(self.score)
        save["best_score"]=max(save["best_score"],self.score)
        save["total_coins"]+=self.coins
        persist()
        beep(110,0.12)

    def spawn(self):
        lane=random.randrange(3)
        roll=random.random()
        kind="coin" if roll<0.52 else ("barrier" if roll<0.84 else "crate")
        self.objects.append(Object(lane,kind))
        if random.random()<0.28:
            second=(lane+random.choice([1,2]))%3
            self.objects.append(Object(second,"coin",1.24))

    def update(self,dt):
        if self.state!="playing":
            return

        self.distance+=self.speed*dt
        self.score+=self.speed*dt*110
        self.speed=min(0.72,self.speed+dt*0.0035)
        self.player.update(dt)

        self.spawn_timer-=dt
        if self.spawn_timer<=0:
            self.spawn()
            self.spawn_timer=max(0.38,0.92-self.speed*0.45)

        for obj in self.objects:
            obj.z-=self.speed*dt
            if obj.z<0.075 and not obj.collected and obj.lane==self.player.lane:
                if obj.kind=="coin":
                    obj.collected=True
                    self.coins+=1
                    self.score+=80
                    beep(760,0.035)
                else:
                    safe_jump=self.player.y>0.25
                    safe_slide=self.player.sliding
                    if not safe_jump and not safe_slide:
                        self.game_over()
                        return

        self.objects=[o for o in self.objects if o.z>-0.08 and not o.collected]

game=Game()

def road_geometry():
    horizon=HEIGHT*0.27
    bottom=HEIGHT*1.02
    center=WIDTH/2
    top_half=WIDTH*0.11
    bottom_half=WIDTH*0.49
    return horizon,bottom,center,top_half,bottom_half

def lane_x(lane,z):
    _,_,center,top_half,bottom_half=road_geometry()
    t=max(0,min(1,1-z))
    half=top_half+(bottom_half-top_half)*t
    return center+(lane-1)*half*0.58

def draw_world():
    sky=pygame.Surface((WIDTH,HEIGHT))
    for y in range(HEIGHT):
        t=y/HEIGHT
        c=tuple(int(SKY_TOP[i]*(1-t)+SKY_BOTTOM[i]*t) for i in range(3))
        pygame.draw.line(sky,c,(0,y),(WIDTH,y))
    screen.blit(sky,(0,0))

    horizon,bottom,center,top_half,bottom_half=road_geometry()

    pygame.draw.circle(screen,(255,220,145),(int(WIDTH*.78),int(HEIGHT*.18)),55)

    for i in range(18):
        bw=WIDTH/18
        bh=15+((i*37)%48)
        pygame.draw.rect(screen,(9,28,43),(int(i*bw),int(horizon-bh),int(bw-2),int(bh)))

    road=[(center-top_half,horizon),(center+top_half,horizon),
          (center+bottom_half,bottom),(center-bottom_half,bottom)]
    pygame.draw.polygon(screen,ROAD,road)

    pygame.draw.line(screen,(243,201,106),(center-top_half,horizon),(center-bottom_half,bottom),4)
    pygame.draw.line(screen,(243,201,106),(center+top_half,horizon),(center+bottom_half,bottom),4)

    for lane in range(2):
        xt=center+(-top_half*.33 if lane==0 else top_half*.33)
        xb=center+(-bottom_half*.33 if lane==0 else bottom_half*.33)
        pygame.draw.line(screen,(150,165,175),(xt,horizon),(xb,bottom),2)

    for i in range(12):
        z=((i/12+game.distance*.8)%1)
        y=horizon+(z**1.7)*(bottom-horizon)
        half=top_half+(bottom_half-top_half)*z
        sw=max(2,half*.018)
        pygame.draw.rect(screen,(235,240,245),(int(center-sw/2),int(y),int(sw),int(4+z*9)))

    for obj in sorted(game.objects,key=lambda o:o.z,reverse=True):
        draw_object(obj)

    draw_player()

def draw_object(obj):
    horizon,_,_,_,_=road_geometry()
    t=max(0,min(1,1-obj.z))
    y=horizon+(t**1.7)*(HEIGHT*.76)
    scale=.2+t*1.05
    x=lane_x(obj.lane,obj.z)

    if obj.kind=="coin":
        r=int(8+14*scale)
        pygame.draw.circle(screen,GOLD,(int(x),int(y-r*.6)),r)
        pygame.draw.circle(screen,(255,240,165),(int(x),int(y-r*.6)),r,3)
        text=FONT_SMALL.render("$",True,(130,85,10))
        screen.blit(text,text.get_rect(center=(x,y-r*.6)))
    else:
        w=int(34+42*scale)
        h=int((24+25*scale) if obj.kind=="barrier" else (34+42*scale))
        color=(228,72,72) if obj.kind=="barrier" else (185,105,56)
        rect=pygame.Rect(int(x-w/2),int(y-h),w,h)
        pygame.draw.rect(screen,color,rect)
        pygame.draw.rect(screen,(255,255,255),rect,2)
        if obj.kind=="barrier":
            pygame.draw.rect(screen,(255,239,166),(rect.x,rect.y+int(h*.42),rect.w,max(4,int(h*.14))))
        else:
            pygame.draw.line(screen,(100,45,20),rect.topleft,rect.bottomright,2)
            pygame.draw.line(screen,(100,45,20),rect.topright,rect.bottomleft,2)

def draw_player():
    x=lane_x(game.player.lane,.02)
    ground=HEIGHT*.88
    jump_y=game.player.y*HEIGHT*.18
    sliding=game.player.sliding
    body_w=54 if sliding else 38
    body_h=30 if sliding else 62

    pygame.draw.ellipse(screen,(15,15,20),(x-32,ground-4,x*0+64,16))
    pygame.draw.rect(screen,CYAN,(int(x-body_w/2),int(ground-body_h-jump_y),body_w,body_h))

    if not sliding:
        pygame.draw.circle(screen,(255,208,170),(int(x),int(ground-body_h-15-jump_y)),15)
        pygame.draw.rect(screen,(23,32,51),(int(x-15),int(ground-body_h-21-jump_y),30,8))

    pygame.draw.rect(screen,(245,248,255),(int(x-20),int(ground-5-jump_y),16,8))
    pygame.draw.rect(screen,(245,248,255),(int(x+4),int(ground-5-jump_y),16,8))

def text_center(text,font,color,y):
    surf=font.render(text,True,color)
    screen.blit(surf,surf.get_rect(center=(WIDTH//2,y)))

def draw_panel():
    overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    overlay.fill((2,8,15,170))
    screen.blit(overlay,(0,0))
    rect=pygame.Rect(WIDTH//2-260,HEIGHT//2-185,520,370)
    pygame.draw.rect(screen,PANEL,rect,border_radius=22)
    pygame.draw.rect(screen,(43,67,90),rect,2,border_radius=22)

def draw_ui():
    pygame.draw.rect(screen,(8,20,33),(15,15,970,74),border_radius=15)
    score_s=FONT.render(f"SCORE  {int(game.score)}",True,WHITE)
    coin_s=FONT.render(f"COINS  {game.coins}",True,GOLD)
    best_s=FONT.render(f"BEST  {save['best_score']}",True,CYAN)
    screen.blit(score_s,(35,35))
    screen.blit(coin_s,(405,35))
    screen.blit(best_s,(735,35))

def draw_menu():
    draw_panel()
    text_center("RUNWAY RUSH",FONT_BIG,WHITE,215)
    text_center("PYGAME EDITION",FONT_SMALL,CYAN,270)
    text_center("3-LANE ENDLESS RUNNER",FONT_SMALL,MUTED,305)
    button("START RUN",pygame.Rect(350,345,300,58),True)
    text_center("← → Move   ↑ Jump   ↓ Slide   P Pause",FONT_SMALL,MUTED,440)

def draw_pause():
    draw_panel()
    text_center("PAUSED",FONT_BIG,WHITE,235)
    button("RESUME",pygame.Rect(350,315,300,55),True)
    button("QUIT",pygame.Rect(350,385,300,55),False)

def draw_gameover():
    draw_panel()
    text_center("RUN OVER",FONT_BIG,WHITE,190)
    text_center(f"Score: {int(game.score)}",FONT,WHITE,275)
    text_center(f"Coins: {game.coins}",FONT,GOLD,315)
    text_center(f"Best: {save['best_score']}",FONT,CYAN,355)
    button("RUN AGAIN",pygame.Rect(350,405,300,55),True)

def button(label,rect,primary):
    color=CYAN if primary else (19,36,55)
    txt=DARK if primary else WHITE
    pygame.draw.rect(screen,color,rect,border_radius=12)
    pygame.draw.rect(screen,(60,85,108),rect,2,border_radius=12)
    surf=FONT.render(label,True,txt)
    screen.blit(surf,surf.get_rect(center=rect.center))

def handle_click(pos):
    x,y=pos
    if game.state=="menu":
        if pygame.Rect(350,345,300,58).collidepoint(pos):
            game.start()
    elif game.state=="paused":
        if pygame.Rect(350,315,300,55).collidepoint(pos):
            game.state="playing"
        elif pygame.Rect(350,385,300,55).collidepoint(pos):
            game.state="menu"
    elif game.state=="gameover":
        if pygame.Rect(350,405,300,55).collidepoint(pos):
            game.start()

running=True
while running:
    dt=min(clock.tick(FPS)/1000,0.04)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        elif event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT,pygame.K_a):
                game.player.move(-1)
            elif event.key in (pygame.K_RIGHT,pygame.K_d):
                game.player.move(1)
            elif event.key in (pygame.K_UP,pygame.K_w,pygame.K_SPACE):
                game.player.jump()
            elif event.key in (pygame.K_DOWN,pygame.K_s):
                game.player.slide()
            elif event.key in (pygame.K_p,pygame.K_ESCAPE):
                if game.state=="playing":
                    game.state="paused"
                elif game.state=="paused":
                    game.state="playing"

        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            handle_click(event.pos)

    game.update(dt)
    draw_world()
    draw_ui()

    if game.state=="menu":
        draw_menu()
    elif game.state=="paused":
        draw_pause()
    elif game.state=="gameover":
        draw_gameover()

    pygame.display.flip()

pygame.quit()
