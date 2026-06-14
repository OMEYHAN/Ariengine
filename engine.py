import json, random, math
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPainterPath, QPolygonF

# ---------- Particle ----------
class Particle:
    def __init__(self, x, y, vx=0, vy=0, life=1.0, color=QColor(255,255,255), size=4):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = 100

    def update(self, dt):
        self.life -= dt
        if self.life > 0:
            self.vy += self.gravity * dt
            self.x += self.vx * dt
            self.y += self.vy * dt
        return self.life > 0

    def draw(self, painter):
        if self.life <= 0: return
        alpha = int(255 * (self.life / self.max_life))
        color = QColor(self.color.red(), self.color.green(), self.color.blue(), alpha)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(self.x, self.y), self.size, self.size)

class ParticleSystem:
    def __init__(self): self.particles = []
    def emit(self, x, y, count=10, color=QColor(255,255,255),
             speed_range=(50,200), life_range=(0.5,1.5), size_range=(2,6)):
        for _ in range(count):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(*speed_range)
            vx = speed * random.choice([-1,1]) * random.uniform(0.3,1.0)
            vy = -speed * random.uniform(0.5,1.0)
            life = random.uniform(*life_range)
            size = random.uniform(*size_range)
            self.particles.append(Particle(x, y, vx, vy, life, color, size))
    def update(self, dt): self.particles = [p for p in self.particles if p.update(dt)]
    def draw(self, painter):
        for p in self.particles: p.draw(painter)
    def clear(self): self.particles.clear()

# ---------- Base ----------
class GameObject:
    def __init__(self, x=0, y=0, width=50, height=50):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.vx = self.vy = 0
        self.color = QColor(255,0,0)
        self.active = True; self.tag = ""
        self.properties = {}
        self.is_static = False; self.has_gravity = True

    def update(self, dt, gravity=0):
        if not self.is_static:
            self.x += self.vx * dt
            if self.has_gravity and gravity: self.vy += gravity * dt
            self.y += self.vy * dt

    def draw(self, painter, animation_timer=0.0):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

    def get_rect(self): return QRectF(self.x, self.y, self.width, self.height)
    def check_collision(self, other): return self.get_rect().intersects(other.get_rect())

    def to_dict(self):
        return {'type':self.__class__.__name__,'x':self.x,'y':self.y,
                'width':self.width,'height':self.height,'color':self.color.name(),
                'tag':self.tag,'is_static':self.is_static,'has_gravity':self.has_gravity,
                'properties':self.properties}
    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'],data['y'],data['width'],data['height'])
        obj.color = QColor(data['color']); obj.tag = data['tag']
        obj.is_static = data.get('is_static',False); obj.has_gravity = data.get('has_gravity',True)
        obj.properties = data.get('properties',{}); return obj

# ---------- Player ----------
class Player(GameObject):
    def __init__(self, x=0, y=0, width=40, height=60):
        super().__init__(x, y, width, height)
        self.color = QColor(0,100,255); self.tag = "player"
        self.properties = {'walk_speed':200,'run_speed':400,'jump_force':-500,
                           'max_jumps':2,'current_jumps':0,'health':100,'max_health':100,
                           'can_sprint':True,'can_jump':True,
                           'model':'classic','animation':'idle'}
        self.is_on_ground=False; self.facing_right=True; self.speed=200

    def draw(self, painter, animation_timer=0.0):
        model = self.properties.get('model','classic')
        anim = self.properties.get('animation','idle')
        t = animation_timer
        painter.save()
        cx = self.x + self.width/2; cy = self.y + self.height/2
        painter.translate(cx, cy)
        if not self.facing_right: painter.scale(-1,1)
        painter.translate(-cx, -cy)

        if model == 'classic':
            if anim == 'idle':
                painter.setBrush(QBrush(self.color))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
                painter.setBrush(QBrush(QColor(255,255,255)))
                painter.drawEllipse(int(self.x+self.width-15), int(self.y+10), 8, 8)
            elif anim == 'walk':
                leg_offset = int(3 * math.sin(t * 10))
                painter.setBrush(QBrush(self.color))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
                # پاها
                painter.drawRect(int(self.x+5), int(self.y+self.height+leg_offset), 8, 6)
                painter.drawRect(int(self.x+self.width-13), int(self.y+self.height-leg_offset), 8, 6)
                painter.setBrush(QBrush(QColor(255,255,255)))
                painter.drawEllipse(int(self.x+self.width-15), int(self.y+10), 8, 8)
            elif anim == 'jump':
                painter.setBrush(QBrush(self.color))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height-8))
                painter.drawRect(int(self.x+5), int(self.y+self.height-8), 8, 8)
                painter.drawRect(int(self.x+self.width-13), int(self.y+self.height-8), 8, 8)
                painter.setBrush(QBrush(QColor(255,255,255)))
                painter.drawEllipse(int(self.x+self.width-15), int(self.y+10), 8, 8)

        elif model == 'slime':
            bounce = int(3 * math.sin(t * 5))
            if anim == 'idle' or anim == 'walk':
                path = QPainterPath()
                path.addEllipse(QRectF(self.x+2, self.y+8+bounce, self.width-4, self.height-8))
                path.addEllipse(QRectF(self.x+5, self.y+bounce, self.width-10, 20))
                painter.setBrush(QBrush(self.color))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawPath(path)
                painter.setBrush(QBrush(QColor(255,255,255)))
                painter.drawEllipse(int(self.x+self.width-12), int(self.y+12+bounce), 6, 6)
            elif anim == 'jump':
                path = QPainterPath()
                path.addEllipse(QRectF(self.x+2, self.y+8, self.width-4, self.height-12))
                path.addEllipse(QRectF(self.x+5, self.y, self.width-10, 18))
                painter.setBrush(QBrush(self.color))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawPath(path)
                painter.setBrush(QBrush(QColor(255,255,255)))
                painter.drawEllipse(int(self.x+self.width-12), int(self.y+10), 6, 6)

        elif model == 'robot':
            if anim == 'idle':
                painter.setBrush(QBrush(self.color))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawRect(int(self.x+5), int(self.y), int(self.width-10), int(self.height))
                painter.drawRect(int(self.x), int(self.y+10), 5, 10)
                painter.drawRect(int(self.x+self.width-5), int(self.y+10), 5, 10)
                painter.drawRect(int(self.x+10), int(self.y-6), 6, 6)
                painter.drawLine(int(self.x+10), int(self.y-10), int(self.x+13), int(self.y-15))
                painter.drawLine(int(self.x+20), int(self.y-10), int(self.x+17), int(self.y-15))
                painter.setBrush(QBrush(QColor(255,255,0)))
                painter.drawEllipse(int(self.x+self.width-12), int(self.y+12), 5, 5)
            elif anim == 'walk':
                leg_phase = int(2 * math.sin(t * 10))
                painter.setBrush(QBrush(self.color))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawRect(int(self.x+5), int(self.y), int(self.width-10), int(self.height))
                painter.drawRect(int(self.x), int(self.y+10+leg_phase), 5, 10)
                painter.drawRect(int(self.x+self.width-5), int(self.y+10-leg_phase), 5, 10)
                painter.drawRect(int(self.x+10), int(self.y-6), 6, 6)
                painter.drawLine(int(self.x+10), int(self.y-10), int(self.x+13), int(self.y-15))
                painter.drawLine(int(self.x+20), int(self.y-10), int(self.x+17), int(self.y-15))
                painter.setBrush(QBrush(QColor(255,255,0)))
                painter.drawEllipse(int(self.x+self.width-12), int(self.y+12), 5, 5)
            elif anim == 'jump':
                painter.setBrush(QBrush(self.color))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawRect(int(self.x+5), int(self.y), int(self.width-10), int(self.height-8))
                painter.drawRect(int(self.x), int(self.y+10), 5, 6)
                painter.drawRect(int(self.x+self.width-5), int(self.y+10), 5, 6)
                painter.drawRect(int(self.x+10), int(self.y-6), 6, 6)
                painter.setBrush(QBrush(QColor(255,255,0)))
                painter.drawEllipse(int(self.x+self.width-12), int(self.y+10), 5, 5)

        painter.restore()

        hp = self.properties.get('health',100); mhp = self.properties.get('max_health',100)
        if hp < mhp:
            bw = self.width; bh = 5; by = self.y-10
            painter.setBrush(QBrush(QColor(255,0,0))); painter.drawRect(int(self.x), int(by), int(bw), bh)
            painter.setBrush(QBrush(QColor(0,255,0))); painter.drawRect(int(self.x), int(by), int(bw*hp//mhp), bh)

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'],data['y'],data.get('width',40),data.get('height',60))
        obj.color = QColor(data.get('color','#0064FF')); obj.tag='player'
        obj.is_static=data.get('is_static',False); obj.has_gravity=data.get('has_gravity',True)
        props = data.get('properties',{}); obj.properties.update(props)
        obj.speed = obj.properties.get('walk_speed',200)
        obj.properties.setdefault('model','classic'); obj.properties.setdefault('animation','idle')
        return obj

# ---------- Enemy ----------
class Enemy(GameObject):
    def __init__(self, x=0, y=0, width=40, height=40):
        super().__init__(x, y, width, height)
        self.color = QColor(255,50,50); self.tag = "enemy"
        self.has_gravity = True
        self.properties = {'patrol_range':100,'speed':100,'damage':20,'patrol_type':'horizontal',
                           'ai_type':'patrol','detection_range':200,'chase_speed':150,
                           'jump_force':-400,'jump_interval':1.5,
                           'model':'skeleton','animation':'idle'}
        self.start_x, self.start_y = x, y
        self.direction=1; self.is_on_ground=False; self._jump_timer=0.0

    def update(self, dt, gravity=0, player=None):
        ai=self.properties.get('ai_type','patrol'); speed=self.properties.get('speed',100)
        pr=self.properties.get('patrol_range',100); det=self.properties.get('detection_range',200)
        chase=self.properties.get('chase_speed',150)
        if ai=='patrol': self._patrol(dt,speed,pr)
        elif ai=='chase': self._chase(dt,speed,pr,chase,det,player)
        elif ai=='static': pass
        elif ai=='jumper': self._jumper(dt,gravity)
        if self.has_gravity and gravity: self.vy += gravity*dt; self.y += self.vy*dt

    def _patrol(self, dt, speed, pr):
        if self.properties.get('patrol_type','horizontal')=='horizontal':
            self.x += self.direction*speed*dt
            if self.x>self.start_x+pr: self.direction=-1
            elif self.x<self.start_x-pr: self.direction=1
        else:
            self.y += self.direction*speed*dt
            if self.y>self.start_y+pr: self.direction=-1
            elif self.y<self.start_y-pr: self.direction=1

    def _chase(self, dt, patrol_spd, pr, chase_spd, det, player):
        if not player: self._patrol(dt, patrol_spd, pr); return
        dx = player.x - self.x; dy = player.y - self.y
        if abs(dx)<det and abs(dy)<150:
            self.direction = 1 if dx>0 else -1
            self.x += self.direction*chase_spd*dt
        else: self._patrol(dt, patrol_spd, pr)

    def _jumper(self, dt, gravity):
        self._jump_timer += dt
        if self._jump_timer >= self.properties.get('jump_interval',1.5):
            self._jump_timer=0.0
            if self.is_on_ground: self.vy=self.properties.get('jump_force',-400); self.is_on_ground=False

    def draw(self, painter, animation_timer=0.0):
        model = self.properties.get('model','skeleton')
        anim = self.properties.get('animation','idle')
        t = animation_timer
        painter.save()
        cx = self.x+self.width/2; cy = self.y+self.height/2
        painter.translate(cx, cy)
        if self.direction<0: painter.scale(-1,1)
        painter.translate(-cx, -cy)

        if model == 'skeleton':
            if anim == 'idle':
                painter.setBrush(QBrush(self.color.darker(150)))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawEllipse(int(self.x+10), int(self.y), 20, 20)
                painter.drawLine(int(self.x+20), int(self.y+20), int(self.x+20), int(self.y+35))
                painter.drawLine(int(self.x+5), int(self.y+25), int(self.x+35), int(self.y+25))
            elif anim == 'walk':
                leg = int(2*math.sin(t*10))
                painter.setBrush(QBrush(self.color.darker(150)))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawEllipse(int(self.x+10), int(self.y), 20, 20)
                painter.drawLine(int(self.x+20), int(self.y+20), int(self.x+20+leg), int(self.y+35))
                painter.drawLine(int(self.x+5), int(self.y+25), int(self.x+35), int(self.y+25))
            elif anim == 'attack':
                painter.setBrush(QBrush(self.color.darker(150)))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawEllipse(int(self.x+10), int(self.y), 20, 20)
                painter.drawLine(int(self.x+20), int(self.y+20), int(self.x+20), int(self.y+35))
                painter.drawLine(int(self.x+5), int(self.y+25), int(self.x+35), int(self.y+25))
                painter.drawLine(int(self.x+5), int(self.y+25), int(self.x-5), int(self.y+15))

        elif model == 'slime':
            if anim == 'idle':
                painter.setBrush(QBrush(QColor(180,0,0)))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawEllipse(int(self.x+2), int(self.y+8), self.width-4, self.height-8)
                painter.drawEllipse(int(self.x+5), int(self.y), self.width-10, 20)
                painter.setBrush(QBrush(Qt.GlobalColor.white))
                painter.drawEllipse(int(self.x+10), int(self.y+10), 6,6)
                painter.drawEllipse(int(self.x+24), int(self.y+10), 6,6)
            elif anim == 'walk':
                stretch = 3*math.sin(t*8)
                painter.setBrush(QBrush(QColor(180,0,0)))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawEllipse(int(self.x+2), int(self.y+8), int(self.width-4+stretch), self.height-8)
                painter.drawEllipse(int(self.x+5), int(self.y), self.width-10, 20)
                painter.setBrush(QBrush(Qt.GlobalColor.white))
                painter.drawEllipse(int(self.x+10), int(self.y+10), 6,6)
                painter.drawEllipse(int(self.x+24), int(self.y+10), 6,6)
            elif anim == 'attack':
                painter.setBrush(QBrush(QColor(180,0,0)))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawEllipse(int(self.x+2), int(self.y+8), self.width-4, self.height-8)
                painter.drawEllipse(int(self.x+5), int(self.y), self.width-10, 20)
                painter.drawRect(int(self.x+5), int(self.y-5), 5, 8)
                painter.drawRect(int(self.x+self.width-10), int(self.y-5), 5, 8)
                painter.setBrush(QBrush(Qt.GlobalColor.white))
                painter.drawEllipse(int(self.x+10), int(self.y+10), 6,6)
                painter.drawEllipse(int(self.x+24), int(self.y+10), 6,6)

        elif model == 'bat':
            if anim == 'idle':
                painter.setBrush(QBrush(QColor(80,80,80)))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawEllipse(int(self.x+10), int(self.y+5), 20, 20)
                painter.drawLine(int(self.x+10), int(self.y+15), int(self.x-5), int(self.y+5))
                painter.drawLine(int(self.x+30), int(self.y+15), int(self.x+35), int(self.y+5))
                painter.setBrush(QBrush(Qt.GlobalColor.red))
                painter.drawEllipse(int(self.x+13), int(self.y+10), 4,4)
                painter.drawEllipse(int(self.x+23), int(self.y+10), 4,4)
            elif anim == 'walk':
                flap = 5*math.sin(t*15)
                painter.setBrush(QBrush(QColor(80,80,80)))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawEllipse(int(self.x+10), int(self.y+5), 20, 20)
                painter.drawLine(int(self.x+10), int(self.y+15), int(self.x-5+flap), int(self.y+5))
                painter.drawLine(int(self.x+30), int(self.y+15), int(self.x+35-flap), int(self.y+5))
                painter.setBrush(QBrush(Qt.GlobalColor.red))
                painter.drawEllipse(int(self.x+13), int(self.y+10), 4,4)
                painter.drawEllipse(int(self.x+23), int(self.y+10), 4,4)
            elif anim == 'attack':
                painter.setBrush(QBrush(QColor(80,80,80)))
                painter.setPen(QPen(Qt.GlobalColor.black,2))
                painter.drawEllipse(int(self.x+10), int(self.y+5), 20, 20)
                painter.drawLine(int(self.x+10), int(self.y+15), int(self.x-10), int(self.y))
                painter.drawLine(int(self.x+30), int(self.y+15), int(self.x+40), int(self.y))
                painter.setBrush(QBrush(Qt.GlobalColor.red))
                painter.drawEllipse(int(self.x+13), int(self.y+10), 4,4)
                painter.drawEllipse(int(self.x+23), int(self.y+10), 4,4)

        painter.restore()

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'],data['y'],data.get('width',40),data.get('height',40))
        obj.color = QColor(data.get('color','#FF3232')); obj.tag='enemy'
        obj.is_static=data.get('is_static',False); obj.has_gravity=data.get('has_gravity',True)
        props = data.get('properties',{}); obj.properties.update(props)
        obj.start_x=data['x']; obj.start_y=data['y']
        obj.properties.setdefault('model','skeleton'); obj.properties.setdefault('animation','idle')
        return obj

# ---------- Platform ----------
class Platform(GameObject):
    def __init__(self, x=0, y=0, width=200, height=30):
        super().__init__(x,y,width,height); self.color=QColor(100,100,100); self.tag="platform"
        self.is_static=True; self.has_gravity=False; self.properties={'type':'solid'}
    def draw(self, painter, animation_timer=0.0):
        painter.setBrush(QBrush(self.color)); painter.setPen(QPen(Qt.GlobalColor.black,2))
        painter.drawRect(int(self.x),int(self.y),int(self.width),int(self.height))
        painter.setPen(QPen(QColor(80,80,80),1))
        for i in range(int(self.x+20), int(self.x+self.width), 40):
            painter.drawLine(i, int(self.y+5), i, int(self.y+self.height-5))
        painter.setPen(QPen(QColor(150,150,150),2))
        painter.drawLine(int(self.x),int(self.y),int(self.x+self.width),int(self.y))
    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'],data['y'],data.get('width',200),data.get('height',30))
        obj.color = QColor(data.get('color','#646464')); obj.tag='platform'
        obj.is_static=True; obj.has_gravity=False
        obj.properties.update(data.get('properties',{})); return obj

# ---------- Collectible ----------
class Collectible(GameObject):
    def __init__(self, x=0, y=0, width=25, height=25):
        super().__init__(x,y,width,height); self.color=QColor(255,215,0); self.tag="collectible"
        self.collected=False; self.is_static=True; self.has_gravity=False
        self.properties={'type':'coin','value':10,'model':'coin','anim_style':'float'}

    def draw(self, painter, animation_timer=0.0):
        if self.collected: return
        model = self.properties.get('model','coin')
        style = self.properties.get('anim_style','float')
        t = animation_timer
        offset_y = 0; scale = 1.0; angle = 0.0
        if style == 'float': offset_y = math.sin(t * 3.0) * 5
        elif style == 'pulse': scale = 1.0 + 0.2 * math.sin(t * 5.0)
        elif style == 'rotate': angle = t * 200

        painter.save()
        cx = self.x + self.width/2; cy = self.y + self.height/2 + offset_y
        painter.translate(cx, cy)
        if scale != 1.0: painter.scale(scale, scale)
        if angle != 0: painter.rotate(angle)
        painter.translate(-cx, -cy)

        if model == 'coin':
            painter.setBrush(QBrush(QColor(255,215,0))); painter.setPen(QPen(Qt.GlobalColor.darkYellow,2))
            painter.drawEllipse(int(self.x), int(self.y+offset_y), int(self.width), int(self.height))
            painter.setPen(QPen(Qt.GlobalColor.black))
            f=QFont(); f.setBold(True); f.setPointSize(10); painter.setFont(f)
            painter.drawText(QRectF(self.x, self.y+offset_y, self.width, self.height), Qt.AlignmentFlag.AlignCenter, "$")
        elif model == 'gem':
            painter.setBrush(QBrush(QColor(100,200,255))); painter.setPen(QPen(Qt.GlobalColor.blue,2))
            diamond = QPolygonF()
            diamond.append(QPointF(self.x+self.width/2, self.y+offset_y))
            diamond.append(QPointF(self.x+self.width, self.y+self.height/2+offset_y))
            diamond.append(QPointF(self.x+self.width/2, self.y+self.height+offset_y))
            diamond.append(QPointF(self.x, self.y+self.height/2+offset_y))
            painter.drawPolygon(diamond)
            painter.setPen(QPen(Qt.GlobalColor.white))
            f=QFont(); f.setBold(True); painter.setFont(f)
            painter.drawText(QRectF(self.x, self.y+offset_y, self.width, self.height), Qt.AlignmentFlag.AlignCenter, "♦")
        elif model == 'star':
            painter.setBrush(QBrush(QColor(255,200,0))); painter.setPen(QPen(Qt.GlobalColor.red,2))
            star = QPainterPath()
            pts = []
            for i in range(5):
                angle_outer = -math.pi/2 + i*2*math.pi/5
                angle_inner = angle_outer + math.pi/5
                pts.append((cx + math.cos(angle_outer)*self.width/2,
                            cy + math.sin(angle_outer)*self.height/2 + offset_y))
                pts.append((cx + math.cos(angle_inner)*self.width/4,
                            cy + math.sin(angle_inner)*self.height/4 + offset_y))
            star.moveTo(pts[0][0], pts[0][1])
            for p in pts[1:]: star.lineTo(p[0], p[1])
            star.closeSubpath()
            painter.drawPath(star)
            painter.setPen(QPen(Qt.GlobalColor.white))
            f=QFont(); f.setBold(True); painter.setFont(f)
            painter.drawText(QRectF(self.x, self.y+offset_y, self.width, self.height), Qt.AlignmentFlag.AlignCenter, "★")
        painter.restore()

    def get_rect(self):
        # بزرگ‌تر کردن ناحیه برای انتخاب راحت‌تر در ادیتور
        return QRectF(self.x-5, self.y-5, self.width+10, self.height+10)

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'],data['y'],data.get('width',25),data.get('height',25))
        obj.color = QColor(data.get('color','#FFD700')); obj.tag='collectible'
        obj.is_static=True; obj.has_gravity=False
        props = data.get('properties',{}); obj.properties.update(props)
        obj.properties.setdefault('model','coin'); obj.properties.setdefault('anim_style','float')
        return obj

# ---------- SpawnPoint ----------
class SpawnPoint(GameObject):
    def __init__(self, x=0, y=0, width=40, height=60):
        super().__init__(x,y,width,height); self.color=QColor(0,255,0,100); self.tag="spawn"
        self.is_static=True; self.has_gravity=False
    def draw(self, painter, animation_timer=0.0):
        painter.setBrush(QBrush(self.color)); painter.setPen(QPen(Qt.GlobalColor.green,2,Qt.PenStyle.DashLine))
        painter.drawRect(int(self.x),int(self.y),int(self.width),int(self.height))
        painter.setPen(QPen(Qt.GlobalColor.white)); f=QFont(); f.setBold(True); painter.setFont(f)
        painter.drawText(QRectF(self.x,self.y,self.width,self.height),Qt.AlignmentFlag.AlignCenter,"START")
    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'],data['y'],data.get('width',40),data.get('height',60))
        obj.color = QColor(data.get('color','#00FF00')); obj.tag='spawn'; obj.is_static=True; obj.has_gravity=False
        obj.properties.update(data.get('properties',{})); return obj

# ---------- GameEngine ----------
class GameEngine:
    def __init__(self, width=800, height=600, template="platformer"):
        self.width, self.height, self.template = width, height, template
        self.game_objects=[]; self.score=0; self.game_over=False; self.game_won=False; self.player=None
        self.background_color=QColor(240,240,240)
        self.game_config={'gravity':980,'game_speed':1.0,'win_condition':'collect_all','lose_condition':'health_zero',
                         'time_limit':0,'particles_enabled':True,'particle_style':'default','collectible_animation':'float'}
        self.key_bindings={'move_left':[Qt.Key.Key_A,Qt.Key.Key_Left],'move_right':[Qt.Key.Key_D,Qt.Key.Key_Right],
                           'jump':[Qt.Key.Key_Space,Qt.Key.Key_W,Qt.Key.Key_Up],'sprint':[Qt.Key.Key_Shift],
                           'pause':[Qt.Key.Key_Escape],'restart':[Qt.Key.Key_R]}
        self.camera_x=0; self.camera_y=0; self.camera_follow_player=(template=="platformer")
        self.particle_system=ParticleSystem(); self.particles_enabled=True; self.animation_timer=0.0

    def add_object(self, obj):
        self.game_objects.append(obj)
        if obj.tag=="player": self.player=obj
    def remove_object(self, obj):
        if obj in self.game_objects: self.game_objects.remove(obj)
        if obj==self.player: self.player=None

    def update(self, dt):
        if not self.particles_enabled: self.particle_system.clear()
        else: self.particle_system.update(dt)
        self.animation_timer += dt
        if self.game_over or self.game_won: return
        g = self.game_config.get('gravity',0) if self.template=="platformer" else 0
        for obj in self.game_objects:
            if hasattr(obj,'is_on_ground'): obj.is_on_ground=False
        for obj in self.game_objects:
            if obj.active:
                if obj.tag=="enemy": obj.update(dt, g, self.player)
                else: obj.update(dt, g)
        if self.template=="platformer": self._phys()
        else: self._simple_col()
        self._cam(); self._win(); self._lose()

    def _emit(self, x, y, count, color, style=None):
        if not self.particles_enabled: return
        st = style or self.game_config.get('particle_style','default')
        if st=='sparkle': self.particle_system.emit(x,y,count*2,color,(100,300),(0.2,0.5),(1,3))
        elif st=='smoke': self.particle_system.emit(x,y,count//2,color.darker(150),(30,80),(1.0,2.0),(6,12))
        else: self.particle_system.emit(x,y,count,color,(60,200),(0.4,1.0),(3,7))

    def _phys(self):
        for obj in self.game_objects:
            if obj.is_static or not obj.active: continue
            for plat in self.game_objects:
                if plat.tag=="platform" and plat.active: self._res(obj,plat)
        if self.player and self.player.active:
            for en in self.game_objects:
                if en.tag=="enemy" and en.active and self.player.check_collision(en):
                    if self.player.vy>0 and (self.player.y+self.player.height-en.y)<15:
                        en.active=False
                        self._emit(en.x+en.width/2, en.y+en.height/2, 20, QColor(255,100,0))
                        self.player.vy = self.player.properties.get('jump_force',-500)*0.6; self.score+=50
                    else:
                        self.player.properties['health'] -= en.properties.get('damage',20)
                        self.player.vx = -300 if self.player.x<en.x else 300
            for it in self.game_objects:
                if it.tag=="collectible" and not it.collected and self.player.check_collision(it):
                    col = QColor(255,215,0)
                    if it.properties.get('type')=='health': col=QColor(255,100,100)
                    elif it.properties.get('type')=='powerup': col=QColor(0,255,100)
                    self._emit(it.x+it.width/2, it.y+it.height/2, 15, col)
                    self._collect(it)
            if self.player.properties.get('health',0)<=0 and not self.game_over:
                self._emit(self.player.x+self.player.width/2, self.player.y+self.player.height/2, 30, QColor(0,100,255))
                self.game_over=True

    def _res(self, obj, plat):
        if not obj.check_collision(plat): return
        r1,r2=obj.get_rect(),plat.get_rect()
        ol=r1.right()-r2.left(); or_=r2.right()-r1.left(); ot=r1.bottom()-r2.top(); ob=r2.bottom()-r1.top()
        m=min(ol,or_,ot,ob)
        if m==ot and obj.vy>=0:
            obj.y=plat.y-obj.height; obj.vy=0
            if hasattr(obj,'is_on_ground'): obj.is_on_ground=True
            if obj.tag=="player": obj.properties['current_jumps']=0
        elif m==ob and obj.vy<0: obj.y=plat.y+plat.height; obj.vy=0
        elif m==ol: obj.x=plat.x-obj.width; obj.vx=min(0,obj.vx)
        elif m==or_: obj.x=plat.x+plat.width; obj.vx=max(0,obj.vx)

    def _collect(self, it):
        t=it.properties.get('type','coin'); v=it.properties.get('value',10)
        if t=='coin': self.score+=v
        elif t=='health' and self.player: self.player.properties['health']=min(self.player.properties['health']+v, self.player.properties['max_health'])
        it.collected=True; it.active=False

    def _simple_col(self):
        if not self.player: return
        for obj in self.game_objects:
            if obj.tag=="enemy" and obj.active and self.player.check_collision(obj): self.game_over=True
            elif obj.tag=="collectible" and not obj.collected and self.player.check_collision(obj): self._collect(obj)

    def _cam(self):
        if self.camera_follow_player and self.player:
            tx=self.player.x - self.width/2 + self.player.width/2; ty=self.player.y - self.height/2 + self.player.height/2
            self.camera_x=max(0,min(tx,2000-self.width)); self.camera_y=max(0,min(ty,2000-self.height))

    def _win(self):
        if self.game_config.get('win_condition')=='collect_all':
            coll=[o for o in self.game_objects if o.tag=="collectible"]
            if coll and all(c.collected for c in coll): self.game_won=True

    def _lose(self):
        if self.game_config.get('lose_condition')=='health_zero' and self.player and self.player.properties['health']<=0: pass
        elif self.game_config.get('lose_condition')=='fall_out' and self.player and self.player.y>self.height+100: self.game_over=True

    def move_player(self, d, action='walk'):
        if not self.player: return
        sp=self.player.properties.get('walk_speed',200) if action=='walk' else self.player.properties.get('run_speed',400)
        self.player.vx=d*sp; self.player.facing_right=d>0

    def jump_player(self):
        if not self.player: return
        if self.player.properties.get('current_jumps',0)<self.player.properties.get('max_jumps',1):
            self.player.vy=self.player.properties.get('jump_force',-500); self.player.properties['current_jumps']+=1
            self.player.is_on_ground=False

    def reset(self):
        self.game_objects.clear(); self.score=0; self.game_over=False; self.game_won=False; self.player=None
        self.particle_system.clear(); self.animation_timer=0.0

    def to_dict(self):
        return {'width':self.width,'height':self.height,'template':self.template,'background_color':self.background_color.name(),
                'game_config':self.game_config,'key_bindings':{k:[int(x) for x in v] for k,v in self.key_bindings.items()},
                'objects':[o.to_dict() for o in self.game_objects]}

    def from_dict(self, data):
        self.reset()
        self.width=data.get('width',800); self.height=data.get('height',600); self.template=data.get('template','platformer')
        self.background_color=QColor(data.get('background_color','#F0F0F0'))
        self.game_config=data.get('game_config',self.game_config)
        self.particles_enabled=self.game_config.get('particles_enabled',True)
        kb=data.get('key_bindings',None)
        if kb: self.key_bindings={k:[Qt.Key(x) for x in v] for k,v in kb.items()}
        for od in data.get('objects',[]):
            t=od['type']
            if t=='Player': o=Player.from_dict(od)
            elif t=='Enemy': o=Enemy.from_dict(od)
            elif t=='Platform': o=Platform.from_dict(od)
            elif t=='Collectible': o=Collectible.from_dict(od)
            elif t=='SpawnPoint': o=SpawnPoint.from_dict(od)
            else: continue
            self.add_object(o)