import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QSpinBox,
                             QComboBox, QColorDialog, QGroupBox, QFormLayout,
                             QListWidget, QMessageBox, QFileDialog, QDialog,
                             QDoubleSpinBox, QCheckBox, QTabWidget,
                             QScrollArea, QKeySequenceEdit, QSplitter, QFrame)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPoint
from PyQt6.QtGui import (QPainter, QColor, QBrush, QPen, QFont,
                         QKeyEvent, QMouseEvent, QKeySequence, QWheelEvent)
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
                QFrame {{
                    background-color: {color};
                    border-radius: 15px;
                    padding: 20px;
                }}
                QFrame:hover {{
                    border: 3px solid white;
                }}
            """)
            card_layout = QVBoxLayout(card)

            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("font-size: 48px;")
            card_layout.addWidget(icon_label)

            name_label = QLabel(name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
            card_layout.addWidget(name_label)

            desc_label = QLabel(desc)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setStyleSheet("font-size: 12px; color: white; margin: 10px;")
            card_layout.addWidget(desc_label)

            btn = QPushButton("Select")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    color: {color};
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: #f0f0f0;
                }}
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
    DEFAULT_KEYS = {
        'move_left': Qt.Key.Key_A,
        'move_right': Qt.Key.Key_D,
        'jump': Qt.Key.Key_Space,
        'sprint': Qt.Key.Key_Shift,
        'pause': Qt.Key.Key_Escape,
        'restart': Qt.Key.Key_R,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        layout.setSpacing(10)

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
            container = QWidget()
            container.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)

            key_edit = QKeySequenceEdit()
            key_edit.setMaximumSequenceLength(2)
            key_edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            key_edit.setStyleSheet("""
                QKeySequenceEdit {
                    padding: 8px;
                    border: 2px solid #ccc;
                    border-radius: 5px;
                    background-color: white;
                    font-size: 13px;
                    min-width: 150px;
                    text-align: left;
                }
                QKeySequenceEdit:focus {
                    border-color: #4CAF50;
                }
            """)
            self.key_inputs[action] = key_edit

            if action in self.DEFAULT_KEYS:
                key_edit.setKeySequence(QKeySequence(self.DEFAULT_KEYS[action]))

            default_label = QLabel(f"Default: {default_text}")
            default_label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            default_label.setStyleSheet("color: #888; font-size: 11px; margin-left: 5px;")

            container_layout.addWidget(key_edit)
            container_layout.addWidget(default_label)

            layout.addRow(label, container)

        self.setLayout(layout)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def set_key_bindings(self, bindings):
        for action, keys in bindings.items():
            if action in self.key_inputs and keys:
                self.key_inputs[action].setKeySequence(QKeySequence(keys[0]))

    def get_key_bindings(self):
        result = {}
        for action, key_edit in self.key_inputs.items():
            sequence = key_edit.keySequence()
            if not sequence.isEmpty():
                keys = []
                for i in range(sequence.count()):
                    keys.append(sequence[i].key())
                result[action] = keys
            else:
                if action in self.DEFAULT_KEYS:
                    result[action] = [self.DEFAULT_KEYS[action]]
        return result


class PlayerConfigWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        layout.setSpacing(10)

        self.walk_speed = QDoubleSpinBox()
        self.walk_speed.setRange(50, 1000)
        self.walk_speed.setValue(200)
        self.walk_speed.setSuffix(" px/s")
        layout.addRow("Walk Speed:", self.walk_speed)

        self.run_speed = QDoubleSpinBox()
        self.run_speed.setRange(100, 2000)
        self.run_speed.setValue(400)
        self.run_speed.setSuffix(" px/s")
        layout.addRow("Run Speed:", self.run_speed)

        self.jump_force = QDoubleSpinBox()
        self.jump_force.setRange(-2000, -100)
        self.jump_force.setValue(-500)
        self.jump_force.setSuffix(" px/s")
        layout.addRow("Jump Force:", self.jump_force)

        self.max_jumps = QSpinBox()
        self.max_jumps.setRange(1, 5)
        self.max_jumps.setValue(2)
        self.max_jumps.setSuffix(" jumps")
        layout.addRow("Max Jumps:", self.max_jumps)

        self.health = QSpinBox()
        self.health.setRange(1, 1000)
        self.health.setValue(100)
        self.health.setSuffix(" HP")
        layout.addRow("Health:", self.health)

        self.can_sprint = QCheckBox("Enable Sprint (Shift)")
        self.can_sprint.setChecked(True)
        layout.addRow(self.can_sprint)

        self.can_jump = QCheckBox("Enable Jump")
        self.can_jump.setChecked(True)
        layout.addRow(self.can_jump)

        self.setLayout(layout)

    def apply_to_player(self, player):
        if player:
            player.properties['walk_speed'] = self.walk_speed.value()
            player.properties['run_speed'] = self.run_speed.value()
            player.properties['jump_force'] = self.jump_force.value()
            player.properties['max_jumps'] = self.max_jumps.value()
            player.properties['health'] = self.health.value()
            player.properties['max_health'] = self.health.value()
            player.properties['can_sprint'] = self.can_sprint.isChecked()
            player.properties['can_jump'] = self.can_jump.isChecked()
            player.speed = self.walk_speed.value()

    def load_from_player(self, player):
        if player:
            self.walk_speed.setValue(player.properties.get('walk_speed', 200))
            self.run_speed.setValue(player.properties.get('run_speed', 400))
            self.jump_force.setValue(player.properties.get('jump_force', -500))
            self.max_jumps.setValue(player.properties.get('max_jumps', 2))
            self.health.setValue(player.properties.get('health', 100))
            self.can_sprint.setChecked(player.properties.get('can_sprint', True))
            self.can_jump.setChecked(player.properties.get('can_jump', True))


class GameConfigWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        tabs = QTabWidget()

        main_tab = QWidget()
        main_layout = QFormLayout()
        main_layout.setSpacing(10)

        self.gravity = QDoubleSpinBox()
        self.gravity.setRange(0, 3000)
        self.gravity.setValue(980)
        self.gravity.setSuffix(" px/s²")
        main_layout.addRow("Gravity:", self.gravity)

        self.game_speed = QDoubleSpinBox()
        self.game_speed.setRange(0.1, 5.0)
        self.game_speed.setSingleStep(0.1)
        self.game_speed.setValue(1.0)
        self.game_speed.setSuffix("x")
        main_layout.addRow("Game Speed:", self.game_speed)

        self.win_condition = QComboBox()
        self.win_condition.addItems(["collect_all", "reach_point", "survive"])
        main_layout.addRow("Win Condition:", self.win_condition)

        self.lose_condition = QComboBox()
        self.lose_condition.addItems(["health_zero", "fall_out", "time_up"])
        main_layout.addRow("Lose Condition:", self.lose_condition)

        self.time_limit = QSpinBox()
        self.time_limit.setRange(0, 3600)
        self.time_limit.setSuffix(" seconds")
        self.time_limit.setSpecialValueText("No limit")
        main_layout.addRow("Time Limit:", self.time_limit)

        # ذرات
        self.particles_enabled = QCheckBox("Enable Particles")
        self.particles_enabled.setChecked(True)
        main_layout.addRow(self.particles_enabled)

        self.particle_style = QComboBox()
        self.particle_style.addItems(["default", "sparkle", "smoke"])
        main_layout.addRow("Particle Style:", self.particle_style)

        # انیمیشن اشیاء
        self.collectible_animation = QComboBox()
        self.collectible_animation.addItems(["none", "float", "pulse", "rotate"])
        main_layout.addRow("Item Animation:", self.collectible_animation)

        main_tab.setLayout(main_layout)
        tabs.addTab(main_tab, "General")

        self.key_binding_widget = KeyBindingWidget()
        tabs.addTab(self.key_binding_widget, "Key Bindings")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def apply_to_engine(self, engine):
        engine.game_config['gravity'] = self.gravity.value()
        engine.game_config['game_speed'] = self.game_speed.value()
        engine.game_config['win_condition'] = self.win_condition.currentText()
        engine.game_config['lose_condition'] = self.lose_condition.currentText()
        engine.game_config['time_limit'] = self.time_limit.value()
        engine.game_config['particles_enabled'] = self.particles_enabled.isChecked()
        engine.game_config['particle_style'] = self.particle_style.currentText()
        engine.game_config['collectible_animation'] = self.collectible_animation.currentText()
        engine.particles_enabled = self.particles_enabled.isChecked()

        key_bindings = self.key_binding_widget.get_key_bindings()
        if key_bindings:
            for action, keys in key_bindings.items():
                if keys:
                    engine.key_bindings[action] = keys
                else:
                    if action in FALLBACK_KEYS:
                        engine.key_bindings[action] = FALLBACK_KEYS[action]
        else:
            engine.key_bindings = {k: v.copy() for k, v in FALLBACK_KEYS.items()}

    def load_from_engine(self, engine):
        self.gravity.setValue(engine.game_config.get('gravity', 980))
        self.game_speed.setValue(engine.game_config.get('game_speed', 1.0))
        self.win_condition.setCurrentText(engine.game_config.get('win_condition', 'collect_all'))
        self.lose_condition.setCurrentText(engine.game_config.get('lose_condition', 'health_zero'))
        self.time_limit.setValue(engine.game_config.get('time_limit', 0))
        self.particles_enabled.setChecked(engine.game_config.get('particles_enabled', True))
        self.particle_style.setCurrentText(engine.game_config.get('particle_style', 'default'))
        self.collectible_animation.setCurrentText(engine.game_config.get('collectible_animation', 'float'))
        self.key_binding_widget.set_key_bindings(engine.key_bindings)


class EditorCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = GameEngine(template="platformer")
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.selected_object = None
        self.dragging = False
        self.drag_offset = (0, 0)
        self.current_tool = "select"
        self.show_grid = True
        self.grid_size = 32
        self.snap_to_grid = True

        self.scroll_x = 0
        self.scroll_y = 0
        self.world_width = 3000
        self.world_height = 2000
        self.zoom = 1.0
        self.middle_button_pressed = False
        self.last_mouse_pos = QPoint()

        self.parent_widget = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor(50, 50, 55))

        painter.save()
        painter.translate(-self.scroll_x, -self.scroll_y)
        painter.scale(self.zoom, self.zoom)

        if self.show_grid:
            painter.setPen(QPen(QColor(70, 70, 75), 1))

            start_x = int(self.scroll_x / self.grid_size) * self.grid_size
            for x in range(start_x, start_x + int(self.width() / self.zoom) + self.grid_size, self.grid_size):
                painter.drawLine(int(x), int(self.scroll_y),
                                 int(x), int(self.scroll_y + self.height() / self.zoom))

            start_y = int(self.scroll_y / self.grid_size) * self.grid_size
            for y in range(start_y, start_y + int(self.height() / self.zoom) + self.grid_size, self.grid_size):
                painter.drawLine(int(self.scroll_x), int(y),
                                 int(self.scroll_x + self.width() / self.zoom), int(y))

        anim_timer = self.engine.animation_timer
        anim_style = self.engine.game_config.get('collectible_animation', 'float')
        for obj in self.engine.game_objects:
            if obj.active:
                if obj.tag == 'collectible':
                    obj.draw(painter, anim_timer, anim_style)
                else:
                    obj.draw(painter, anim_timer)
                if obj == self.selected_object:
                    painter.setPen(QPen(Qt.GlobalColor.yellow, 3 / self.zoom, Qt.PenStyle.DashLine))
                    painter.drawRect(int(obj.x - 2), int(obj.y - 2),
                                     int(obj.width + 4), int(obj.height + 4))

        painter.restore()

        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(10, self.height() - 20,
                         f"Scroll: ({int(self.scroll_x)}, {int(self.scroll_y)}) | Zoom: {self.zoom:.1f}x")
        painter.drawText(self.width() - 250, self.height() - 20,
                         f"Grid: {self.grid_size}px | Objects: {len(self.engine.game_objects)}")

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_factor = 1.1
            if event.angleDelta().y() > 0:
                self.zoom = min(3.0, self.zoom * zoom_factor)
            else:
                self.zoom = max(0.1, self.zoom / zoom_factor)
            self.update()
        else:
            scroll_speed = 50
            if event.angleDelta().y() != 0:
                self.scroll_y -= event.angleDelta().y() // abs(event.angleDelta().y()) * scroll_speed
            if event.angleDelta().x() != 0:
                self.scroll_x -= event.angleDelta().x() // abs(event.angleDelta().x()) * scroll_speed
            self.scroll_y = max(0, min(self.scroll_y, self.world_height - self.height()))
            self.scroll_x = max(0, min(self.scroll_x, self.world_width - self.width()))
            self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middle_button_pressed = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

        if event.button() != Qt.MouseButton.LeftButton:
            return

        x = (event.position().x() + self.scroll_x) / self.zoom
        y = (event.position().y() + self.scroll_y) / self.zoom

        if self.snap_to_grid:
            x = round(x / self.grid_size) * self.grid_size
            y = round(y / self.grid_size) * self.grid_size

        if self.current_tool == "select":
            self.selected_object = None
            for obj in reversed(self.engine.game_objects):
                if obj.get_rect().contains(x, y):
                    self.selected_object = obj
                    self.dragging = True
                    self.drag_offset = (x - obj.x, y - obj.y)
                    break
            if self.parent_widget:
                self.parent_widget.update_properties()
                self.parent_widget.update_object_list()

        elif self.current_tool == "player":
            if not any(obj.tag == "player" for obj in self.engine.game_objects):
                player = Player(x - 20, y - 30)
                self.engine.add_object(player)
                self.selected_object = player

        elif self.current_tool == "platform":
            platform = Platform(x, y, self.grid_size * 4, self.grid_size)
            self.engine.add_object(platform)
            self.selected_object = platform

        elif self.current_tool == "enemy":
            enemy = Enemy(x, y)
            self.engine.add_object(enemy)
            self.selected_object = enemy

        elif self.current_tool == "collectible":
            collectible = Collectible(x, y)
            self.engine.add_object(collectible)
            self.selected_object = collectible

        elif self.current_tool == "spawn":
            if not any(obj.tag == "spawn" for obj in self.engine.game_objects):
                spawn = SpawnPoint(x, y)
                self.engine.add_object(spawn)
                self.selected_object = spawn

        if self.parent_widget:
            self.parent_widget.update_properties()
            self.parent_widget.update_object_list()
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.middle_button_pressed:
            delta = event.pos() - self.last_mouse_pos
            self.scroll_x -= delta.x()
            self.scroll_y -= delta.y()
            self.scroll_x = max(0, min(self.scroll_x, self.world_width - self.width()))
            self.scroll_y = max(0, min(self.scroll_y, self.world_height - self.height()))
            self.last_mouse_pos = event.pos()
            self.update()
            return

        if not self.dragging or not self.selected_object:
            return

        x = (event.position().x() + self.scroll_x) / self.zoom - self.drag_offset[0]
        y = (event.position().y() + self.scroll_y) / self.zoom - self.drag_offset[1]

        if self.snap_to_grid:
            x = round(x / self.grid_size) * self.grid_size
            y = round(y / self.grid_size) * self.grid_size

        self.selected_object.x = max(0, min(x, self.world_width - self.selected_object.width))
        self.selected_object.y = max(0, min(y, self.world_height - self.selected_object.height))

        if self.parent_widget:
            self.parent_widget.update_properties()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middle_button_pressed = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.dragging = False

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Delete and self.selected_object:
            self.engine.remove_object(self.selected_object)
            self.selected_object = None
            if self.parent_widget:
                self.parent_widget.update_properties()
                self.parent_widget.update_object_list()
            self.update()
        elif event.key() == Qt.Key.Key_G:
            self.show_grid = not self.show_grid
            self.update()
        elif event.key() == Qt.Key.Key_F:
            if self.selected_object:
                self.scroll_x = int(self.selected_object.x - self.width() / 2)
                self.scroll_y = int(self.selected_object.y - self.height() / 2)
                self.scroll_x = max(0, min(self.scroll_x, self.world_width - self.width()))
                self.scroll_y = max(0, min(self.scroll_y, self.world_height - self.height()))
                self.update()


class GameWindow(QMainWindow):
    def __init__(self, engine_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎮 Game Running...")
        self.setGeometry(150, 150, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = GamePlayCanvas()
        self.canvas.parent_window = self

        try:
            self.canvas.engine.from_dict(engine_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load game data: {str(e)}")
            self.close()
            return

        layout.addWidget(self.canvas)

        self.canvas.start_game()

    def closeEvent(self, event):
        self.canvas.stop_game()
        if self.parent():
            self.parent().on_game_window_closed()
        event.accept()


class GamePlayCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = GameEngine()
        self.setMinimumSize(800, 600)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.keys_pressed = set()
        self.jump_pressed = False
        self.parent_window = None

    def start_game(self):
        self.timer.start(16)
        self.setFocus()
        self.keys_pressed.clear()
        self.jump_pressed = False

    def stop_game(self):
        self.timer.stop()

    def _get_bindings(self, action):
        bind = self.engine.key_bindings.get(action, [])
        if not bind:
            bind = FALLBACK_KEYS.get(action, [])
        return bind

    def game_loop(self):
        dt = 0.016 * self.engine.game_config.get('game_speed', 1.0)

        if self.engine.player and not self.engine.game_over and not self.engine.game_won:
            dx = 0
            sprint = False

            move_left_keys = self._get_bindings('move_left')
            move_right_keys = self._get_bindings('move_right')
            sprint_keys = self._get_bindings('sprint')
            jump_keys = self._get_bindings('jump')

            for key in self.keys_pressed:
                if key in move_left_keys:
                    dx = -1
                elif key in move_right_keys:
                    dx = 1
                elif key in sprint_keys:
                    sprint = self.engine.player.properties.get('can_sprint', False)

            if dx != 0:
                self.engine.move_player(dx, 'run' if sprint else 'walk')
            else:
                self.engine.player.vx = 0

            should_jump = False
            for key in self.keys_pressed:
                if key in jump_keys:
                    should_jump = True
                    break

            if should_jump and not self.jump_pressed:
                if self.engine.player.properties.get('can_jump', True):
                    self.engine.jump_player()
                self.jump_pressed = True
            elif not should_jump:
                self.jump_pressed = False

        self.engine.update(dt)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), self.engine.background_color)

        painter.save()
        painter.translate(-self.engine.camera_x, -self.engine.camera_y)

        anim_timer = self.engine.animation_timer
        anim_style = self.engine.game_config.get('collectible_animation', 'float')
        for obj in self.engine.game_objects:
            if obj.active and obj.tag != "spawn":
                if obj.tag == 'collectible':
                    obj.draw(painter, anim_timer, anim_style)
                else:
                    obj.draw(painter, anim_timer)

        if self.engine.particles_enabled:
            self.engine.particle_system.draw(painter)

        painter.restore()

        self.draw_game_ui(painter)

    def draw_game_ui(self, painter):
        painter.fillRect(0, 0, 250, 80, QColor(0, 0, 0, 180))
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(15, 30, f"⭐ Score: {self.engine.score}")

        if self.engine.player:
            health = self.engine.player.properties.get('health', 0)
            max_health = self.engine.player.properties.get('max_health', 100)
            painter.drawText(15, 60, f"❤️ Health: {health}/{max_health}")

            if health < max_health:
                bar_x = 15
                bar_y = 70
                bar_width = 220
                bar_height = 6

                painter.fillRect(bar_x, bar_y, bar_width, bar_height, QColor(255, 0, 0, 200))
                if max_health > 0:
                    painter.fillRect(bar_x, bar_y, int(bar_width * (health / max_health)), bar_height,
                                     QColor(0, 255, 0, 200))

        if self.engine.game_over:
            painter.fillRect(self.rect(), QColor(255, 0, 0, 100))
            painter.setPen(QPen(Qt.GlobalColor.white))
            font = QFont()
            font.setPointSize(36)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "GAME OVER!\nPress R to restart")
        elif self.engine.game_won:
            painter.fillRect(self.rect(), QColor(0, 255, 0, 100))
            painter.setPen(QPen(Qt.GlobalColor.white))
            font = QFont()
            font.setPointSize(36)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "LEVEL COMPLETE! 🎉")

    def keyPressEvent(self, event: QKeyEvent):
        self.keys_pressed.add(event.key())

        native = event.nativeVirtualKey()
        if native in NATIVE_KEY_MAP:
            physical_key = NATIVE_KEY_MAP[native]
            self.keys_pressed.add(physical_key)

        if any(k in self._get_bindings('pause') for k in self.keys_pressed):
            if self.parent_window:
                self.parent_window.close()

        if any(k in self._get_bindings('restart') for k in self.keys_pressed):
            self.restart_game()

    def keyReleaseEvent(self, event: QKeyEvent):
        self.keys_pressed.discard(event.key())

        native = event.nativeVirtualKey()
        if native in NATIVE_KEY_MAP:
            physical_key = NATIVE_KEY_MAP[native]
            self.keys_pressed.discard(physical_key)

    def restart_game(self):
        spawn = None
        for obj in self.engine.game_objects:
            if obj.tag == "spawn":
                spawn = obj
                break

        self.engine.game_over = False
        self.engine.game_won = False
        self.engine.score = 0

        if self.engine.player:
            self.engine.player.properties['health'] = self.engine.player.properties.get('max_health', 100)
            self.engine.player.properties['current_jumps'] = 0
            self.engine.player.vx = 0
            self.engine.player.vy = 0
            self.engine.player.is_on_ground = False

            if spawn:
                self.engine.player.x = spawn.x
                self.engine.player.y = spawn.y
            else:
                self.engine.player.x = 100
                self.engine.player.y = 100

        for obj in self.engine.game_objects:
            if obj.tag == "collectible":
                obj.collected = False
                obj.active = True
            elif obj.tag == "enemy":
                obj.active = True
                obj.x = obj.start_x
                obj.y = obj.start_y
                obj.vx = 0
                obj.vy = 0

        self.engine.particle_system.clear()
        self.keys_pressed.clear()
        self.jump_pressed = False
        self.setFocus()


class MainWindow(QMainWindow):
    def __init__(self, template="platformer"):
        super().__init__()
        self.setWindowTitle(f"🎮 2D Game Engine - {template.capitalize()} Template")
        self.setGeometry(100, 100, 1400, 850)

        self.template = template
        self.game_window = None
        self.panel_collapsed = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(5, 5, 5, 5)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self.splitter = splitter

        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_panel.setMinimumWidth(200)
        left_panel.setMaximumWidth(500)
        left_panel.setStyleSheet("background-color: #2b2b2b;")

        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(8, 8, 8, 8)

        panel_controls = QHBoxLayout()

        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setFixedSize(30, 30)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        self.collapse_btn.clicked.connect(self.toggle_panel)
        panel_controls.addWidget(self.collapse_btn)

        panel_controls.addStretch()

        self.panel_title = QLabel(f"{template.capitalize()}")
        self.panel_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        panel_controls.addWidget(self.panel_title)

        panel_controls.addStretch()
        left_layout.addLayout(panel_controls)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { 
                border: 2px solid #444; 
                border-radius: 8px; 
                background-color: #363636; 
            }
            QTabBar::tab { 
                padding: 8px 12px; 
                font-size: 12px; 
                color: white; 
                background-color: #3c3c3c; 
                border-top-left-radius: 5px; 
                border-top-right-radius: 5px; 
                margin-right: 2px; 
            }
            QTabBar::tab:selected { 
                background-color: #4CAF50; 
                font-weight: bold; 
            }
            QTabBar::tab:hover { 
                background-color: #555; 
            }
        """)

        tools_tab = QWidget()
        tools_layout = QVBoxLayout(tools_tab)
        tools_layout.setSpacing(5)

        design_group = QGroupBox("🔧 Design Tools")
        design_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        design_layout = QVBoxLayout()
        design_layout.setSpacing(3)

        tools = [
            ("🔍 Select", "select", "1"),
            ("🏃 Player", "player", "2"),
            ("🧱 Platform", "platform", "3"),
            ("👾 Enemy", "enemy", "4"),
            ("💎 Item", "collectible", "5"),
            ("🚩 Spawn", "spawn", "6"),
        ]

        for text, tool, shortcut in tools:
            btn = QPushButton(f"{text} ({shortcut})")
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px;
                    font-size: 12px;
                    color: white;
                    background-color: #4a4a4a;
                    border: 1px solid #666;
                    border-radius: 5px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
                QPushButton:pressed {
                    background-color: #4CAF50;
                }
            """)
            btn.clicked.connect(lambda checked, t=tool: self.set_tool(t))
            design_layout.addWidget(btn)

        grid_layout = QHBoxLayout()
        self.grid_check = QCheckBox("Grid")
        self.grid_check.setChecked(True)
        self.grid_check.setStyleSheet("color: white; font-size: 12px;")
        self.grid_check.stateChanged.connect(
            lambda: setattr(self.editor_canvas, 'show_grid', self.grid_check.isChecked())
        )
        grid_layout.addWidget(self.grid_check)

        self.snap_check = QCheckBox("Snap")
        self.snap_check.setChecked(True)
        self.snap_check.setStyleSheet("color: white; font-size: 12px;")
        self.snap_check.stateChanged.connect(
            lambda: setattr(self.editor_canvas, 'snap_to_grid', self.snap_check.isChecked())
        )
        grid_layout.addWidget(self.snap_check)
        design_layout.addLayout(grid_layout)

        design_group.setLayout(design_layout)
        tools_layout.addWidget(design_group)

        self.props_group = QGroupBox("📋 Properties")
        self.props_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        self.props_layout = QFormLayout()
        self.props_layout.setSpacing(3)

        spin_style = """
            QSpinBox, QDoubleSpinBox {
                padding: 4px;
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #3c3c3c;
                color: white;
                font-size: 11px;
                min-width: 70px;
                max-width: 100px;
            }
        """

        self.prop_x = QSpinBox();
        self.prop_x.setRange(0, 5000);
        self.prop_x.valueChanged.connect(self.on_property_changed);
        self.prop_x.setStyleSheet(spin_style)
        self.props_layout.addRow("X:", self.prop_x)
        self.prop_y = QSpinBox();
        self.prop_y.setRange(0, 5000);
        self.prop_y.valueChanged.connect(self.on_property_changed);
        self.prop_y.setStyleSheet(spin_style)
        self.props_layout.addRow("Y:", self.prop_y)
        self.prop_width = QSpinBox();
        self.prop_width.setRange(10, 2000);
        self.prop_width.valueChanged.connect(self.on_property_changed);
        self.prop_width.setStyleSheet(spin_style)
        self.props_layout.addRow("W:", self.prop_width)
        self.prop_height = QSpinBox();
        self.prop_height.setRange(10, 2000);
        self.prop_height.valueChanged.connect(self.on_property_changed);
        self.prop_height.setStyleSheet(spin_style)
        self.props_layout.addRow("H:", self.prop_height)

        self.prop_ai_type = QComboBox()
        self.prop_ai_type.addItems(["patrol", "chase", "static", "jumper"])
        self.prop_ai_type.currentTextChanged.connect(self.on_property_changed)
        self.props_layout.addRow("AI Type:", self.prop_ai_type)

        self.prop_detection_range = QSpinBox()
        self.prop_detection_range.setRange(0, 1000)
        self.prop_detection_range.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Detection:", self.prop_detection_range)

        self.prop_chase_speed = QDoubleSpinBox()
        self.prop_chase_speed.setRange(0, 1000)
        self.prop_chase_speed.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Chase Spd:", self.prop_chase_speed)

        self.prop_speed = QDoubleSpinBox()
        self.prop_speed.setRange(0, 1000)
        self.prop_speed.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Speed:", self.prop_speed)

        self.prop_patrol_range = QSpinBox()
        self.prop_patrol_range.setRange(0, 2000)
        self.prop_patrol_range.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Patrol Rng:", self.prop_patrol_range)

        self.prop_damage = QSpinBox()
        self.prop_damage.setRange(0, 1000)
        self.prop_damage.valueChanged.connect(self.on_property_changed)
        self.props_layout.addRow("Damage:", self.prop_damage)

        self.btn_color = QPushButton("🎨 Color")
        self.btn_color.clicked.connect(self.change_color)
        self.btn_color.setStyleSheet(
            "QPushButton { padding: 6px; background-color: #4a4a4a; color: white; border: 1px solid #666; border-radius: 5px; font-size: 12px; } QPushButton:hover { background-color: #5a5a5a; }")
        self.props_layout.addRow(self.btn_color)

        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_delete.setStyleSheet(
            "QPushButton { padding: 6px; background-color: #c0392b; color: white; border: none; border-radius: 5px; font-size: 12px; font-weight: bold; } QPushButton:hover { background-color: #e74c3c; }")
        self.props_layout.addRow(self.btn_delete)

        self.props_group.setLayout(self.props_layout)
        tools_layout.addWidget(self.props_group)

        self.tab_widget.addTab(tools_tab, "🔧")

        self.player_config = PlayerConfigWidget()
        self.tab_widget.addTab(self.player_config, "🏃")

        self.game_config = GameConfigWidget()
        self.tab_widget.addTab(self.game_config, "⚙️")

        left_layout.addWidget(self.tab_widget)

        control_layout = QVBoxLayout()
        control_layout.setSpacing(5)

        self.btn_play = QPushButton("▶ PLAY")
        self.btn_play.setStyleSheet(
            "QPushButton { padding: 12px; background-color: #4CAF50; color: white; font-weight: bold; font-size: 14px; border: none; border-radius: 8px; } QPushButton:hover { background-color: #45a049; } QPushButton:pressed { background-color: #2E7D32; }")
        self.btn_play.clicked.connect(self.start_game)
        control_layout.addWidget(self.btn_play)

        save_load_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾");
        self.btn_save.clicked.connect(self.save_level)
        self.btn_save.setStyleSheet(
            "QPushButton { padding: 8px; background-color: #3498db; color: white; font-weight: bold; border: none; border-radius: 5px; } QPushButton:hover { filter: brightness(110%); }")
        save_load_layout.addWidget(self.btn_save)

        self.btn_load = QPushButton("📂");
        self.btn_load.clicked.connect(self.load_level)
        self.btn_load.setStyleSheet(
            "QPushButton { padding: 8px; background-color: #2ecc71; color: white; font-weight: bold; border: none; border-radius: 5px; } QPushButton:hover { filter: brightness(110%); }")
        save_load_layout.addWidget(self.btn_load)

        self.btn_clear = QPushButton("🗑️");
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_clear.setStyleSheet(
            "QPushButton { padding: 8px; background-color: #e67e22; color: white; font-weight: bold; border: none; border-radius: 5px; } QPushButton:hover { filter: brightness(110%); }")
        save_load_layout.addWidget(self.btn_clear)

        control_layout.addLayout(save_load_layout)
        left_layout.addLayout(control_layout)

        objects_group = QGroupBox("📦 Objects")
        objects_group.setStyleSheet(
            "QGroupBox { color: white; font-size: 13px; font-weight: bold; border: 2px solid #555; border-radius: 8px; margin-top: 10px; padding-top: 20px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        objects_layout = QVBoxLayout()

        self.objects_list = QListWidget()
        self.objects_list.itemClicked.connect(self.select_from_list)
        self.objects_list.setStyleSheet(
            "QListWidget { background-color: #3c3c3c; color: white; border: 1px solid #555; border-radius: 5px; font-size: 11px; } QListWidget::item { padding: 4px; border-bottom: 1px solid #555; } QListWidget::item:selected { background-color: #4CAF50; }")
        self.objects_list.setMaximumHeight(300)
        objects_layout.addWidget(self.objects_list)

        objects_group.setLayout(objects_layout)
        left_layout.addWidget(objects_group)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            "padding: 8px; background-color: #333; color: white; border-radius: 5px; font-size: 11px;")
        left_layout.addWidget(self.status_label)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet("QScrollArea { border: none; background-color: #2b2b2b; }")
        left_scroll.setWidget(left_panel)
        self.left_scroll = left_scroll

        splitter.addWidget(left_scroll)

        self.editor_canvas = EditorCanvas()
        self.editor_canvas.parent_widget = self
        self.editor_canvas.engine.template = template
        self.editor_canvas.setStyleSheet("background-color: #1e1e1e;")
        splitter.addWidget(self.editor_canvas)

        splitter.setSizes([280, 1120])

        main_layout.addWidget(splitter)

        self.game_config.load_from_engine(self.editor_canvas.engine)

        self.update_properties()
        self.load_default_scene()

    def toggle_panel(self):
        left_panel = self.left_scroll.widget()
        if not self.panel_collapsed:
            self.collapsed_size = left_panel.width()
            left_panel.setMinimumWidth(30)
            left_panel.setMaximumWidth(30)
            self.collapse_btn.setText("▶")
            self.panel_collapsed = True
        else:
            left_panel.setMinimumWidth(200)
            left_panel.setMaximumWidth(500)
            total = self.splitter.sizes()[0] + self.splitter.sizes()[1]
            self.splitter.setSizes([self.collapsed_size, total - self.collapsed_size])
            self.collapse_btn.setText("◀")
            self.panel_collapsed = False

    def set_tool(self, tool):
        self.editor_canvas.current_tool = tool
        tool_names = {"select": "Select", "player": "Add Player", "platform": "Add Platform", "enemy": "Add Enemy",
                      "collectible": "Add Item", "spawn": "Add Spawn Point"}
        self.status_label.setText(f"🔧 Tool: {tool_names.get(tool, tool)} | Click on canvas to place")

    def load_default_scene(self):
        if self.template == "platformer":
            ground = Platform(0, 550, 3000, 50)
            ground.color = QColor(100, 80, 60)
            self.editor_canvas.engine.add_object(ground)

            platforms = [(192, 416, 256, 32), (512, 320, 256, 32), (800, 352, 256, 32), (1088, 256, 256, 32),
                         (1408, 416, 256, 32), (320, 224, 192, 32), (960, 160, 192, 32)]
            for x, y, w, h in platforms:
                self.editor_canvas.engine.add_object(Platform(x, y, w, h))

            spawn = SpawnPoint(96, 490)
            self.editor_canvas.engine.add_object(spawn)

            self.editor_canvas.engine.add_object(Player(96, 490))

            enemy1 = Enemy(608, 280)
            enemy1.properties['ai_type'] = 'chase'
            enemy1.properties['detection_range'] = 250
            enemy1.properties['chase_speed'] = 180
            self.editor_canvas.engine.add_object(enemy1)

            enemy2 = Enemy(1152, 216)
            enemy2.properties['ai_type'] = 'jumper'
            self.editor_canvas.engine.add_object(enemy2)

            enemy3 = Enemy(352, 184)
            enemy3.properties['ai_type'] = 'patrol'
            self.editor_canvas.engine.add_object(enemy3)

            coin_positions = [(160, 520), (224, 520), (288, 520), (352, 520), (416, 520), (480, 520), (544, 520),
                              (608, 520), (672, 520), (736, 520), (224, 386), (288, 386), (352, 386), (544, 290),
                              (608, 290), (672, 290), (832, 322), (896, 322), (960, 322), (1120, 226), (1184, 226),
                              (352, 194), (416, 194), (992, 130), (1056, 130)]
            for x, y in coin_positions:
                self.editor_canvas.engine.add_object(Collectible(x, y))

            health = Collectible(1504, 386)
            health.properties['type'] = 'health'
            health.properties['value'] = 30
            self.editor_canvas.engine.add_object(health)

            powerup = Collectible(1024, 226)
            powerup.properties['type'] = 'powerup'
            powerup.properties['value'] = 50
            self.editor_canvas.engine.add_object(powerup)

        elif self.template == "rpg":
            spawn = SpawnPoint(400, 300)
            self.editor_canvas.engine.add_object(spawn)
            self.editor_canvas.engine.add_object(Player(400, 300))
            for i in range(3):
                self.editor_canvas.engine.add_object(Enemy(200 + i * 200, 400))
            for i in range(5):
                self.editor_canvas.engine.add_object(Collectible(100 + i * 150, 200))

        elif self.template == "simple":
            spawn = SpawnPoint(100, 100)
            self.editor_canvas.engine.add_object(spawn)
            self.editor_canvas.engine.add_object(Player(100, 100))
            self.editor_canvas.engine.add_object(Enemy(400, 300))
            for i in range(5):
                self.editor_canvas.engine.add_object(Collectible(200 + i * 100, 200))

        self.update_object_list()
        self.editor_canvas.update()

    def update_properties(self):
        obj = self.editor_canvas.selected_object
        is_enemy = bool(obj and obj.tag == "enemy")

        self.prop_ai_type.setVisible(is_enemy)
        self.prop_detection_range.setVisible(is_enemy)
        self.prop_chase_speed.setVisible(is_enemy)
        self.prop_speed.setVisible(is_enemy)
        self.prop_patrol_range.setVisible(is_enemy)
        self.prop_damage.setVisible(is_enemy)

        for widget in [self.prop_x, self.prop_y, self.prop_width, self.prop_height,
                       self.btn_color, self.btn_delete]:
            widget.setEnabled(obj is not None)

        if not obj:
            self.props_group.setTitle("📋 Properties (None)")
            return

        self.props_group.setTitle(f"📋 Properties: {obj.tag}")

        self.prop_x.setEnabled(True);
        self.prop_y.setEnabled(True)
        self.prop_width.setEnabled(True);
        self.prop_height.setEnabled(True)
        self.btn_color.setEnabled(True);
        self.btn_delete.setEnabled(True)

        for widget, value in [(self.prop_x, obj.x), (self.prop_y, obj.y),
                              (self.prop_width, obj.width), (self.prop_height, obj.height)]:
            widget.blockSignals(True)
            widget.setValue(int(value))
            widget.blockSignals(False)

        if is_enemy:
            self.prop_ai_type.setCurrentText(obj.properties.get('ai_type', 'patrol'))
            self.prop_detection_range.setValue(obj.properties.get('detection_range', 200))
            self.prop_chase_speed.setValue(obj.properties.get('chase_speed', 150))
            self.prop_speed.setValue(obj.properties.get('speed', 100))
            self.prop_patrol_range.setValue(obj.properties.get('patrol_range', 100))
            self.prop_damage.setValue(obj.properties.get('damage', 20))

    def on_property_changed(self):
        obj = self.editor_canvas.selected_object
        if not obj:
            return

        sender = self.sender()

        if sender == self.prop_x:
            obj.x = self.prop_x.value()
        elif sender == self.prop_y:
            obj.y = self.prop_y.value()
        elif sender == self.prop_width:
            obj.width = self.prop_width.value()
        elif sender == self.prop_height:
            obj.height = self.prop_height.value()
        elif sender == self.prop_ai_type:
            obj.properties['ai_type'] = self.prop_ai_type.currentText()
        elif sender == self.prop_detection_range:
            obj.properties['detection_range'] = self.prop_detection_range.value()
        elif sender == self.prop_chase_speed:
            obj.properties['chase_speed'] = self.prop_chase_speed.value()
        elif sender == self.prop_speed:
            obj.properties['speed'] = self.prop_speed.value()
        elif sender == self.prop_patrol_range:
            obj.properties['patrol_range'] = self.prop_patrol_range.value()
        elif sender == self.prop_damage:
            obj.properties['damage'] = self.prop_damage.value()

        self.editor_canvas.update()

    def change_color(self):
        obj = self.editor_canvas.selected_object
        if obj:
            color = QColorDialog.getColor(obj.color, self)
            if color.isValid():
                obj.color = color
                self.editor_canvas.update()

    def delete_selected(self):
        if self.editor_canvas.selected_object:
            self.editor_canvas.engine.remove_object(self.editor_canvas.selected_object)
            self.editor_canvas.selected_object = None
            self.update_properties()
            self.update_object_list()
            self.editor_canvas.update()

    def update_object_list(self):
        self.objects_list.clear()
        for obj in self.editor_canvas.engine.game_objects:
            self.objects_list.addItem(f"{obj.tag} ({obj.__class__.__name__}) - ({int(obj.x)}, {int(obj.y)})")

    def select_from_list(self, item):
        index = self.objects_list.row(item)
        if 0 <= index < len(self.editor_canvas.engine.game_objects):
            self.editor_canvas.selected_object = self.editor_canvas.engine.game_objects[index]
            self.update_properties()
            self.editor_canvas.update()

    def start_game(self):
        if not any(obj.tag == "player" for obj in self.editor_canvas.engine.game_objects):
            QMessageBox.warning(self, "Error", "Please add a Player first!")
            return

        try:
            player = self.editor_canvas.engine.player
            if player:
                self.player_config.apply_to_player(player)
            self.game_config.apply_to_engine(self.editor_canvas.engine)

            self.editor_state = self.editor_canvas.engine.to_dict()
            game_data = self.editor_canvas.engine.to_dict()

            self.game_window = GameWindow(game_data, self)
            self.game_window.show()

            self.status_label.setText("🎮 Game running in separate window...")
            self.btn_play.setEnabled(False)
            self.btn_play.setText("Game Running...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start game:\n{str(e)}")
            if hasattr(self, 'editor_state'):
                self.editor_canvas.engine.from_dict(self.editor_state)
            self.btn_play.setEnabled(True)
            self.btn_play.setText("▶ PLAY")

    def on_game_window_closed(self):
        self.game_window = None
        self.btn_play.setEnabled(True)
        self.btn_play.setText("▶ PLAY")
        self.status_label.setText("Editor Mode - Game window closed")

        if hasattr(self, 'editor_state'):
            self.editor_canvas.engine.from_dict(self.editor_state)
            self.update_properties()
            self.update_object_list()
            self.editor_canvas.update()

    def save_level(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Level", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'w') as f:
                json.dump(self.editor_canvas.engine.to_dict(), f, indent=2)
            self.status_label.setText(f"✅ Saved to {filename}")

    def load_level(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Level", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.editor_canvas.engine.from_dict(data)
            self.editor_canvas.selected_object = None
            self.update_properties()
            self.update_object_list()
            self.editor_canvas.update()
            self.status_label.setText(f"📂 Loaded from {filename}")

    def clear_all(self):
        reply = QMessageBox.question(self, "Clear All", "Are you sure you want to clear everything?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.editor_canvas.engine.reset()
            self.editor_canvas.selected_object = None
            self.update_properties()
            self.update_object_list()
            self.editor_canvas.update()
            self.status_label.setText("🗑️ All objects cleared")

    def keyPressEvent(self, event):
        shortcuts = {Qt.Key.Key_1: "select", Qt.Key.Key_2: "player", Qt.Key.Key_3: "platform", Qt.Key.Key_4: "enemy",
                     Qt.Key.Key_5: "collectible", Qt.Key.Key_6: "spawn"}
        if event.key() in shortcuts:
            self.set_tool(shortcuts[event.key()])
        super().keyPressEvent(event)


class GameLauncher:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')

        self.app.setStyleSheet(
            "QMainWindow { background-color: #2b2b2b; } QToolTip { background-color: #333; color: white; border: 1px solid #555; padding: 5px; font-size: 12px; }")

        dialog = TemplateDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template = dialog.selected_template
            self.window = MainWindow(template)
            self.window.show()
            sys.exit(self.app.exec())


def main():
    GameLauncher()


if __name__ == "__main__":
    main()
