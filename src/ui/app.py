# pylint: disable=too-many-lines
# This module holds all widgets, screens and the main window in one place.
# Splitting it into ui/widgets.py + ui/screens.py is a worthwhile future refactor.
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSizePolicy, QPushButton, QStackedWidget,
    QSpinBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QEasingCurve,
    QVariantAnimation, QPointF, QRectF
)
from PyQt6.QtGui import (
    QIcon, QPalette, QColor, QPainter, QPen, QFont,
    QLinearGradient, QRadialGradient
)
from ui.styles import COLORS, rgba
from ui.workers import AppWorker, RaffleStatsWorker
from ui.i18n import get_text
from config import get_application_path
from db.manager import RaffleDatabase
from browser.login import get_profile_path


class ModernProgressBar(QFrame):
    def __init__(self, parent=None, color=COLORS['accent']):
        super().__init__(parent)
        self.color = color
        self.setFixedHeight(8)
        self.setStyleSheet(f"""
            ModernProgressBar {{
                background-color: {COLORS['card_bg'].darker(120).name()};
                border-radius: 4px;
            }}
        """)
        self._value = 0
        self._max = 100

    def setMaximum(self, val):
        self._max = val

    def setValue(self, val):
        self._value = val
        if self._max > 0:
            pct = min(100, int(val / self._max * 100))
        else:
            pct = 0
        self.setStyleSheet(f"""
            ModernProgressBar {{
                background-color: {COLORS['card_bg'].darker(120).name()};
                border-radius: 4px;
                qproperty-value: {pct};
            }}
        """)


class StatsCard(QFrame):
    def __init__(self, title, icon_text, color=COLORS['accent'], parent=None):
        super().__init__(parent)
        self.color = color
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.apply_style()
        self.create_layout(title, icon_text)

    def apply_style(self):
        self.setStyleSheet(f"""
            StatsCard {{
                background-color: {COLORS['card_bg'].name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(150)

    def create_layout(self, title, icon_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['text_secondary'].name()}; font-size: 14px;")

        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(f"color: {COLORS['text'].name()}; font-size: 24px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.details_label = QLabel("")
        self.details_label.setStyleSheet(f"color: {COLORS['text_secondary'].name()}; font-size: 12px;")
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = ModernProgressBar(color=self.color)

        icon_label = self.create_icon_label(icon_text)

        header_layout = QHBoxLayout()
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label, 1)

        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addWidget(self.details_label)
        layout.addWidget(self.progress_bar)

    def create_icon_label(self, icon_text):
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet(f"""
            color: {self.color.name()};
            font-size: 20px;
            background-color: {self.color.darker(300).name()};
            border-radius: 20px;
            padding: 10px;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(40, 40)
        return icon_label


class IconButton(QPushButton):
    def __init__(self, icon_text, parent=None):
        super().__init__(icon_text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(50, 50)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['nav_bg'].name()};
                color: {COLORS['text_secondary'].name()};
                border: none;
                border-radius: 12px;
                font-size: 22px;
            }}
            QPushButton:checked {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['accent'].name()},
                    stop:1 {COLORS['accent2'].name()}
                );
                color: white;
            }}
            QPushButton:hover:!checked {{
                background-color: {COLORS['nav_active'].name()};
                color: {COLORS['text'].name()};
            }}
        """)


class SpinningLoader(QWidget):
    def __init__(self, parent=None, color=COLORS['accent']):
        super().__init__(parent)
        self.setFixedSize(44, 44)
        self._color = color
        self._angle = 0.0
        self._running = False

        self._rotation_anim = QVariantAnimation()
        self._rotation_anim.setDuration(1200)
        self._rotation_anim.setStartValue(0.0)
        self._rotation_anim.setEndValue(360.0)
        self._rotation_anim.setLoopCount(-1)
        self._rotation_anim.valueChanged.connect(self._on_rotate)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(16)
        glow.setColor(self._color)
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)
        self._glow = glow

    def _on_rotate(self, value):
        self._angle = value
        self.update()

    def set_color(self, color):
        self._color = color
        self._glow.setColor(color)
        self.update()

    def start(self):
        if not self._running:
            self._running = True
            self._rotation_anim.start()

    def stop(self):
        self._running = False
        self._rotation_anim.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2
        r = min(cx, cy) - 5

        pen = QPen(self._color, 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        painter.drawArc(QRectF(cx - r, cy - r, r * 2, r * 2), int(self._angle * 16), 280 * 16)


class StepTimeline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setMinimumWidth(200)
        self._active_step = -1
        self._completed_steps = set()
        self._color = COLORS['accent']
        self._lang = 'en'

    def set_language(self, lang):
        self._lang = lang
        self.update()

    def set_active(self, step_index, color):
        self._active_step = step_index
        self._color = color
        self.update()

    def mark_completed(self, step_index):
        self._completed_steps.add(step_index)
        self.update()

    def reset(self):
        self._active_step = -1
        self._completed_steps.clear()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        step_keys = ['step_scan', 'step_process', 'step_wait']
        labels = [get_text(k, self._lang) for k in step_keys]
        n = len(labels)
        step_w = self.width() / n
        cy = self.height() / 2

        for i, label in enumerate(labels):
            x = step_w * i
            cx = x + 14
            if i < n - 1:
                self._draw_connector(painter, i, cx, cy, step_w * (i + 1) + 14)
            self._draw_node(painter, i, cx, cy)
            self._draw_label(painter, i, label, QRectF(x, cy + 9, step_w, 14))

    def _draw_connector(self, painter, i, cx, cy, nx):
        alpha = 180 if i < self._active_step else 50
        lc = QColor(self._color if i < self._active_step else COLORS['text_secondary'])
        lc.setAlpha(alpha)
        pen = QPen(lc, 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(cx + 9, cy), QPointF(nx - 9, cy))

    def _draw_node(self, painter, i, cx, cy):
        if i in self._completed_steps:
            cc = COLORS['success']
            painter.setPen(QPen(cc, 2))
            painter.setBrush(cc)
            painter.drawEllipse(QPointF(cx, cy), 6, 6)
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawLine(QPointF(cx - 3, cy), QPointF(cx - 1, cy + 2))
            painter.drawLine(QPointF(cx - 1, cy + 2), QPointF(cx + 3, cy - 3))
        elif i == self._active_step:
            painter.setPen(QPen(self._color, 2.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), 8, 8)
            painter.setBrush(self._color)
            painter.drawEllipse(QPointF(cx, cy), 3.5, 3.5)
        else:
            painter.setPen(QPen(COLORS['text_secondary'], 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), 6, 6)

    def _draw_label(self, painter, i, label, rect):
        text_color = COLORS['text'] if i <= self._active_step else COLORS['text_secondary']
        painter.setPen(QPen(text_color, 1))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)


class GradientProgressBar(QWidget):
    def __init__(self, parent=None, color=COLORS['accent']):
        super().__init__(parent)
        self.setFixedHeight(10)
        self._color = color
        self._target_color = color
        self._start_color = color
        self._percentage = 0.0
        self._color_anim = QVariantAnimation()
        self._color_anim.setDuration(500)
        self._color_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._color_anim.valueChanged.connect(self._on_color_step)

        self._progress_anim = QVariantAnimation()
        self._progress_anim.setDuration(500)
        self._progress_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._progress_anim.valueChanged.connect(self._on_progress_step)

    def set_color(self, color):
        self._color_anim.stop()
        self._start_color = QColor(self._color)
        self._target_color = QColor(color)
        self._color_anim.setStartValue(0.0)
        self._color_anim.setEndValue(1.0)
        self._color_anim.start()

    def set_percentage(self, pct):
        self._progress_anim.stop()
        self._progress_anim.setStartValue(self._percentage)
        self._progress_anim.setEndValue(float(pct))
        self._progress_anim.start()

    def reset(self):
        self._progress_anim.stop()
        self._color_anim.stop()
        self._percentage = 0.0
        self.update()

    def _on_color_step(self, t):
        self._color = QColor(
            int(self._start_color.red() + (self._target_color.red() - self._start_color.red()) * t),
            int(self._start_color.green() + (self._target_color.green() - self._start_color.green()) * t),
            int(self._start_color.blue() + (self._target_color.blue() - self._start_color.blue()) * t)
        )
        self.update()

    def _on_progress_step(self, val):
        self._percentage = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(COLORS['card_bg'].darker(150))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 5, 5)

        if self._percentage <= 0:
            return

        fill_w = max(6, int(self.width() * self._percentage / 100.0))

        gradient = QLinearGradient(0, 0, fill_w, 0)
        gradient.setColorAt(0.0, self._color.darker(115))
        gradient.setColorAt(0.55, self._color)
        gradient.setColorAt(1.0, self._color.lighter(140))
        painter.setBrush(gradient)
        painter.drawRoundedRect(0, 0, fill_w, self.height(), 5, 5)

        glow = QRadialGradient(fill_w, self.height() / 2, 9)
        glow.setColorAt(0.0, QColor(self._color.red(), self._color.green(), self._color.blue(), 100))
        glow.setColorAt(1.0, QColor(self._color.red(), self._color.green(), self._color.blue(), 0))
        painter.setBrush(glow)
        painter.drawEllipse(QPointF(fill_w, self.height() / 2), 9, 9)


class StatusCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            StatusCard {{
                background-color: {COLORS['card_bg'].name()};
                border: 1px solid {COLORS['border'].name()};
                border-radius: 14px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.loader = SpinningLoader(self, COLORS['accent'])
        row1.addWidget(self.loader)

        self.state_label = QLabel("")
        self.state_label.setStyleSheet(f"color: {COLORS['text_secondary'].name()}; font-size: 20px; font-weight: bold;")
        row1.addWidget(self.state_label, 1)

        self.step_timeline = StepTimeline(self)
        row1.addWidget(self.step_timeline)

        layout.addLayout(row1)

        layout.addStretch(1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)

        self.progress_bar = GradientProgressBar(self, COLORS['accent'])
        row2.addWidget(self.progress_bar, 1)

        self.percentage_label = QLabel("")
        self.percentage_label.setStyleSheet(f"color: {COLORS['accent'].name()}; font-size: 18px; font-weight: bold;")
        self.percentage_label.setFixedWidth(50)
        self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row2.addWidget(self.percentage_label)

        layout.addLayout(row2)

        self.current_color = COLORS['text_secondary']
        self.current_state = ''
        self._lang = 'en'

        self._color_anim = QVariantAnimation()
        self._color_anim.setDuration(400)
        self._color_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._color_anim.valueChanged.connect(self._on_color_transition)

    def set_language(self, lang):
        self._lang = lang
        self.step_timeline.set_language(lang)

    def _on_color_transition(self, t):
        c = QColor(
            int(self._start_color.red() + (self._target_color.red() - self._start_color.red()) * t),
            int(self._start_color.green() + (self._target_color.green() - self._start_color.green()) * t),
            int(self._start_color.blue() + (self._target_color.blue() - self._start_color.blue()) * t)
        )
        self.state_label.setStyleSheet(f"color: {c.name()}; font-size: 20px; font-weight: bold;")
        self.percentage_label.setStyleSheet(f"color: {c.name()}; font-size: 18px; font-weight: bold;")
        self.loader.set_color(c)

    def set_state(self, state, color):
        self.current_state = state

        self._color_anim.stop()
        self._start_color = QColor(self.current_color)
        self._target_color = QColor(color)
        self._color_anim.setStartValue(0.0)
        self._color_anim.setEndValue(1.0)
        self._color_anim.start()
        self.current_color = color

        self.progress_bar.set_color(color)

        if state == 'scanning':
            self.progress_bar.reset()
            self.percentage_label.setText("")

            self.loader.start()
            self.step_timeline.reset()
            self.step_timeline.set_active(0, color)

        elif state == 'processing':
            self.loader.start()
            self.step_timeline.mark_completed(0)
            self.step_timeline.set_active(1, color)

        elif state == 'waiting':
            self.loader.stop()
            self.progress_bar.reset()
            self.percentage_label.setText("")
            self.step_timeline.mark_completed(0)
            self.step_timeline.mark_completed(1)
            self.step_timeline.set_active(2, color)

        else:
            self.loader.stop()
            self.progress_bar.reset()
            self.percentage_label.setText("")
            self.step_timeline.reset()

    def update_progress(self, current, total, processed, failed):
        if total == 0:
            return

        percentage = int((current / total) * 100)
        self.percentage_label.setText(f"{percentage}%")

        self.progress_bar.set_percentage(percentage)

        if current >= total:
            self.step_timeline.mark_completed(1)


class StatsCounter(QFrame):
    def __init__(self, title, color=COLORS['accent'], icon="", parent=None):
        super().__init__(parent)
        self.color = color
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.apply_style()
        self.create_layout(title, color, icon)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)

    def apply_style(self):
        self.setStyleSheet(f"""
            StatsCounter {{
                background-color: {COLORS['card_bg'].name()};
                border: 1px solid {COLORS['border'].name()};
                border-radius: 14px;
            }}
            StatsCounter:hover {{
                background-color: {COLORS['card_hover'].name()};
                border: 1px solid {self.color.name()};
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def create_layout(self, title, color, icon):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(10)

        self.icon_label = QLabel(icon)
        self.icon_label.setFixedSize(34, 34)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            background-color: {rgba(color, 0.16)};
            color: {color.name()};
            border-radius: 10px;
            font-size: 16px;
        """)
        header.addWidget(self.icon_label)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            f"color: {COLORS['text_secondary'].name()}; font-size: 12px; "
            f"font-weight: bold; letter-spacing: 0.5px;"
        )
        header.addWidget(self.title_label, 1)

        layout.addLayout(header)

        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(f"color: {color.name()}; font-size: 30px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.value_label)


class LanguageSelectionScreen(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.create_ui()

    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(get_text('select_language', 'en'))
        title.setStyleSheet(f"color: {COLORS['text'].name()}; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(40)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(40)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ru_button = QPushButton("🇷🇺  Русский")
        ru_button.setFixedSize(200, 80)
        ru_button.setStyleSheet(self._lang_button_style())
        ru_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ru_button.clicked.connect(lambda: self.select_language('ru'))
        buttons_layout.addWidget(ru_button)

        en_button = QPushButton("🇺🇸  English")
        en_button.setFixedSize(200, 80)
        en_button.setStyleSheet(self._lang_button_style())
        en_button.setCursor(Qt.CursorShape.PointingHandCursor)
        en_button.clicked.connect(lambda: self.select_language('en'))
        buttons_layout.addWidget(en_button)

        layout.addLayout(buttons_layout)

    def _lang_button_style(self):
        return f"""
            QPushButton {{
                background-color: {COLORS['card_bg'].name()};
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['border'].name()};
                border-radius: 14px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['card_hover'].name()};
                border: 2px solid {COLORS['accent'].name()};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent'].darker(115).name()};
            }}
        """

    def select_language(self, lang):
        self.db.set_setting('language', lang)
        self.window().start_app()


class LoginScreen(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.title_label = None
        self.desc_label = None
        self.done_button = None
        self.create_ui()

    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lang = self.db.get_setting('language') or 'en'

        self.title_label = QLabel(get_text('login_to_steam', lang))
        self.title_label.setStyleSheet(f"color: {COLORS['text'].name()}; font-size: 32px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        layout.addSpacing(20)

        self.desc_label = QLabel(get_text('login_description', lang))
        self.desc_label.setStyleSheet(f"color: {COLORS['text_secondary'].name()}; font-size: 16px;")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.desc_label)

        layout.addSpacing(40)

        self.done_button = QPushButton(get_text('done', lang))
        self.done_button.setFixedSize(200, 60)
        self.done_button.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['accent'].name()},
                    stop:1 {COLORS['accent2'].name()}
                );
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent'].lighter(110).name()};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent'].darker(120).name()};
            }}
        """)
        self.done_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.done_button.clicked.connect(self.on_done_clicked)
        layout.addWidget(self.done_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def showEvent(self, event):
        super().showEvent(event)
        lang = self.db.get_setting('language') or 'en'
        if self.title_label:
            self.title_label.setText(get_text('login_to_steam', lang))
        if self.desc_label:
            self.desc_label.setText(get_text('login_description', lang))
        if self.done_button:
            self.done_button.setText(get_text('done', lang))

    def on_done_clicked(self):
        self.window().app_worker.login_done()
        self.window().show_main_app()


class SectionHeader(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {COLORS['border'].name()}; border: none;")

        self.label = QLabel(text)
        self.label.setStyleSheet(
            f"color: {COLORS['text_secondary'].name()}; font-size: 12px; "
            f"font-weight: bold; letter-spacing: 0.5px;"
        )

        layout.addWidget(self.label)
        layout.addWidget(line, 1)

    def set_text(self, text):
        self.label.setText(text)


class SettingRow(QFrame):
    def __init__(self, title, description, spinbox, suffix="", parent=None):
        super().__init__(parent)
        self.setStyleSheet("SettingRow { background-color: transparent; border-radius: 6px; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(12)

        self.text_layout = QVBoxLayout()
        self.text_layout.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {COLORS['text'].name()}; font-size: 14px; font-weight: 600;")
        self.text_layout.addWidget(self.title_label)

        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet(f"color: {COLORS['text_secondary'].name()}; font-size: 11px;")
        self.desc_label.setWordWrap(True)
        self.text_layout.addWidget(self.desc_label)

        layout.addLayout(self.text_layout, 1)

        spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['card_bg'].darker(110).name()};
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['card_bg'].lighter(130).name()};
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 14px;
                font-weight: 600;
                min-width: 55px;
                max-width: 55px;
            }}
            QSpinBox:focus {{
                border-color: {COLORS['accent'].name()};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px;
                height: 0px;
            }}
        """)
        spinbox.setFixedSize(60, 34)
        layout.addWidget(spinbox)

        if suffix:
            suffix_label = QLabel(suffix)
            suffix_label.setStyleSheet(f"color: {COLORS['text_secondary'].name()}; font-size: 12px; font-weight: 600;")
            suffix_label.setFixedWidth(30)
            layout.addWidget(suffix_label)

    def set_texts(self, title, description):
        self.title_label.setText(title)
        self.desc_label.setText(description)


class SettingsPanel(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.rows = []
        self.create_ui()

    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        lang = self.db.get_setting('language') or 'en'

        self.scan_delay_min = QSpinBox()
        self.scan_delay_min.setRange(1, 60)
        self.scan_delay_min.setValue(int(float(self.db.get_setting('scan_delay_min'))))
        self.scan_delay_min.valueChanged.connect(self._on_setting_changed)

        self.scan_delay_max = QSpinBox()
        self.scan_delay_max.setRange(1, 60)
        self.scan_delay_max.setValue(int(float(self.db.get_setting('scan_delay_max'))))
        self.scan_delay_max.valueChanged.connect(self._on_setting_changed)

        self.wait_minutes_min = QSpinBox()
        self.wait_minutes_min.setRange(1, 60)
        self.wait_minutes_min.setValue(int(self.db.get_setting('wait_minutes_min')))
        self.wait_minutes_min.valueChanged.connect(self._on_setting_changed)

        self.wait_minutes_max = QSpinBox()
        self.wait_minutes_max.setRange(1, 60)
        self.wait_minutes_max.setValue(int(self.db.get_setting('wait_minutes_max')))
        self.wait_minutes_max.valueChanged.connect(self._on_setting_changed)

        lang_ru = self.db.get_setting('language') == 'ru'
        seconds_label = "сек" if lang_ru else "sec"
        minutes_label = "мин" if lang_ru else "min"

        self.scan_header = SectionHeader(get_text('scan_parameters', lang))
        layout.addWidget(self.scan_header)

        row1 = SettingRow(
            get_text('scan_delay_min', lang),
            get_text('scan_delay_min_desc', lang),
            self.scan_delay_min, seconds_label
        )
        self.rows.append(('scan_delay_min', 'scan_delay_min_desc', row1))
        layout.addWidget(row1)

        row2 = SettingRow(
            get_text('scan_delay_max', lang),
            get_text('scan_delay_max_desc', lang),
            self.scan_delay_max, seconds_label
        )
        self.rows.append(('scan_delay_max', 'scan_delay_max_desc', row2))
        layout.addWidget(row2)

        layout.addSpacing(8)

        self.wait_header = SectionHeader(get_text('wait_section', lang))
        layout.addWidget(self.wait_header)

        row3 = SettingRow(
            get_text('wait_minutes_min', lang),
            get_text('wait_minutes_min_desc', lang),
            self.wait_minutes_min, minutes_label
        )
        self.rows.append(('wait_minutes_min', 'wait_minutes_min_desc', row3))
        layout.addWidget(row3)

        row4 = SettingRow(
            get_text('wait_minutes_max', lang),
            get_text('wait_minutes_max_desc', lang),
            self.wait_minutes_max, minutes_label
        )
        self.rows.append(('wait_minutes_max', 'wait_minutes_max_desc', row4))
        layout.addWidget(row4)

        layout.addSpacing(8)

        saved_label = QLabel("")

        saved_label.setStyleSheet(f"color: {COLORS['success'].name()}; font-size: 12px;")
        saved_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        saved_label.setVisible(False)
        self._saved_label = saved_label
        layout.addWidget(saved_label)

        layout.addStretch(1)

        self.relogin_button = QLabel(self._relogin_html(lang))
        self.relogin_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.relogin_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.relogin_button.linkActivated.connect(self.relogin)
        layout.addWidget(self.relogin_button)

        layout.addSpacing(8)

        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self._do_save)

    def _relogin_html(self, lang):
        color = COLORS['danger'].darker(110).name()
        text = get_text('relogin', lang)
        return (
            f"<a href='#' style='color: {color}; text-decoration: none; "
            f"font-size: 12px;'>{text}</a>"
        )

    def _on_setting_changed(self):
        self._save_timer.start()

    def _do_save(self):
        self.db.set_setting('scan_delay_min', str(self.scan_delay_min.value()))
        self.db.set_setting('scan_delay_max', str(self.scan_delay_max.value()))
        self.db.set_setting('wait_minutes_min', str(self.wait_minutes_min.value()))
        self.db.set_setting('wait_minutes_max', str(self.wait_minutes_max.value()))
        if self._saved_label:
            lang = self.db.get_setting('language') or 'en'
            if lang == 'ru':
                self._saved_label.setText("Сохранено")
            else:
                self._saved_label.setText("Saved")
            self._saved_label.setVisible(True)
            QTimer.singleShot(1500, lambda: self._saved_label.setVisible(False))

    def showEvent(self, event):
        super().showEvent(event)
        lang = self.db.get_setting('language') or 'en'
        self.scan_header.set_text(get_text('scan_parameters', lang))
        self.wait_header.set_text(get_text('wait_section', lang))
        if self.relogin_button:
            self.relogin_button.setText(self._relogin_html(lang))
        keys = [
            ('scan_delay_min', 'scan_delay_min_desc'),
            ('scan_delay_max', 'scan_delay_max_desc'),
            ('wait_minutes_min', 'wait_minutes_min_desc'),
            ('wait_minutes_max', 'wait_minutes_max_desc'),
        ]
        for i, (title_key, desc_key, row) in enumerate(self.rows):
            if i < len(keys):
                row.set_texts(get_text(title_key, lang), get_text(desc_key, lang))

    def relogin(self):
        self.window().relogin_user()


class ScrapTF2App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = RaffleDatabase()
        self.app_worker = None
        self.raffle_stats_worker = None
        self.init_ui()
        self.check_initial_state()

    def init_ui(self):
        self.setWindowTitle("ScrapTF2")
        self.setMinimumSize(1200, 800)
        self.load_icon()
        self.setup_dark_theme()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.language_screen = LanguageSelectionScreen(self.db)
        self.login_screen = LoginScreen(self.db)
        self.main_screen = self.create_main_screen()

        self.stack.addWidget(self.language_screen)
        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.main_screen)

    def load_icon(self):
        icon_path = os.path.join(get_application_path(), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def check_initial_state(self):
        language = self.db.get_setting('language')

        if not language:
            self.stack.setCurrentWidget(self.language_screen)
        else:
            self.start_app()

    def start_app(self):
        self.app_worker = AppWorker(get_profile_path(), self.db)
        self.app_worker.status_changed.connect(self.update_status)
        self.app_worker.login_required.connect(self._on_login_required)
        self.app_worker.start()

        if self.db.get_setting('logged_in') == '1':
            self.show_main_app()
        else:
            self.show_login_screen()

    def _on_login_required(self):
        self.show_login_screen()

    def show_login_screen(self):
        self.stack.setCurrentWidget(self.login_screen)

    def show_main_app(self):
        self.refresh_ui_language()
        self.stack.setCurrentWidget(self.main_screen)

        if not self.raffle_stats_worker or not self.raffle_stats_worker.isRunning():
            self.raffle_stats_worker = RaffleStatsWorker()
            self.raffle_stats_worker.stats_updated.connect(self.update_raffle_stats)
            self.raffle_stats_worker.start()

    def refresh_ui_language(self):
        lang = self.db.get_setting('language') or 'en'

        self.stat_cards['total'].title_label.setText(get_text('total', lang))
        self.stat_cards['processed'].title_label.setText(get_text('processed', lang))
        self.stat_cards['unprocessed'].title_label.setText(get_text('pending', lang))

        self.status_card.set_language(lang)
        self.status_card.state_label.setText(get_text('state_starting', lang))

    def create_main_screen(self):
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        self.content_stack.addWidget(self.create_status_page())
        self.content_stack.addWidget(self.create_settings_page())

        lang = self.db.get_setting('language') or 'en'

        nav_frame = QFrame()
        nav_frame.setFixedWidth(74)
        nav_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['nav_bg'].name()};
                border-right: 1px solid {COLORS['border'].name()};
            }}
        """)
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(12, 16, 12, 16)
        nav_layout.setSpacing(12)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        status_btn = IconButton("📊")
        status_btn.setChecked(True)
        status_btn.setToolTip(get_text('nav_status', lang))
        status_btn.clicked.connect(lambda: self.switch_page(0, status_btn))
        nav_layout.addWidget(status_btn)

        settings_btn = IconButton("⚙")
        settings_btn.setToolTip(get_text('nav_settings', lang))
        settings_btn.clicked.connect(lambda: self.switch_page(1, settings_btn))
        nav_layout.addWidget(settings_btn)

        nav_layout.addStretch()

        main_layout.addWidget(nav_frame)

        return widget

    def create_settings_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.settings_panel = SettingsPanel(self.db)
        layout.addWidget(self.settings_panel)

        return widget

    def create_status_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(15)

        self.create_stats_section(container_layout)

        self.status_card = StatusCard()
        lang = self.db.get_setting('language') or 'en'
        self.status_card.state_label.setText(get_text('state_starting', lang))
        self.status_card.set_language(lang)
        self.status_card.loader.start()
        container_layout.addWidget(self.status_card)

        layout.addWidget(container)
        layout.addStretch()

        return widget

    def switch_page(self, index, button):
        self.content_stack.setCurrentIndex(index)
        for btn in self.sender().parent().findChildren(IconButton):
            btn.setChecked(False)
        button.setChecked(True)

    def create_stats_section(self, parent_layout):
        lang = self.db.get_setting('language') or 'en'

        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: transparent;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(16)

        self.stat_cards = {
            'total': StatsCounter(get_text('total', lang), COLORS['accent'], "\U0001F4E6"),
            'processed': StatsCounter(get_text('processed', lang), COLORS['success'], "✔"),
            'unprocessed': StatsCounter(get_text('pending', lang), COLORS['warning'], "⏳"),
        }
        for card in self.stat_cards.values():
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_frame)

    def setup_dark_theme(self):
        app = QApplication.instance()
        palette = QPalette()

        palette.setColor(QPalette.ColorRole.Window, COLORS['background'])
        palette.setColor(QPalette.ColorRole.WindowText, COLORS['text'])
        palette.setColor(QPalette.ColorRole.Base, COLORS['card_bg'])
        palette.setColor(QPalette.ColorRole.AlternateBase, COLORS['card_bg'].darker(120))
        palette.setColor(QPalette.ColorRole.ToolTipBase, COLORS['card_bg'])
        palette.setColor(QPalette.ColorRole.ToolTipText, COLORS['text'])
        palette.setColor(QPalette.ColorRole.Text, COLORS['text'])
        palette.setColor(QPalette.ColorRole.Button, COLORS['card_bg'])
        palette.setColor(QPalette.ColorRole.ButtonText, COLORS['text'])
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, COLORS['accent'])
        palette.setColor(QPalette.ColorRole.Highlight, COLORS['accent'])
        palette.setColor(QPalette.ColorRole.HighlightedText, COLORS['text'])

        app.setPalette(palette)

        bg = COLORS['background']
        bg_alt = COLORS['background_alt']
        app.setStyleSheet(f"""
            * {{
                font-family: "Segoe UI", "Inter", "Roboto", sans-serif;
            }}

            QMainWindow {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0.6, y2:1,
                    stop:0 {bg_alt.name()},
                    stop:1 {bg.name()}
                );
            }}

            QGroupBox {{
                border: 1px solid {COLORS['border'].name()};
                border-radius: 12px;
                margin-top: 10px;
                font-weight: bold;
                color: {COLORS['text'].name()};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }}

            QLabel {{
                color: {COLORS['text'].name()};
                background: transparent;
            }}

            QToolTip {{
                background-color: {COLORS['card_bg'].name()};
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['border_strong'].name()};
                border-radius: 6px;
                padding: 6px 9px;
                font-size: 12px;
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 2px 2px 2px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border_strong'].name()};
                border-radius: 5px;
                min-height: 32px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['accent'].name()};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

    def update_raffle_stats(self, stats):
        self.stat_cards['total'].value_label.setText(str(stats['total']))
        self.stat_cards['processed'].value_label.setText(str(stats['processed']))
        self.stat_cards['unprocessed'].value_label.setText(str(stats['unprocessed']))

    def update_status(self, status):
        state = status.get('state', '')
        lang = self.db.get_setting('language') or 'en'

        if not state:
            return

        self.status_card.set_language(lang)

        if state == 'scanning':
            self.status_card.state_label.setText(get_text('state_scanning', lang))
            self.status_card.set_state('scanning', COLORS['accent'])
        elif state == 'processing':
            current = status.get('current', 0)
            total = status.get('total', 0)
            processed = status.get('processed', 0)
            failed = status.get('failed', 0)

            self.status_card.state_label.setText(get_text('state_processing', lang))
            self.status_card.set_state('processing', COLORS['success'])
            self.status_card.update_progress(current, total, processed, failed)
        elif state == 'waiting':
            remaining = status.get('remaining', 0)
            minutes = remaining // 60
            seconds = remaining % 60
            label = f"{get_text('state_waiting', lang)} {minutes:02d}:{seconds:02d}"
            self.status_card.state_label.setText(label)
            self.status_card.set_state('waiting', COLORS['warning'])
        elif state == 'stopped':
            self.status_card.state_label.setText(get_text('state_stopped', lang))
            self.status_card.set_state('stopped', COLORS['danger'])

    def relogin_user(self):
        if self.raffle_stats_worker and self.raffle_stats_worker.isRunning():
            self.raffle_stats_worker.stop()

        if self.app_worker and self.app_worker.isRunning():
            self.app_worker.relogin()
            self.show_login_screen()

    def closeEvent(self, event):
        if self.app_worker and self.app_worker.isRunning():
            self.app_worker.stop()

        if self.raffle_stats_worker and self.raffle_stats_worker.isRunning():
            self.raffle_stats_worker.stop()

        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        QApplication.processEvents()


def main():
    app = QApplication(sys.argv)
    window = ScrapTF2App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
