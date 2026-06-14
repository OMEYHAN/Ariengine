import sys, json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QSpinBox,
                             QComboBox, QColorDialog, QGroupBox, QFormLayout,
                             QListWidget, QMessageBox, QFileDialog, QDialog,
                             QDoubleSpinBox, QCheckBox, QTabWidget,
                             QScrollArea, QKeySequenceEdit, QSplitter, QFrame,
                             QToolBar)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPoint, QSize
from PyQt6.QtGui import (QPainter, QColor, QBrush, QPen, QFont,
                         QKeyEvent, QMouseEvent, QKeySequence, QWheelEvent,
                         QAction)
from engine import GameEngine, Player, Enemy, Platform, Collectible, SpawnPoint

FALLBACK_KEYS = {
    'move_left': [Qt.Key.Key_A, Qt.Key.Key_Left],
    'move_right': [Qt.Key.Key_D, Qt.Key.Key_Right],
    'jump': [Qt.Key.Key_Space, Qt.Key.Key_W, Qt.Key.Key_Up],
    'sprint': [Qt.Key.Key_Shift],
    'pause': [Qt.Key.Key_Escape],
    'restart': [Qt.Key.Key_R],
}

NATIVE_KEY_MAP = {
    0x30: Qt.Key.Key_0, 0x31: Qt.Key.Key_1, 0x32: Qt.Key.Key_2, 0x33: Qt.Key.Key_3,
    0x34: Qt.Key.Key_4, 0x35: Qt.Key.Key_5, 0x36: Qt.Key.Key_6, 0x37: Qt.Key.Key_7,
    0x38: Qt.Key.Key_8, 0x39: Qt.Key.Key_9,
    0x41: Qt.Key.Key_A, 0x42: Qt.Key.Key_B, 0x43: Qt.Key.Key_C, 0x44: Qt.Key.Key_D,
    0x45: Qt.Key.Key_E, 0x46: Qt.Key.Key_F, 0x47: Qt.Key.Key_G, 0x48: Qt.Key.Key_H,
    0x49: Qt.Key.Key_I, 0x4A: Qt.Key.Key_J, 0x4B: Qt.Key.Key_K, 0x4C: Qt.Key.Key_L,
    0x4D: Qt.Key.Key_M, 0x4E: Qt.Key.Key_N, 0x4F: Qt.Key.Key_O, 0x50: Qt.Key.Key_P,
    0x51: Qt.Key.Key_Q, 0x52: Qt.Key.Key_R, 0x53: Qt.Key.Key_S, 0x54: Qt.Key.Key_T,
    0x55: Qt.Key.Key_U, 0x56: Qt.Key.Key_V, 0x57: Qt.Key.Key_W, 0x58: Qt.Key.Key_X,
    0x59: Qt.Key.Key_Y, 0x5A: Qt.Key.Key_Z,
    0x20: Qt.Key.Key_Space,
    0x0D: Qt.Key.Key_Enter, 0x1B: Qt.Key.Key_Escape,
    0x09: Qt.Key.Key_Tab, 0x08: Qt.Key.Key_Backspace,
    0x2E: Qt.Key.Key_Delete, 0x10: Qt.Key.Key_Shift,
    0x11: Qt.Key.Key_Control, 0x12: Qt.Key.Key_Alt,
    0x25: Qt.Key.Key_Left, 0x26: Qt.Key.Key_Up,
    0x27: Qt.Key.Key_Right, 0x28: Qt.Key.Key_Down,
    0x70: Qt.Key.Key_F1, 0x71: Qt.Key.Key_F2, 0x72: Qt.Key.Key_F3,
    0x73: Qt.Key.Key_F4, 0x74: Qt.Key.Key_F5, 0x75: Qt.Key.Key_F6,
    0x77: Qt.Key.Key_F7, 0x78: Qt.Key.Key_F8, 0x79: Qt.Key.Key_F9,
    0x7A: Qt.Key.Key_F10, 0x7B: Qt.Key.Key_F11, 0x7C: Qt.Key.Key_F12,
}


class TemplateDialog(QDialog):
    # (کد شما بدون تغییر)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Game Template")
        self.setFixedSize(700, 500)
        self.selected_template = "platformer"
        layout = QVBoxLayout()
        title = QLabel("🎮 Choose Your Game Template")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin: 20px; color: #333;")
        layout.addWidget(title)
        templates_layout = QHBoxLayout()
        templates_layout.setSpacing(20)
        templates_data = [
            ("Platformer", "🎮", "#4CAF50",
             "Jump, run, collect!\nPhysics-based gameplay\n• Gravity & Jumping\n• Platforms & Enemies\n• Coins & Power-ups",
             "platformer"),
            ("RPG", "⚔️", "#2196F3",
             "Quests, items, levels!\nStory-driven gameplay\n• NPCs & Dialogues\n• Inventory System\n• Leveling Up",
             "rpg"),
            ("Simple 2D", "🕹️", "#FF9800",
             "Basic movement!\nEasy to learn\n• Free Movement\n• Simple Collisions\n• Quick Start",
             "simple")
        ]
        for name, icon, color, desc, template_id in templates_data:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ background-color: {color}; border-radius: 15px; padding: 20px; }}
                QFrame:hover {{ border: 3px solid white; }}
            """)
            card_layout = QVBoxLayout(card)
            icon_label = QLabel(icon); icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter); icon_label.setStyleSheet("font-size: 48px;")
            card_layout.addWidget(icon_label)
            name_label = QLabel(name); name_label.setAlignment(Qt.AlignmentFlag.AlignCenter); name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
            card_layout.addWidget(name_label)
            desc_label = QLabel(desc); desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter); desc_label.setStyleSheet("font-size: 12px; color: white; margin: 10px;")
            card_layout.addWidget(desc_label)
            btn = QPushButton("Select")
            btn.setStyleSheet(f"""
                QPushButton {{ background-color: white; color: {color}; font-weight: bold; padding: 10px; border-radius: 5px; font-size: 14px; }}
                QPushButton:hover {{ background-color: #f0f0f0; }}
            """)
            btn.clicked.connect(lambda checked, t=template_id: self.select_template(t))
            card_layout.addWidget(btn)
            templates_layout.addWidget(card)
        layout.addLayout(templates_layout)
        self.setLayout(layout)
    def select_template(self, template):
        self.selected_template = template
        self.accept()


class KeyBindingWidget(QWidget):
    # (کد شما بدون تغییر)
    DEFAULT_KEYS = {
        'move_left': Qt.Key.Key_A, 'move_right': Qt.Key.Key_D,
        'jump': Qt.Key.Key_Space, 'sprint': Qt.Key.Key_Shift,
        'pause': Qt.Key.Key_Escape, 'restart': Qt.Key.Key_R,
    }
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout(); layout.setSpacing(10)
        self.key_inputs = {}
        bindings = [
            ("Move Left:", "move_left", "A, Left Arrow"),
            ("Move Right:", "move_right", "D, Right Arrow"),
            ("Jump:", "jump", "Space, W, Up Arrow"),
            ("Sprint:", "sprint", "Shift"),
            ("Pause/Exit:", "pause", "Escape"),
            ("Restart:", "restart", "R"),
        ]
        for label, action, default_text in bindings:
            container = QWidget(); container.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            container_layout = QHBoxLayout(container); container_layout.setContentsMargins(0,0,0,0)
            key_edit = QKeySequenceEdit(); key_edit.setMaximumSequenceLength(2)
            key_edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            key_edit.setStyleSheet("""
                QKeySequenceEdit { padding: 8px; border: 2px solid #ccc; border-radius: 5px; background-color: white; font-size: 13px; min-width: 150px; text-align: left; }
                QKeySequenceEdit:focus { border-color: #4CAF50; }
            """)
            self.key_inputs[action] = key_edit
            if action in self.DEFAULT_KEYS: key_edit.setKeySequence(QKeySequence(self.DEFAULT_KEYS[action]))
            default_label = QLabel(f"Default: {default_text}")
            default_label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            default_label.setStyleSheet("color: #888; font-size: 11px; margin-left: 5px;")
            container_layout.addWidget(key_edit); container_layout.addWidget(default_label)
            layout.addRow(label, container)
        self.setLayout(layout); self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    def set_key_bindings(self, bindings):
        for action, keys in bindings.items():
            if action in self.key_inputs and keys: self.key_inputs[action].setKeySequence(QKeySequence(keys[0]))
    def get_key_bindings(self):
        result = {}
        for action, key_edit in self.key_inputs.items():
            sequence = key_edit.keySequence()
            if not sequence.isEmpty():
                result[action] = [sequence[i].key() for i in range(sequence.count())]
            elif action in self.DEFAULT_KEYS:
                result[action] = [self.DEFAULT_KEYS[action]]
        return result


class PlayerConfigWidget(QWidget):
    # (کد شما بدون تغییر)
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout(); layout.setSpacing(10)
        self.walk_speed = QDoubleSpinBox(); self.walk_speed.setRange(50,1000); self.walk_speed.setValue(200); self.walk_speed.setSuffix(" px/s")
        layout.addRow("Walk Speed:", self.walk_speed)
        self.run_speed = QDoubleSpinBox(); self.run_speed.setRange(100,2000); self.run_speed.setValue(400); self.run_speed.setSuffix(" px/s")
        layout.addRow("Run Speed:", self.run_speed)
        self.jump_force = QDoubleSpinBox(); self.jump_force.setRange(-2000,-100); self.jump_force.setValue(-500); self.jump_force.setSuffix(" px/s")
        layout.addRow("Jump Force:", self.jump_force)
        self.max_jumps = QSpinBox(); self.max_jumps.setRange(1,5); self.max_jumps.setValue(2); self.max_jumps.setSuffix(" jumps")
        layout.addRow("Max Jumps:", self.max_jumps)
        self.health = QSpinBox(); self.health.setRange(1,1000); self.health.setValue(100); self.health.setSuffix(" HP")
        layout.addRow("Health:", self.health)
        self.can_sprint = QCheckBox("Enable Sprint (Shift)"); self.can_sprint.setChecked(True)
        layout.addRow(self.can_sprint)
        self.can_jump = QCheckBox("Enable Jump"); self.can_jump.setChecked(True)
        layout.addRow(self.can_jump)
        self.setLayout(layout)
    def apply_to_player(self, player):
        if player:
            player.properties['walk_speed']=self.walk_speed.value(); player.properties['run_speed']=self.run_speed.value()
            player.properties['jump_force']=self.jump_force.value(); player.properties['max_jumps']=self.max_jumps.value()
            player.properties['health']=self.health.value(); player.properties['max_health']=self.health.value()
            player.properties['can_sprint']=self.can_sprint.isChecked(); player.properties['can_jump']=self.can_jump.isChecked()
            player.speed = self.walk_speed.value()
    def load_from_player(self, player):
        if player:
            self.walk_speed.setValue(player.properties.get('walk_speed',200))
            self.run_speed.setValue(player.properties.get('run_speed',400))
            self.jump_force.setValue(player.properties.get('jump_force',-500))
            self.max_jumps.setValue(player.properties.get('max_jumps',2))
            self.health.setValue(player.properties.get('health',100))
            self.can_sprint.setChecked(player.properties.get('can_sprint',True))
            self.can_jump.setChecked(player.properties.get('can_jump',True))


class GameConfigWidget(QWidget):
    # (کد شما بدون تغییر)
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        tabs = QTabWidget()
        main_tab = QWidget(); main_layout = QFormLayout(); main_layout.setSpacing(10)
        self.gravity = QDoubleSpinBox(); self.gravity.setRange(0,3000); self.gravity.setValue(980); self.gravity.setSuffix(" px/s²")
        main_layout.addRow("Gravity:", self.gravity)
        self.game_speed = QDoubleSpinBox(); self.game_speed.setRange(0.1,5.0); self.game_speed.setSingleStep(0.1); self.game_speed.setValue(1.0); self.game_speed.setSuffix("x")
        main_layout.addRow("Game Speed:", self.game_speed)
        self.win_condition = QComboBox(); self.win_condition.addItems(["collect_all","reach_point","survive"])
        main_layout.addRow("Win Condition:", self.win_condition)
        self.lose_condition = QComboBox(); self.lose_condition.addItems(["health_zero","fall_out","time_up"])
        main_layout.addRow("Lose Condition:", self.lose_condition)
        self.time_limit = QSpinBox(); self.time_limit.setRange(0,3600); self.time_limit.setSuffix(" seconds"); self.time_limit.setSpecialValueText("No limit")
        main_layout.addRow("Time Limit:", self.time_limit)
        self.particles_enabled = QCheckBox("Enable Particles"); self.particles_enabled.setChecked(True)
        main_layout.addRow(self.particles_enabled)
        self.particle_style = QComboBox(); self.particle_style.addItems(["default","sparkle","smoke"])
        main_layout.addRow("Particle Style:", self.particle_style)
        self.collectible_animation = QComboBox(); self.collectible_animation.addItems(["none","float","pulse","rotate"])
        main_layout.addRow("Item Animation:", self.collectible_animation)
        main_tab.setLayout(main_layout); tabs.addTab(main_tab, "General")
        self.key_binding_widget = KeyBindingWidget(); tabs.addTab(self.key_binding_widget, "Key Bindings")
        layout.addWidget(tabs)
        self.setLayout(layout)
    def apply_to_engine(self, engine):
        engine.game_config['gravity']=self.gravity.value(); engine.game_config['game_speed']=self.game_speed.value()
        engine.game_config['win_condition']=self.win_condition.currentText(); engine.game_config['lose_condition']=self.lose_condition.currentText()
        engine.game_config['time_limit']=self.time_limit.value()
        engine.game_config['particles_enabled']=self.particles_enabled.isChecked()
        engine.game_config['particle_style']=self.particle_style.currentText()
        engine.game_config['collectible_animation']=self.collectible_animation.currentText()
        engine.particles_enabled = self.particles_enabled.isChecked()
        kb = self.key_binding_widget.get_key_bindings()
        for action, keys in kb.items():
            if keys: engine.key_bindings[action] = keys
            elif action in FALLBACK_KEYS: engine.key_bindings[action] = FALLBACK_KEYS[action]
    def load_from_engine(self, engine):
        self.gravity.setValue(engine.game_config.get('gravity',980)); self.game_speed.setValue(engine.game_config.get('game_speed',1.0))
        self.win_condition.setCurrentText(engine.game_config.get('win_condition','collect_all'))
        self.lose_condition.setCurrentText(engine.game_config.get('lose_condition','health_zero'))
        self.time_limit.setValue(engine.game_config.get('time_limit',0))
        self.particles_enabled.setChecked(engine.game_config.get('particles_enabled',True))
        self.particle_style.setCurrentText(engine.game_config.get('particle_style','default'))
        self.collectible_animation.setCurrentText(engine.game_config.get('collectible_animation','float'))
        self.key_binding_widget.set_key_bindings(engine.key_bindings)


class EditorCanvas(QWidget):
    # (با تغییر کوچک برای انتخاب Collectible)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = GameEngine(template="platformer")
        self.setMinimumSize(800,600); self.setMouseTracking(True); self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.selected_object = None; self.dragging = False; self.drag_offset = (0,0)
        self.current_tool = "select"; self.show_grid = True; self.grid_size = 32; self.snap_to_grid = True
        self.scroll_x = 0; self.scroll_y = 0; self.world_width = 3000; self.world_height = 2000
        self.zoom = 1.0; self.middle_button_pressed = False; self.last_mouse_pos = QPoint()
        self.parent_widget = None

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(50,50,55))
        painter.save(); painter.translate(-self.scroll_x, -self.scroll_y); painter.scale(self.zoom, self.zoom)
        if self.show_grid:
            painter.setPen(QPen(QColor(70,70,75),1))
            start_x = int(self.scroll_x / self.grid_size) * self.grid_size
            for x in range(start_x, start_x + int(self.width()/self.zoom) + self.grid_size, self.grid_size):
                painter.drawLine(int(x), int(self.scroll_y), int(x), int(self.scroll_y + self.height()/self.zoom))
            start_y = int(self.scroll_y / self.grid_size) * self.grid_size
            for y in range(start_y, start_y + int(self.height()/self.zoom) + self.grid_size, self.grid_size):
                painter.drawLine(int(self.scroll_x), int(y), int(self.scroll_x + self.width()/self.zoom), int(y))
        anim_timer = self.engine.animation_timer
        for obj in self.engine.game_objects:
            if obj.active:
                obj.draw(painter, anim_timer)
                if obj == self.selected_object:
                    painter.setPen(QPen(Qt.GlobalColor.yellow, 3/self.zoom, Qt.PenStyle.DashLine))
                    painter.drawRect(int(obj.x-2), int(obj.y-2), int(obj.width+4), int(obj.height+4))
        painter.restore()

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            factor = 1.1 if event.angleDelta().y()>0 else 0.9
            self.zoom = max(0.1, min(3.0, self.zoom * factor))
        else:
            d = 50
            if event.angleDelta().y(): self.scroll_y -= (event.angleDelta().y()//abs(event.angleDelta().y()))*d
            if event.angleDelta().x(): self.scroll_x -= (event.angleDelta().x()//abs(event.angleDelta().x()))*d
            self.scroll_x = max(0, min(self.scroll_x, self.world_width - self.width()//self.zoom))
            self.scroll_y = max(0, min(self.scroll_y, self.world_height - self.height()//self.zoom))
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middle_button_pressed = True; self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor); return
        if event.button() != Qt.MouseButton.LeftButton: return
        x = (event.position().x() + self.scroll_x) / self.zoom
        y = (event.position().y() + self.scroll_y) / self.zoom
        if self.snap_to_grid:
            x = round(x / self.grid_size) * self.grid_size
            y = round(y / self.grid_size) * self.grid_size

        if self.current_tool == "select":
            self.selected_object = None
            for obj in reversed(self.engine.game_objects):
                rect = obj.get_rect()
                if obj.tag == 'collectible':
                    rect = rect.adjusted(-5, -5, 5, 5)  # بزرگ‌تر برای انتخاب راحت‌تر
                if rect.contains(x, y):
                    self.selected_object = obj
                    self.dragging = True
                    self.drag_offset = (x - obj.x, y - obj.y)
                    break
            if self.parent_widget:
                self.parent_widget.update_properties()
                self.parent_widget.update_object_list()

        elif self.current_tool == "player" and not any(o.tag=="player" for o in self.engine.game_objects):
            p = Player(x-20, y-30); self.engine.add_object(p); self.selected_object = p
        elif self.current_tool == "platform":
            p = Platform(x, y, self.grid_size*4, self.grid_size); self.engine.add_object(p); self.selected_object = p
        elif self.current_tool == "enemy":
            e = Enemy(x, y); self.engine.add_object(e); self.selected_object = e
        elif self.current_tool == "collectible":
            c = Collectible(x, y); self.engine.add_object(c); self.selected_object = c
        elif self.current_tool == "spawn" and not any(o.tag=="spawn" for o in self.engine.game_objects):
            s = SpawnPoint(x, y); self.engine.add_object(s); self.selected_object = s

        if self.parent_widget:
            self.parent_widget.update_properties(); self.parent_widget.update_object_list()
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.middle_button_pressed:
            delta = event.pos() - self.last_mouse_pos
            self.scroll_x -= delta.x(); self.scroll_y -= delta.y()
            self.scroll_x = max(0, min(self.scroll_x, self.world_width - self.width()//self.zoom))
            self.scroll_y = max(0, min(self.scroll_y, self.world_height - self.height()//self.zoom))
            self.last_mouse_pos = event.pos(); self.update(); return
        if not self.dragging or not self.selected_object: return
        x = (event.position().x() + self.scroll_x) / self.zoom - self.drag_offset[0]
        y = (event.position().y() + self.scroll_y) / self.zoom - self.drag_offset[1]
        if self.snap_to_grid:
            x = round(x/self.grid_size)*self.grid_size
            y = round(y/self.grid_size)*self.grid_size
        self.selected_object.x = max(0, min(x, self.world_width - self.selected_object.width))
        self.selected_object.y = max(0, min(y, self.world_height - self.selected_object.height))
        if self.parent_widget: self.parent_widget.update_properties()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middle_button_pressed = False; self.setCursor(Qt.CursorShape.ArrowCursor)
        self.dragging = False

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete and self.selected_object:
            self.engine.remove_object(self.selected_object); self.selected_object = None
            if self.parent_widget: self.parent_widget.update_properties(); self.parent_widget.update_object_list()
            self.update()
        elif event.key() == Qt.Key.Key_G: self.show_grid = not self.show_grid; self.update()
        elif event.key() == Qt.Key.Key_F and self.selected_object:
            self.scroll_x = int(self.selected_object.x - self.width()/2)
            self.scroll_y = int(self.selected_object.y - self.height()/2)
            self.scroll_x = max(0, min(self.scroll_x, self.world_width - self.width()))
            self.scroll_y = max(0, min(self.scroll_y, self.world_height - self.height()))
            self.update()

class GameWindow(QMainWindow):
    def __init__(self, engine_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎮 Game Running..."); self.setGeometry(150,150,900,700)
        self.canvas = GamePlayCanvas(); self.canvas.parent_window = self
        try: self.canvas.engine.from_dict(engine_data)
        except Exception as e: QMessageBox.critical(self,"Error",str(e)); self.close(); return
        self.setCentralWidget(self.canvas); self.canvas.start_game()
    def closeEvent(self, event):
        self.canvas.stop_game()
        if self.parent(): self.parent().on_game_window_closed()
        event.accept()

class GamePlayCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = GameEngine(); self.setMinimumSize(800,600); self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.timer = QTimer(); self.timer.timeout.connect(self.game_loop)
        self.keys_pressed = set(); self.jump_pressed = False; self.parent_window = None
    def start_game(self): self.timer.start(16); self.setFocus(); self.keys_pressed.clear(); self.jump_pressed=False
    def stop_game(self): self.timer.stop()
    def _get_bindings(self, action):
        bind = self.engine.key_bindings.get(action,[])
        return bind if bind else FALLBACK_KEYS.get(action,[])
    def game_loop(self):
        dt = 0.016 * self.engine.game_config.get('game_speed',1.0)
        if self.engine.player and not self.engine.game_over and not self.engine.game_won:
            dx=0; sprint=False
            for key in self.keys_pressed:
                if key in self._get_bindings('move_left'): dx=-1
                elif key in self._get_bindings('move_right'): dx=1
                elif key in self._get_bindings('sprint'): sprint=self.engine.player.properties.get('can_sprint',False)
            if dx: self.engine.move_player(dx, 'run' if sprint else 'walk')
            else: self.engine.player.vx=0
            for key in self.keys_pressed:
                if key in self._get_bindings('jump'):
                    if not self.jump_pressed and self.engine.player.properties.get('can_jump',True):
                        self.engine.jump_player(); self.jump_pressed=True
                    break
            else: self.jump_pressed=False
        self.engine.update(dt); self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self.engine.background_color)
        painter.save(); painter.translate(-self.engine.camera_x, -self.engine.camera_y)
        anim_timer = self.engine.animation_timer
        for obj in self.engine.game_objects:
            if obj.active and obj.tag != "spawn":
                obj.draw(painter, anim_timer)
        if self.engine.particles_enabled: self.engine.particle_system.draw(painter)
        painter.restore()
        self.draw_game_ui(painter)
    def draw_game_ui(self, painter):
        painter.fillRect(0,0,250,80, QColor(0,0,0,180)); painter.setPen(Qt.GlobalColor.white)
        f=QFont(); f.setPointSize(14); f.setBold(True); painter.setFont(f)
        painter.drawText(15,30, f"⭐ Score: {self.engine.score}")
        if self.engine.player:
            hp=self.engine.player.properties.get('health',0); mhp=self.engine.player.properties.get('max_health',100)
            painter.drawText(15,60, f"❤️ Health: {hp}/{mhp}")
            if hp<mhp:
                bar_x,bar_y,bar_w,bar_h = 15,70,220,6
                painter.fillRect(bar_x,bar_y,bar_w,bar_h, QColor(255,0,0,200))
                if mhp>0: painter.fillRect(bar_x,bar_y, int(bar_w*hp/mhp), bar_h, QColor(0,255,0,200))
        if self.engine.game_over:
            painter.fillRect(self.rect(), QColor(255,0,0,100)); painter.setPen(Qt.GlobalColor.white)
            f=QFont(); f.setPointSize(36); f.setBold(True); painter.setFont(f)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "GAME OVER!\nPress R to restart")
        elif self.engine.game_won:
            painter.fillRect(self.rect(), QColor(0,255,0,100)); painter.setPen(Qt.GlobalColor.white)
            f=QFont(); f.setPointSize(36); f.setBold(True); painter.setFont(f)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "LEVEL COMPLETE! 🎉")
    def keyPressEvent(self, event: QKeyEvent):
        self.keys_pressed.add(event.key())
        native = event.nativeVirtualKey()
        if native in NATIVE_KEY_MAP: self.keys_pressed.add(NATIVE_KEY_MAP[native])
        if any(k in self._get_bindings('pause') for k in self.keys_pressed):
            if self.parent_window: self.parent_window.close()
        if any(k in self._get_bindings('restart') for k in self.keys_pressed):
            self.restart_game()
    def keyReleaseEvent(self, event: QKeyEvent):
        self.keys_pressed.discard(event.key())
        native = event.nativeVirtualKey()
        if native in NATIVE_KEY_MAP: self.keys_pressed.discard(NATIVE_KEY_MAP[native])
    def restart_game(self):
        spawn = next((o for o in self.engine.game_objects if o.tag=="spawn"), None)
        self.engine.game_over=False; self.engine.game_won=False; self.engine.score=0
        if self.engine.player:
            self.engine.player.properties['health']=self.engine.player.properties.get('max_health',100)
            self.engine.player.properties['current_jumps']=0
            self.engine.player.vx=self.engine.player.vy=0
            if spawn: self.engine.player.x, self.engine.player.y = spawn.x, spawn.y
            else: self.engine.player.x, self.engine.player.y = 100,100
        for obj in self.engine.game_objects:
            if obj.tag=="collectible": obj.collected=False; obj.active=True
            elif obj.tag=="enemy": obj.active=True; obj.x,obj.y=obj.start_x,obj.start_y; obj.vx=obj.vy=0
        self.engine.particle_system.clear(); self.keys_pressed.clear(); self.jump_pressed=False; self.setFocus()


class MainWindow(QMainWindow):
    def __init__(self, template="platformer"):
        super().__init__()
        self.setWindowTitle(f"🎮 2D Game Engine - {template.capitalize()} Template")
        self.setGeometry(100,100,1400,850)
        self.template=template; self.game_window=None; self.panel_collapsed=False

        # ---- Toolbar ----
        toolbar = QToolBar("Main Toolbar"); toolbar.setMovable(False); toolbar.setIconSize(QSize(24,24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.play_action = QAction("▶ Play", self); self.play_action.triggered.connect(self.start_game); toolbar.addAction(self.play_action)
        self.stop_action = QAction("⏹ Stop", self); self.stop_action.triggered.connect(self.stop_game); self.stop_action.setEnabled(False); toolbar.addAction(self.stop_action)
        toolbar.addSeparator()
        self.save_action = QAction("💾 Save", self); self.save_action.triggered.connect(self.save_level); toolbar.addAction(self.save_action)
        self.load_action = QAction("📂 Load", self); self.load_action.triggered.connect(self.load_level); toolbar.addAction(self.load_action)
        toolbar.addSeparator()
        self.clear_action = QAction("🗑️ Clear", self); self.clear_action.triggered.connect(self.clear_all); toolbar.addAction(self.clear_action)

        # ---- Central Widget ----
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget); main_layout.setSpacing(0); main_layout.setContentsMargins(5,5,5,5)
        splitter = QSplitter(Qt.Orientation.Horizontal); splitter.setChildrenCollapsible(False); self.splitter=splitter

        left_panel = QWidget(); left_panel.setMinimumWidth(200); left_panel.setMaximumWidth(500); left_panel.setStyleSheet("background-color: #2b2b2b;")
        left_layout = QVBoxLayout(left_panel); left_layout.setSpacing(5); left_layout.setContentsMargins(8,8,8,8)

        panel_controls = QHBoxLayout()
        self.collapse_btn = QPushButton("◀"); self.collapse_btn.setFixedSize(30,30)
        self.collapse_btn.setStyleSheet("QPushButton{background-color:#4a4a4a;color:white;border:none;border-radius:15px;font-size:16px;font-weight:bold;}QPushButton:hover{background-color:#5a5a5a;}")
        self.collapse_btn.clicked.connect(self.toggle_panel); panel_controls.addWidget(self.collapse_btn)
        panel_controls.addStretch(); panel_controls.addWidget(QLabel(template)); panel_controls.addStretch()
        left_layout.addLayout(panel_controls)

        self.tab_widget = QTabWidget()
        tools_tab = QWidget(); tools_layout = QVBoxLayout(tools_tab); tools_layout.setSpacing(5)
        design_group = QGroupBox("🔧 Design Tools")
        design_layout = QVBoxLayout(); design_layout.setSpacing(3)
        for txt,tool,sh in [("Select","select","1"),("Player","player","2"),("Platform","platform","3"),
                            ("Enemy","enemy","4"),("Item","collectible","5"),("Spawn","spawn","6")]:
            btn=QPushButton(f"{txt} ({sh})"); btn.clicked.connect(lambda _,t=tool: self.set_tool(t)); design_layout.addWidget(btn)
        grid_layout = QHBoxLayout()
        self.grid_check=QCheckBox("Grid"); self.grid_check.setChecked(True); self.snap_check=QCheckBox("Snap"); self.snap_check.setChecked(True)
        grid_layout.addWidget(self.grid_check); grid_layout.addWidget(self.snap_check); design_layout.addLayout(grid_layout)
        design_group.setLayout(design_layout); tools_layout.addWidget(design_group)

        self.props_group = QGroupBox("📋 Properties")
        self.props_layout = QFormLayout(); self.props_layout.setSpacing(3)
        spin_style = "QSpinBox,QDoubleSpinBox{padding:4px;border:1px solid #555;border-radius:3px;background-color:#3c3c3c;color:white;font-size:11px;min-width:70px;max-width:100px;}"
        self.prop_x=QSpinBox(); self.prop_x.setRange(0,5000); self.prop_x.valueChanged.connect(self.on_property_changed); self.prop_x.setStyleSheet(spin_style)
        self.props_layout.addRow("X:",self.prop_x)
        self.prop_y=QSpinBox(); self.prop_y.setRange(0,5000); self.prop_y.valueChanged.connect(self.on_property_changed); self.prop_y.setStyleSheet(spin_style)
        self.props_layout.addRow("Y:",self.prop_y)
        self.prop_width=QSpinBox(); self.prop_width.setRange(10,2000); self.prop_width.valueChanged.connect(self.on_property_changed); self.prop_width.setStyleSheet(spin_style)
        self.props_layout.addRow("W:",self.prop_width)
        self.prop_height=QSpinBox(); self.prop_height.setRange(10,2000); self.prop_height.valueChanged.connect(self.on_property_changed); self.prop_height.setStyleSheet(spin_style)
        self.props_layout.addRow("H:",self.prop_height)

        # Model & Animation combos
        self.model_combo = QComboBox(); self.model_combo.currentTextChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Model:", self.model_combo)
        self.anim_combo = QComboBox(); self.anim_combo.currentTextChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Animation:", self.anim_combo)

        # AI fields (hidden unless enemy)
        self.prop_ai_type = QComboBox(); self.prop_ai_type.addItems(["patrol","chase","static","jumper"]); self.prop_ai_type.currentTextChanged.connect(self.on_property_changed)
        self.props_layout.addRow("AI Type:", self.prop_ai_type)
        self.prop_detection_range = QSpinBox(); self.prop_detection_range.setRange(0,1000); self.prop_detection_range.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Detection:", self.prop_detection_range)
        self.prop_chase_speed = QDoubleSpinBox(); self.prop_chase_speed.setRange(0,1000); self.prop_chase_speed.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Chase Spd:", self.prop_chase_speed)
        self.prop_speed = QDoubleSpinBox(); self.prop_speed.setRange(0,1000); self.prop_speed.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Speed:", self.prop_speed)
        self.prop_patrol_range = QSpinBox(); self.prop_patrol_range.setRange(0,2000); self.prop_patrol_range.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Patrol Rng:", self.prop_patrol_range)
        self.prop_damage = QSpinBox(); self.prop_damage.setRange(0,1000); self.prop_damage.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Damage:", self.prop_damage)

        self.btn_color = QPushButton("🎨 Color"); self.btn_color.clicked.connect(self.change_color)
        self.props_layout.addRow(self.btn_color)
        self.btn_delete = QPushButton("🗑️ Delete"); self.btn_delete.clicked.connect(self.delete_selected)
        self.props_layout.addRow(self.btn_delete)

        self.props_group.setLayout(self.props_layout); tools_layout.addWidget(self.props_group)
        self.tab_widget.addTab(tools_tab,"🔧")
        self.player_config = PlayerConfigWidget(); self.tab_widget.addTab(self.player_config,"🏃")
        self.game_config = GameConfigWidget(); self.tab_widget.addTab(self.game_config,"⚙️")
        left_layout.addWidget(self.tab_widget)

        # Object list
        objects_group = QGroupBox("📦 Objects"); objects_layout = QVBoxLayout()
        self.objects_list = QListWidget(); self.objects_list.itemClicked.connect(self.select_from_list)
        self.objects_list.setStyleSheet("QListWidget{background-color:#3c3c3c;color:white;border:1px solid #555;border-radius:5px;font-size:11px;}QListWidget::item{padding:4px;border-bottom:1px solid #555;}QListWidget::item:selected{background-color:#4CAF50;}")
        self.objects_list.setMaximumHeight(300); objects_layout.addWidget(self.objects_list)
        objects_group.setLayout(objects_layout); left_layout.addWidget(objects_group)

        self.status_label = QLabel("Ready"); left_layout.addWidget(self.status_label)

        left_scroll = QScrollArea(); left_scroll.setWidgetResizable(True); left_scroll.setWidget(left_panel); self.left_scroll=left_scroll
        splitter.addWidget(left_scroll)

        self.editor_canvas = EditorCanvas(); self.editor_canvas.parent_widget = self
        self.editor_canvas.engine.template = template
        splitter.addWidget(self.editor_canvas); splitter.setSizes([280,1120])
        main_layout.addWidget(splitter)

        self.grid_check.stateChanged.connect(lambda: setattr(self.editor_canvas,'show_grid',self.grid_check.isChecked()))
        self.snap_check.stateChanged.connect(lambda: setattr(self.editor_canvas,'snap_to_grid',self.snap_check.isChecked()))
        self.game_config.load_from_engine(self.editor_canvas.engine)
        self.update_properties(); self.load_default_scene()

    def toggle_panel(self):
        lp = self.left_scroll.widget()
        if not self.panel_collapsed:
            self.collapsed_size = lp.width(); lp.setMinimumWidth(30); lp.setMaximumWidth(30)
            self.collapse_btn.setText("▶"); self.panel_collapsed = True
        else:
            lp.setMinimumWidth(200); lp.setMaximumWidth(500)
            total = sum(self.splitter.sizes())
            self.splitter.setSizes([self.collapsed_size, total - self.collapsed_size])
            self.collapse_btn.setText("◀"); self.panel_collapsed = False

    def set_tool(self, tool): self.editor_canvas.current_tool = tool; self.status_label.setText(f"Tool: {tool}")

    def load_default_scene(self):
        if self.template == "platformer":
            self.editor_canvas.engine.add_object(Platform(0,550,3000,50))
            for x,y,w,h in [(192,416,256,32),(512,320,256,32),(800,352,256,32)]:
                self.editor_canvas.engine.add_object(Platform(x,y,w,h))
            self.editor_canvas.engine.add_object(SpawnPoint(96,490))
            self.editor_canvas.engine.add_object(Player(96,490))
            for x,y in [(608,280),(1152,216)]: self.editor_canvas.engine.add_object(Enemy(x,y))
            for x,y in [(160,520),(224,520),(288,520)]: self.editor_canvas.engine.add_object(Collectible(x,y))
        self.update_object_list(); self.editor_canvas.update()

    def update_properties(self):
        obj = self.editor_canvas.selected_object
        is_enemy = bool(obj and obj.tag == "enemy")
        is_player = obj and obj.tag == "player"
        is_collectible = obj and obj.tag == "collectible"

        self.prop_ai_type.setVisible(is_enemy)
        self.prop_detection_range.setVisible(is_enemy)
        self.prop_chase_speed.setVisible(is_enemy)
        self.prop_speed.setVisible(is_enemy)
        self.prop_patrol_range.setVisible(is_enemy)
        self.prop_damage.setVisible(is_enemy)

        for w in [self.prop_x,self.prop_y,self.prop_width,self.prop_height,self.btn_color,self.btn_delete]:
            w.setEnabled(obj is not None)

        self.model_combo.clear(); self.anim_combo.clear()
        if is_player:
            self.model_combo.addItems(["classic","slime","robot"])
            self.model_combo.setCurrentText(obj.properties.get('model','classic'))
            self.anim_combo.addItems(["idle","walk","jump"])
            self.anim_combo.setCurrentText(obj.properties.get('animation','idle'))
            self.model_combo.setVisible(True); self.anim_combo.setVisible(True)
        elif is_enemy:
            self.model_combo.addItems(["skeleton","slime","bat"])
            self.model_combo.setCurrentText(obj.properties.get('model','skeleton'))
            self.anim_combo.addItems(["idle","walk","attack"])
            self.anim_combo.setCurrentText(obj.properties.get('animation','idle'))
            self.model_combo.setVisible(True); self.anim_combo.setVisible(True)
        elif is_collectible:
            self.model_combo.addItems(["coin","gem","star"])
            self.model_combo.setCurrentText(obj.properties.get('model','coin'))
            self.anim_combo.addItems(["float","pulse","rotate"])
            self.anim_combo.setCurrentText(obj.properties.get('anim_style','float'))
            self.model_combo.setVisible(True); self.anim_combo.setVisible(True)
        else:
            self.model_combo.setVisible(False); self.anim_combo.setVisible(False)

        if not obj: self.props_group.setTitle("📋 Properties (None)"); return
        self.props_group.setTitle(f"📋 Properties: {obj.tag}")
        self.prop_x.setEnabled(True); self.prop_y.setEnabled(True); self.prop_width.setEnabled(True); self.prop_height.setEnabled(True)
        self.btn_color.setEnabled(True); self.btn_delete.setEnabled(True)
        for w,v in [(self.prop_x,obj.x),(self.prop_y,obj.y),(self.prop_width,obj.width),(self.prop_height,obj.height)]:
            w.blockSignals(True); w.setValue(int(v)); w.blockSignals(False)
        if is_enemy:
            self.prop_ai_type.setCurrentText(obj.properties.get('ai_type','patrol'))
            self.prop_detection_range.setValue(obj.properties.get('detection_range',200))
            self.prop_chase_speed.setValue(obj.properties.get('chase_speed',150))
            self.prop_speed.setValue(obj.properties.get('speed',100))
            self.prop_patrol_range.setValue(obj.properties.get('patrol_range',100))
            self.prop_damage.setValue(obj.properties.get('damage',20))

    def on_property_changed(self):
        obj = self.editor_canvas.selected_object
        if not obj: return
        sender = self.sender()
        if sender == self.prop_x: obj.x = self.prop_x.value()
        elif sender == self.prop_y: obj.y = self.prop_y.value()
        elif sender == self.prop_width: obj.width = self.prop_width.value()
        elif sender == self.prop_height: obj.height = self.prop_height.value()
        elif sender == self.model_combo:
            if obj.tag in ("player","enemy"): obj.properties['model'] = self.model_combo.currentText()
            elif obj.tag == "collectible": obj.properties['model'] = self.model_combo.currentText()
        elif sender == self.anim_combo:
            if obj.tag in ("player","enemy"): obj.properties['animation'] = self.anim_combo.currentText()
            elif obj.tag == "collectible": obj.properties['anim_style'] = self.anim_combo.currentText()
        elif sender == self.prop_ai_type: obj.properties['ai_type'] = self.prop_ai_type.currentText()
        elif sender == self.prop_detection_range: obj.properties['detection_range'] = self.prop_detection_range.value()
        elif sender == self.prop_chase_speed: obj.properties['chase_speed'] = self.prop_chase_speed.value()
        elif sender == self.prop_speed: obj.properties['speed'] = self.prop_speed.value()
        elif sender == self.prop_patrol_range: obj.properties['patrol_range'] = self.prop_patrol_range.value()
        elif sender == self.prop_damage: obj.properties['damage'] = self.prop_damage.value()
        self.editor_canvas.update()

    def change_color(self):
        obj = self.editor_canvas.selected_object
        if obj:
            c = QColorDialog.getColor(obj.color, self)
            if c.isValid(): obj.color = c; self.editor_canvas.update()

    def delete_selected(self):
        if self.editor_canvas.selected_object:
            self.editor_canvas.engine.remove_object(self.editor_canvas.selected_object)
            self.editor_canvas.selected_object = None
            self.update_properties(); self.update_object_list(); self.editor_canvas.update()

    def update_object_list(self):
        self.objects_list.clear()
        for obj in self.editor_canvas.engine.game_objects:
            self.objects_list.addItem(f"{obj.tag} ({obj.__class__.__name__}) - ({int(obj.x)},{int(obj.y)})")

    def select_from_list(self, item):
        index = self.objects_list.row(item)
        if 0 <= index < len(self.editor_canvas.engine.game_objects):
            self.editor_canvas.selected_object = self.editor_canvas.engine.game_objects[index]
            self.update_properties(); self.editor_canvas.update()

    def start_game(self):
        if not any(o.tag=="player" for o in self.editor_canvas.engine.game_objects):
            QMessageBox.warning(self,"Error","Please add a Player first!"); return
        try:
            if self.editor_canvas.engine.player: self.player_config.apply_to_player(self.editor_canvas.engine.player)
            self.game_config.apply_to_engine(self.editor_canvas.engine)
            self.editor_state = self.editor_canvas.engine.to_dict()
            self.gw = GameWindow(self.editor_canvas.engine.to_dict(), self)
            self.gw.show()
            self.play_action.setEnabled(False); self.stop_action.setEnabled(True)
            self.status_label.setText("🎮 Game running...")
        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))
            self.play_action.setEnabled(True); self.stop_action.setEnabled(False)

    def stop_game(self):
        if self.gw: self.gw.close()

    def on_game_window_closed(self):
        self.gw = None; self.play_action.setEnabled(True); self.stop_action.setEnabled(False)
        self.status_label.setText("Editor Mode")
        if hasattr(self,'editor_state'):
            self.editor_canvas.engine.from_dict(self.editor_state)
            self.update_properties(); self.update_object_list(); self.editor_canvas.update()

    def save_level(self):
        fn,_ = QFileDialog.getSaveFileName(self,"Save Level","","JSON Files (*.json)")
        if fn:
            with open(fn,'w') as f: json.dump(self.editor_canvas.engine.to_dict(), f, indent=2)
            self.status_label.setText(f"✅ Saved to {fn}")

    def load_level(self):
        fn,_ = QFileDialog.getOpenFileName(self,"Load Level","","JSON Files (*.json)")
        if fn:
            with open(fn,'r') as f: self.editor_canvas.engine.from_dict(json.load(f))
            self.editor_canvas.selected_object = None
            self.update_properties(); self.update_object_list(); self.editor_canvas.update()
            self.status_label.setText(f"📂 Loaded from {fn}")

    def clear_all(self):
        if QMessageBox.question(self,"Clear All","Are you sure?",
                                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
            self.editor_canvas.engine.reset(); self.editor_canvas.selected_object = None
            self.update_properties(); self.update_object_list(); self.editor_canvas.update()
            self.status_label.setText("🗑️ All objects cleared")

    def keyPressEvent(self, event):
        shortcuts = {Qt.Key.Key_1:"select",Qt.Key.Key_2:"player",Qt.Key.Key_3:"platform",
                     Qt.Key.Key_4:"enemy",Qt.Key.Key_5:"collectible",Qt.Key.Key_6:"spawn"}
        if event.key() in shortcuts: self.set_tool(shortcuts[event.key()])
        super().keyPressEvent(event)


class GameLauncher:
    def __init__(self):
        self.app = QApplication(sys.argv); self.app.setStyle('Fusion')
        self.app.setStyleSheet("QMainWindow{background-color:#2b2b2b;}QToolTip{background-color:#333;color:white;border:1px solid #555;padding:5px;font-size:12px;}")
        dialog = TemplateDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            w = MainWindow(dialog.selected_template); w.show()
            sys.exit(self.app.exec())

def main():
    GameLauncher()

if __name__ == "__main__":
    main()