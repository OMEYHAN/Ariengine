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
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        color = QColor(self.color.red(), self.color.green(), self.color.blue(), alpha)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(self.x, self.y), self.size, self.size)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=10, color=QColor(255,255,255),
             speed_range=(50,200), life_range=(0.5,1.5), size_range=(2,6)):
        for _ in range(count):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(*speed_range)
            vx = speed * random.choice([-1,1]) * random.uniform(0.3, 1.0)
            vy = -speed * random.uniform(0.5, 1.0)
            life = random.uniform(*life_range)
            size = random.uniform(*size_range)
            self.particles.append(Particle(x, y, vx, vy, life, color, size))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, painter):
        for p in self.particles:
            p.draw(painter)

    def clear(self):
        self.particles.clear()


# ---------- Base GameObject ----------
class GameObject:
    def __init__(self, x=0, y=0, width=50, height=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.color = QColor(255, 0, 0)
        self.active = True
        self.tag = ""
        self.properties = {}
        self.is_static = False
        self.has_gravity = True

    def update(self, dt, gravity=0):
        if not self.is_static:
            self.x += self.vx * dt
            if self.has_gravity and gravity:
                self.vy += gravity * dt
            self.y += self.vy * dt

    def draw(self, painter, animation_timer=0.0):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

    def get_rect(self):
        return QRectF(self.x, self.y, self.width, self.height)

    def check_collision(self, other):
        return self.get_rect().intersects(other.get_rect())

    def to_dict(self):
        return {
            'type': self.__class__.__name__,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'color': self.color.name(),
            'tag': self.tag,
            'is_static': self.is_static,
            'has_gravity': self.has_gravity,
            'properties': self.properties
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'], data['y'], data['width'], data['height'])
        obj.color = QColor(data['color'])
        obj.tag = data['tag']
        obj.is_static = data.get('is_static', False)
        obj.has_gravity = data.get('has_gravity', True)
        obj.properties = data.get('properties', {})
        return obj


# ---------- Player ----------
class Player(GameObject):
    def __init__(self, x=0, y=0, width=40, height=60):
        super().__init__(x, y, width, height)
        self.color = QColor(0, 100, 255)
        self.tag = "player"
        self.is_static = False
        self.has_gravity = True
        self.properties = {
            'walk_speed': 200,
            'run_speed': 400,
            'jump_force': -500,
            'max_jumps': 2,
            'current_jumps': 0,
            'health': 100,
            'max_health': 100,
            'can_sprint': True,
            'can_jump': True,
            'model': 'classic'
        }
        self.is_on_ground = False
        self.facing_right = True
        self.speed = 200

    def draw(self, painter, animation_timer=0.0):
        model = self.properties.get('model', 'classic')
        painter.save()
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        painter.translate(cx, cy)
        if not self.facing_right:
            painter.scale(-1, 1)
        painter.translate(-cx, -cy)

        if model == 'classic':
            painter.setBrush(QBrush(self.color))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(self.x + self.width - 15), int(self.y + 10), 8, 8)

        elif model == 'slime':
            path = QPainterPath()
            path.addEllipse(QRectF(self.x + 2, self.y + 8, self.width - 4, self.height - 8))
            path.addEllipse(QRectF(self.x + 5, self.y, self.width - 10, 20))
            painter.setBrush(QBrush(self.color))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawPath(path)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(self.x + self.width - 12), int(self.y + 12), 6, 6)

        elif model == 'robot':
            painter.setBrush(QBrush(self.color))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawRect(int(self.x + 5), int(self.y), int(self.width - 10), int(self.height))
            painter.drawRect(int(self.x), int(self.y + 10), 5, 10)
            painter.drawRect(int(self.x + self.width - 5), int(self.y + 10), 5, 10)
            painter.drawRect(int(self.x + 10), int(self.y - 6), 6, 6)
            painter.drawLine(int(self.x + 10), int(self.y - 10), int(self.x + 13), int(self.y - 15))
            painter.drawLine(int(self.x + 20), int(self.y - 10), int(self.x + 17), int(self.y - 15))
            painter.setBrush(QBrush(QColor(255, 255, 0)))
            painter.drawEllipse(int(self.x + self.width - 12), int(self.y + 12), 5, 5)

        painter.restore()

        health = self.properties.get('health', 100)
        max_health = self.properties.get('max_health', 100)
        if health < max_health:
            bar_width = self.width
            bar_height = 5
            bar_y = self.y - 10
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.drawRect(int(self.x), int(bar_y), int(bar_width), bar_height)
            painter.setBrush(QBrush(QColor(0, 255, 0)))
            painter.drawRect(int(self.x), int(bar_y), int(bar_width * health // max_health), bar_height)

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'], data['y'], data.get('width', 40), data.get('height', 60))
        obj.color = QColor(data.get('color', '#0064FF'))
        obj.tag = 'player'
        obj.is_static = data.get('is_static', False)
        obj.has_gravity = data.get('has_gravity', True)
        props = data.get('properties', {})
        if props:
            obj.properties.update(props)
        obj.speed = obj.properties.get('walk_speed', 200)
        obj.properties.setdefault('model', 'classic')
        return obj


# ---------- Enemy ----------
class Enemy(GameObject):
    def __init__(self, x=0, y=0, width=40, height=40):
        super().__init__(x, y, width, height)
        self.color = QColor(255, 50, 50)
        self.tag = "enemy"
        self.has_gravity = True
        self.properties = {
            'patrol_range': 100,
            'speed': 100,
            'damage': 20,
            'patrol_type': 'horizontal',
            'ai_type': 'patrol',
            'detection_range': 200,
            'chase_speed': 150,
            'jump_force': -400,
            'jump_interval': 1.5,
            'model': 'beast'
        }
        self.start_x = x
        self.start_y = y
        self.direction = 1
        self.is_on_ground = False
        self._jump_timer = 0.0

    def update(self, dt, gravity=0, player=None):
        ai = self.properties.get('ai_type', 'patrol')
        speed = self.properties.get('speed', 100)
        patrol_range = self.properties.get('patrol_range', 100)
        detection_range = self.properties.get('detection_range', 200)
        chase_speed = self.properties.get('chase_speed', 150)

        if ai == 'patrol':
            self._patrol(dt, speed, patrol_range)
        elif ai == 'chase':
            self._chase(dt, speed, patrol_range, chase_speed, detection_range, player)
        elif ai == 'static':
            pass
        elif ai == 'jumper':
            self._jumper(dt, gravity)

        if self.has_gravity and gravity:
            self.vy += gravity * dt
            self.y += self.vy * dt

    def _patrol(self, dt, speed, patrol_range):
        patrol_type = self.properties.get('patrol_type', 'horizontal')
        if patrol_type == 'horizontal':
            self.x += self.direction * speed * dt
            if self.x > self.start_x + patrol_range:
                self.direction = -1
            elif self.x < self.start_x - patrol_range:
                self.direction = 1
        else:
            self.y += self.direction * speed * dt
            if self.y > self.start_y + patrol_range:
                self.direction = -1
            elif self.y < self.start_y - patrol_range:
                self.direction = 1

    def _chase(self, dt, patrol_speed, patrol_range, chase_speed, detection_range, player):
        if player is None:
            self._patrol(dt, patrol_speed, patrol_range)
            return
        dx = player.x - self.x
        dy = player.y - self.y
        if abs(dx) < detection_range and abs(dy) < 150:
            self.direction = 1 if dx > 0 else -1
            self.x += self.direction * chase_speed * dt
        else:
            self._patrol(dt, patrol_speed, patrol_range)

    def _jumper(self, dt, gravity):
        self._jump_timer += dt
        if self._jump_timer >= self.properties.get('jump_interval', 1.5):
            self._jump_timer = 0.0
            if self.is_on_ground:
                self.vy = self.properties.get('jump_force', -400)
                self.is_on_ground = False

    def draw(self, painter, animation_timer=0.0):
        model = self.properties.get('model', 'beast')
        painter.save()
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        painter.translate(cx, cy)
        if self.direction < 0:
            painter.scale(-1, 1)
        painter.translate(-cx, -cy)

        if model == 'beast':
            painter.setBrush(QBrush(self.color))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(self.x + self.width - 12), int(self.y + 8), 6, 6)

        elif model == 'spike':
            path = QPainterPath()
            r = min(self.width, self.height) / 2
            path.addEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
            for i in range(6):
                angle = i * 3.14159 * 2 / 6
                px = cx + math.cos(angle) * (r + 5)
                py = cy + math.sin(angle) * (r + 5)
                path.moveTo(px, py)
                path.lineTo(cx + math.cos(angle + 0.2) * (r + 12),
                            cy + math.sin(angle + 0.2) * (r + 12))
                path.lineTo(cx + math.cos(angle - 0.2) * (r + 12),
                            cy + math.sin(angle - 0.2) * (r + 12))
                path.closeSubpath()
            painter.setBrush(QBrush(self.color))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawPath(path)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(cx - 3), int(cy - 3), 6, 6)

        elif model == 'ghost':
            painter.setBrush(QBrush(self.color.lighter(120)))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawEllipse(int(self.x + 5), int(self.y), int(self.width - 10), int(self.height - 8))
            painter.drawRect(int(self.x + 5), int(self.y + self.height / 2),
                             int(self.width - 10), int(self.height / 2 - 4))
            painter.setBrush(QBrush(Qt.GlobalColor.white))
            painter.drawEllipse(int(self.x + 10), int(self.y + 10), 6, 6)
            painter.drawEllipse(int(self.x + self.width - 16), int(self.y + 10), 6, 6)
            painter.setBrush(QBrush(Qt.GlobalColor.black))
            painter.drawEllipse(int(self.x + 12), int(self.y + 12), 3, 3)
            painter.drawEllipse(int(self.x + self.width - 14), int(self.y + 12), 3, 3)

        painter.restore()

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'], data['y'], data.get('width', 40), data.get('height', 40))
        obj.color = QColor(data.get('color', '#FF3232'))
        obj.tag = 'enemy'
        obj.is_static = data.get('is_static', False)
        obj.has_gravity = data.get('has_gravity', True)
        props = data.get('properties', {})
        if props:
            obj.properties.update(props)
        obj.start_x = data['x']
        obj.start_y = data['y']
        obj.properties.setdefault('model', 'beast')
        return obj


# ---------- Platform ----------
class Platform(GameObject):
    def __init__(self, x=0, y=0, width=200, height=30):
        super().__init__(x, y, width, height)
        self.color = QColor(100, 100, 100)
        self.tag = "platform"
        self.is_static = True
        self.has_gravity = False
        self.properties = {'type': 'solid'}

    def draw(self, painter, animation_timer=0.0):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        for i in range(int(self.x + 20), int(self.x + self.width), 40):
            painter.drawLine(i, int(self.y + 5), i, int(self.y + self.height - 5))
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.drawLine(int(self.x), int(self.y), int(self.x + self.width), int(self.y))

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'], data['y'], data.get('width', 200), data.get('height', 30))
        obj.color = QColor(data.get('color', '#646464'))
        obj.tag = 'platform'
        obj.is_static = True
        obj.has_gravity = False
        props = data.get('properties', {})
        if props:
            obj.properties.update(props)
        return obj


# ---------- Collectible ----------
class Collectible(GameObject):
    def __init__(self, x=0, y=0, width=25, height=25):
        super().__init__(x, y, width, height)
        self.color = QColor(255, 215, 0)
        self.tag = "collectible"
        self.collected = False
        self.is_static = True
        self.has_gravity = False
        self.properties = {'type': 'coin', 'value': 10, 'model': 'coin'}

    def draw(self, painter, animation_timer=0.0, animation_style='float'):
        if self.collected:
            return
        model = self.properties.get('model', 'coin')
        offset_y = 0
        scale = 1.0
        angle = 0.0
        if animation_style == 'float':
            offset_y = math.sin(animation_timer * 3.0) * 5
        elif animation_style == 'pulse':
            scale = 1.0 + 0.2 * math.sin(animation_timer * 5.0)
        elif animation_style == 'rotate':
            angle = animation_timer * 200

        painter.save()
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2 + offset_y
        painter.translate(cx, cy)
        if scale != 1.0:
            painter.scale(scale, scale)
        if angle != 0:
            painter.rotate(angle)
        painter.translate(-cx, -cy)

        if model == 'coin':
            painter.setBrush(QBrush(QColor(255, 215, 0)))
            painter.setPen(QPen(Qt.GlobalColor.darkYellow, 2))
            painter.drawEllipse(int(self.x), int(self.y + offset_y), int(self.width), int(self.height))
            painter.setPen(QPen(Qt.GlobalColor.black))
            font = QFont()
            font.setBold(True)
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(QRectF(self.x, self.y + offset_y, self.width, self.height),
                             Qt.AlignmentFlag.AlignCenter, "$")

        elif model == 'gem':
            painter.setBrush(QBrush(QColor(100, 200, 255)))
            painter.setPen(QPen(Qt.GlobalColor.blue, 2))
            diamond = QPolygonF()
            diamond.append(QPointF(self.x + self.width / 2, self.y + offset_y))
            diamond.append(QPointF(self.x + self.width, self.y + self.height / 2 + offset_y))
            diamond.append(QPointF(self.x + self.width / 2, self.y + self.height + offset_y))
            diamond.append(QPointF(self.x, self.y + self.height / 2 + offset_y))
            painter.drawPolygon(diamond)
            painter.setPen(QPen(Qt.GlobalColor.white))
            font = QFont()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QRectF(self.x, self.y + offset_y, self.width, self.height),
                             Qt.AlignmentFlag.AlignCenter, "♦")

        elif model == 'star':
            painter.setBrush(QBrush(QColor(255, 200, 0)))
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
            star = QPainterPath()
            pts = []
            for i in range(5):
                angle_outer = -math.pi / 2 + i * 2 * math.pi / 5
                angle_inner = angle_outer + math.pi / 5
                pts.append((cx + math.cos(angle_outer) * self.width / 2,
                            cy + math.sin(angle_outer) * self.height / 2 + offset_y))
                pts.append((cx + math.cos(angle_inner) * self.width / 4,
                            cy + math.sin(angle_inner) * self.height / 4 + offset_y))
            star.moveTo(pts[0][0], pts[0][1])
            for p in pts[1:]:
                star.lineTo(p[0], p[1])
            star.closeSubpath()
            painter.drawPath(star)
            painter.setPen(QPen(Qt.GlobalColor.white))
            font = QFont()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QRectF(self.x, self.y + offset_y, self.width, self.height),
                             Qt.AlignmentFlag.AlignCenter, "★")

        painter.restore()

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'], data['y'], data.get('width', 25), data.get('height', 25))
        obj.color = QColor(data.get('color', '#FFD700'))
        obj.tag = 'collectible'
        obj.is_static = True
        obj.has_gravity = False
        props = data.get('properties', {})
        if props:
            obj.properties.update(props)
        obj.properties.setdefault('model', 'coin')
        return obj


# ---------- SpawnPoint ----------
class SpawnPoint(GameObject):
    def __init__(self, x=0, y=0, width=40, height=60):
        super().__init__(x, y, width, height)
        self.color = QColor(0, 255, 0, 100)
        self.tag = "spawn"
        self.is_static = True
        self.has_gravity = False

    def draw(self, painter, animation_timer=0.0):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.GlobalColor.green, 2, Qt.PenStyle.DashLine))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(self.x, self.y, self.width, self.height),
                         Qt.AlignmentFlag.AlignCenter, "START")

    @classmethod
    def from_dict(cls, data):
        obj = cls(data['x'], data['y'], data.get('width', 40), data.get('height', 60))
        obj.color = QColor(data.get('color', '#00FF00'))
        obj.tag = 'spawn'
        obj.is_static = True
        obj.has_gravity = False
        props = data.get('properties', {})
        if props:
            obj.properties.update(props)
        return obj


# ---------- GameEngine ----------
class GameEngine:
    def __init__(self, width=800, height=600, template="platformer"):
        self.width = width
        self.height = height
        self.template = template
        self.game_objects = []
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.player = None
        self.background_color = QColor(240, 240, 240)
        self.game_config = {
            'gravity': 980,
            'game_speed': 1.0,
            'win_condition': 'collect_all',
            'lose_condition': 'health_zero',
            'time_limit': 0,
            'particles_enabled': True,
            'particle_style': 'default',
            'collectible_animation': 'float'
        }
        self.key_bindings = {
            'move_left': [Qt.Key.Key_A, Qt.Key.Key_Left],
            'move_right': [Qt.Key.Key_D, Qt.Key.Key_Right],
            'jump': [Qt.Key.Key_Space, Qt.Key.Key_W, Qt.Key.Key_Up],
            'sprint': [Qt.Key.Key_Shift],
            'pause': [Qt.Key.Key_Escape],
            'restart': [Qt.Key.Key_R]
        }
        self.camera_x = 0
        self.camera_y = 0
        self.camera_follow_player = (template == "platformer")
        self.particle_system = ParticleSystem()
        self.particles_enabled = True
        self.animation_timer = 0.0

    def add_object(self, obj):
        self.game_objects.append(obj)
        if obj.tag == "player":
            self.player = obj

    def remove_object(self, obj):
        if obj in self.game_objects:
            self.game_objects.remove(obj)
            if obj == self.player:
                self.player = None

    def update(self, dt):
        if not self.particles_enabled:
            self.particle_system.clear()
        else:
            self.particle_system.update(dt)

        self.animation_timer += dt

        if self.game_over or self.game_won:
            return

        gravity = self.game_config.get('gravity', 0) if self.template == "platformer" else 0

        for obj in self.game_objects:
            if hasattr(obj, 'is_on_ground'):
                obj.is_on_ground = False

        for obj in self.game_objects:
            if obj.active:
                if obj.tag == "enemy":
                    obj.update(dt, gravity, self.player)
                else:
                    obj.update(dt, gravity)

        if self.template == "platformer":
            self._platformer_physics()
        else:
            self._simple_collisions()

        self._update_camera()
        self._check_win_condition()
        self._check_lose_condition()

    def _emit_particles(self, x, y, count, base_color, style=None):
        if not self.particles_enabled:
            return
        if style is None:
            style = self.game_config.get('particle_style', 'default')

        if style == 'sparkle':
            self.particle_system.emit(x, y, count=count * 2, color=base_color,
                                      speed_range=(100, 300), life_range=(0.2, 0.5), size_range=(1, 3))
        elif style == 'smoke':
            dark_color = base_color.darker(150)
            self.particle_system.emit(x, y, count=count // 2, color=dark_color,
                                      speed_range=(30, 80), life_range=(1.0, 2.0), size_range=(6, 12))
        else:
            self.particle_system.emit(x, y, count=count, color=base_color,
                                      speed_range=(60, 200), life_range=(0.4, 1.0), size_range=(3, 7))

    def _platformer_physics(self):
        for obj in self.game_objects:
            if obj.is_static or not obj.active:
                continue
            for platform in self.game_objects:
                if platform.tag == "platform" and platform.active:
                    self._resolve_collision(obj, platform)

        if self.player and self.player.active:
            for enemy in self.game_objects:
                if enemy.tag == "enemy" and enemy.active and self.player.check_collision(enemy):
                    if self.player.vy > 0 and (self.player.y + self.player.height - enemy.y) < 15:
                        enemy.active = False
                        self._emit_particles(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2,
                                            count=20, base_color=QColor(255, 100, 0))
                        self.player.vy = self.player.properties.get('jump_force', -500) * 0.6
                        self.score += 50
                    else:
                        self.player.properties['health'] -= enemy.properties.get('damage', 20)
                        if self.player.x < enemy.x:
                            self.player.vx = -300
                        else:
                            self.player.vx = 300

            for item in self.game_objects:
                if item.tag == "collectible" and not item.collected and self.player.check_collision(item):
                    if item.properties.get('type') == 'health':
                        color = QColor(255, 100, 100)
                    elif item.properties.get('type') == 'powerup':
                        color = QColor(0, 255, 100)
                    else:
                        color = QColor(255, 215, 0)
                    self._emit_particles(item.x + item.width / 2, item.y + item.height / 2,
                                        count=15, base_color=color)
                    self._collect_item(item)

            if self.player.properties.get('health', 0) <= 0 and not self.game_over:
                self._emit_particles(self.player.x + self.player.width / 2,
                                    self.player.y + self.player.height / 2,
                                    count=30, base_color=QColor(0, 100, 255))
                self.game_over = True

    def _resolve_collision(self, obj, platform):
        if not obj.check_collision(platform):
            return
        obj_rect = obj.get_rect()
        plat_rect = platform.get_rect()

        overlap_left = obj_rect.right() - plat_rect.left()
        overlap_right = plat_rect.right() - obj_rect.left()
        overlap_top = obj_rect.bottom() - plat_rect.top()
        overlap_bottom = plat_rect.bottom() - obj_rect.top()

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_top and obj.vy >= 0:
            obj.y = platform.y - obj.height
            obj.vy = 0
            if hasattr(obj, 'is_on_ground'):
                obj.is_on_ground = True
            if obj.tag == "player":
                obj.properties['current_jumps'] = 0
        elif min_overlap == overlap_bottom and obj.vy < 0:
            obj.y = platform.y + platform.height
            obj.vy = 0
        elif min_overlap == overlap_left:
            obj.x = platform.x - obj.width
            obj.vx = min(0, obj.vx)
        elif min_overlap == overlap_right:
            obj.x = platform.x + platform.width
            obj.vx = max(0, obj.vx)

    def _collect_item(self, item):
        item_type = item.properties.get('type', 'coin')
        value = item.properties.get('value', 10)
        if item_type == 'coin':
            self.score += value
        elif item_type == 'health' and self.player:
            self.player.properties['health'] = min(
                self.player.properties['health'] + value,
                self.player.properties['max_health']
            )
        item.collected = True
        item.active = False

    def _simple_collisions(self):
        if not self.player:
            return
        for obj in self.game_objects:
            if obj.tag == "enemy" and obj.active and self.player.check_collision(obj):
                self.game_over = True
            elif obj.tag == "collectible" and not obj.collected and self.player.check_collision(obj):
                self._collect_item(obj)

    def _update_camera(self):
        if self.camera_follow_player and self.player:
            target_x = self.player.x - self.width / 2 + self.player.width / 2
            target_y = self.player.y - self.height / 2 + self.player.height / 2
            self.camera_x = max(0, min(target_x, 2000 - self.width))
            self.camera_y = max(0, min(target_y, 2000 - self.height))

    def _check_win_condition(self):
        if self.game_config.get('win_condition') == 'collect_all':
            collectibles = [o for o in self.game_objects if o.tag == "collectible"]
            if collectibles and all(c.collected for c in collectibles):
                self.game_won = True

    def _check_lose_condition(self):
        if self.game_config.get('lose_condition') == 'health_zero' and self.player:
            if self.player.properties['health'] <= 0:
                pass
        elif self.game_config.get('lose_condition') == 'fall_out' and self.player:
            if self.player.y > self.height + 100:
                self.game_over = True

    def move_player(self, direction, action='walk'):
        if not self.player:
            return
        speed = self.player.properties.get('walk_speed', 200)
        if action == 'run':
            speed = self.player.properties.get('run_speed', 400)
        self.player.vx = direction * speed
        self.player.facing_right = direction > 0

    def jump_player(self):
        if not self.player:
            return
        if self.player.properties.get('current_jumps', 0) < self.player.properties.get('max_jumps', 1):
            self.player.vy = self.player.properties.get('jump_force', -500)
            self.player.properties['current_jumps'] += 1
            self.player.is_on_ground = False

    def reset(self):
        self.game_objects.clear()
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.player = None
        self.particle_system.clear()
        self.animation_timer = 0.0

    def to_dict(self):
        return {
            'width': self.width,
            'height': self.height,
            'template': self.template,
            'background_color': self.background_color.name(),
            'game_config': self.game_config,
            'key_bindings': {k: [int(x) for x in v] for k, v in self.key_bindings.items()},
            'objects': [o.to_dict() for o in self.game_objects]
        }

    def from_dict(self, data):
        self.reset()
        self.width = data.get('width', 800)
        self.height = data.get('height', 600)
        self.template = data.get('template', 'platformer')
        self.background_color = QColor(data.get('background_color', '#F0F0F0'))
        self.game_config = data.get('game_config', self.game_config)
        self.particles_enabled = self.game_config.get('particles_enabled', True)

        kb = data.get('key_bindings', None)
        if kb:
            self.key_bindings = {k: [Qt.Key(x) for x in v] for k, v in kb.items()}

        for obj_data in data.get('objects', []):
            t = obj_data['type']
            if t == 'Player':
                obj = Player.from_dict(obj_data)
            elif t == 'Enemy':
                obj = Enemy.from_dict(obj_data)
            elif t == 'Platform':
                obj = Platform.from_dict(obj_data)
            elif t == 'Collectible':
                obj = Collectible.from_dict(obj_data)
            elif t == 'SpawnPoint':
                obj = SpawnPoint.from_dict(obj_data)
            else:
                continue
            self.add_object(obj)
