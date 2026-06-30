import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSizePolicy, QPushButton, QStackedWidget,
    QSpinBox, QGroupBox, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QPalette, QColor
from ui.styles import COLORS
from ui.workers import MainWorker, RaffleStatsWorker, LoginWorker
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
                color: {COLORS['text'].name()};
                border: none;
                border-radius: 10px;
                font-size: 24px;
            }}
            QPushButton:checked {{
                background-color: {COLORS['accent'].name()};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {COLORS['nav_active'].name()};
            }}
        """)


class StatusCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            StatusCard {{
                background-color: {COLORS['card_bg'].name()};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet(f"""
            color: {COLORS['text_secondary'].name()};
            font-size: 24px;
        """)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.status_indicator.setGraphicsEffect(self.opacity_effect)
        header_layout.addWidget(self.status_indicator)
        
        self.state_label = QLabel("")
        self.state_label.setStyleSheet(f"""
            color: {COLORS['text_secondary'].name()};
            font-size: 20px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.state_label, 1)
        
        self.percentage_label = QLabel("")
        self.percentage_label.setStyleSheet(f"""
            color: {COLORS['accent'].name()};
            font-size: 18px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.percentage_label)
        
        layout.addLayout(header_layout)
        
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg'].darker(150).name()};
                border-radius: 4px;
            }}
        """)
        self.progress_bar_layout = QHBoxLayout(self.progress_bar)
        self.progress_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_bar_layout.setSpacing(0)
        
        self.progress_fill = QFrame()
        self.progress_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['accent'].name()};
                border-radius: 4px;
            }}
        """)
        self.progress_bar_layout.addWidget(self.progress_fill)
        
        layout.addWidget(self.progress_bar)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.processed_label = QLabel("")
        self.processed_label.setStyleSheet(f"""
            color: {COLORS['success'].name()};
            font-size: 13px;
        """)
        stats_layout.addWidget(self.processed_label)
        
        self.failed_label = QLabel("")
        self.failed_label.setStyleSheet(f"""
            color: {COLORS['danger'].name()};
            font-size: 13px;
        """)
        stats_layout.addWidget(self.failed_label)
        
        self.remaining_label = QLabel("")
        self.remaining_label.setStyleSheet(f"""
            color: {COLORS['text_secondary'].name()};
            font-size: 13px;
        """)
        stats_layout.addWidget(self.remaining_label)
        
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        self.pulse_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.pulse_animation.setDuration(1500)
        self.pulse_animation.setStartValue(1.0)
        self.pulse_animation.setEndValue(0.3)
        self.pulse_animation.setLoopCount(-1)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        
        self.progress_animation = QPropertyAnimation(self.progress_fill, b"maximumWidth")
        self.progress_animation.setDuration(500)
        self.progress_animation.setStartValue(0)
        self.progress_animation.setEndValue(0)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.current_color = COLORS['text_secondary']

    def set_state(self, state, color):
        self.current_color = color
        self.status_indicator.setStyleSheet(f"""
            color: {color.name()};
            font-size: 24px;
        """)
        self.state_label.setStyleSheet(f"""
            color: {color.name()};
            font-size: 20px;
            font-weight: bold;
        """)
        self.progress_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {color.name()};
                border-radius: 4px;
            }}
        """)
        self.percentage_label.setStyleSheet(f"""
            color: {color.name()};
            font-size: 18px;
            font-weight: bold;
        """)
        
        if state == 'scanning':
            self.pulse_animation.start()
            self.percentage_label.setText("")
            self.processed_label.setText("")
            self.failed_label.setText("")
            self.remaining_label.setText("")
            self.progress_animation.stop()
            self.progress_fill.setFixedWidth(0)
        elif state == 'processing':
            self.pulse_animation.start()
        else:
            self.pulse_animation.stop()
            self.progress_animation.stop()
            self.opacity_effect.setOpacity(1.0)
            self.progress_fill.setFixedWidth(0)
            self.percentage_label.setText("")

    def update_progress(self, current, total, processed, failed):
        if total == 0:
            return
        
        percentage = int((current / total) * 100)
        self.percentage_label.setText(f"{percentage}%")
        
        self.processed_label.setText(f"✓ {processed}")
        self.failed_label.setText(f"✗ {failed}")
        self.remaining_label.setText(f"Осталось: {total - current}")
        
        self.progress_animation.stop()
        self.progress_animation.setStartValue(self.progress_fill.width())
        max_width = self.progress_bar.width()
        target_width = int(max_width * percentage / 100)
        self.progress_animation.setEndValue(target_width)
        self.progress_animation.start()


class StatsCounter(QFrame):
    def __init__(self, title, color=COLORS['accent'], parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.apply_style()
        self.create_layout(title, color)

    def apply_style(self):
        self.setStyleSheet(f"""
            StatsCounter {{
                background-color: {COLORS['card_bg'].name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def create_layout(self, title, color):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['text_secondary'].name()}; font-size: 12px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(f"color: {color.name()}; font-size: 24px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
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
        ru_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card_bg'].name()};
                color: {COLORS['text'].name()};
                border: 2px solid {COLORS['accent'].name()};
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent'].name()};
            }}
        """)
        ru_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ru_button.clicked.connect(lambda: self.select_language('ru'))
        buttons_layout.addWidget(ru_button)

        en_button = QPushButton("🇺🇸  English")
        en_button.setFixedSize(200, 80)
        en_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card_bg'].name()};
                color: {COLORS['text'].name()};
                border: 2px solid {COLORS['accent'].name()};
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent'].name()};
            }}
        """)
        en_button.setCursor(Qt.CursorShape.PointingHandCursor)
        en_button.clicked.connect(lambda: self.select_language('en'))
        buttons_layout.addWidget(en_button)

        layout.addLayout(buttons_layout)

    def select_language(self, lang):
        self.db.set_setting('language', lang)
        self.window().show_login_screen()


class LoginScreen(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.login_worker = None
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
                background-color: {COLORS['accent'].name()};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
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
        self.start_login()

    def start_login(self):
        if self.login_worker is None or not self.login_worker.isRunning():
            profile_path = get_profile_path()
            self.login_worker = LoginWorker(profile_path)
            self.login_worker.login_finished.connect(self.on_login_finished)
            self.login_worker.start()

    def on_done_clicked(self):
        self.db.set_setting('logged_in', '1')
        if self.login_worker and self.login_worker.isRunning():
            self.login_worker.stop()
            self.login_worker.wait()
        self.window().show_main_app()

    def on_login_finished(self):
        pass

    def closeEvent(self, event):
        if self.login_worker and self.login_worker.isRunning():
            self.login_worker.stop()
        super().closeEvent(event)


class SettingCard(QFrame):
    def __init__(self, icon, title, description, spinbox, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            SettingCard {{
                background-color: {COLORS['card_bg'].darker(120).name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            color: {COLORS['accent'].name()};
            font-size: 28px;
            padding: 10px;
            background-color: {COLORS['accent'].darker(300).name()};
            border-radius: 10px;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(50, 50)
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['text'].name()};
            font-size: 16px;
            font-weight: bold;
        """)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            color: {COLORS['text_secondary'].name()};
            font-size: 12px;
        """)
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout, 1)
        
        spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['card_bg'].name()};
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['card_bg'].lighter(150).name()};
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 80px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px;
                height: 0px;
            }}
        """)
        spinbox.setFixedSize(100, 45)
        layout.addWidget(spinbox)


class SettingsPanel(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.save_button = None
        self.cards = []
        self.create_ui()

    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        lang = self.db.get_setting('language') or 'en'

        self.scan_delay_min = QSpinBox()
        self.scan_delay_min.setRange(1, 60)
        self.scan_delay_min.setValue(int(float(self.db.get_setting('scan_delay_min'))))
        
        self.scan_delay_max = QSpinBox()
        self.scan_delay_max.setRange(1, 60)
        self.scan_delay_max.setValue(int(float(self.db.get_setting('scan_delay_max'))))
        
        self.wait_minutes_min = QSpinBox()
        self.wait_minutes_min.setRange(1, 60)
        self.wait_minutes_min.setValue(int(self.db.get_setting('wait_minutes_min')))
        
        self.wait_minutes_max = QSpinBox()
        self.wait_minutes_max.setRange(1, 60)
        self.wait_minutes_max.setValue(int(self.db.get_setting('wait_minutes_max')))

        card1 = SettingCard(
            "⏱",
            get_text('scan_delay_min', lang),
            get_text('scan_delay_min_desc', lang),
            self.scan_delay_min
        )
        self.cards.append(card1)
        layout.addWidget(card1)

        card2 = SettingCard(
            "⏱",
            get_text('scan_delay_max', lang),
            get_text('scan_delay_max_desc', lang),
            self.scan_delay_max
        )
        self.cards.append(card2)
        layout.addWidget(card2)

        card3 = SettingCard(
            "⏳",
            get_text('wait_minutes_min', lang),
            get_text('wait_minutes_min_desc', lang),
            self.wait_minutes_min
        )
        self.cards.append(card3)
        layout.addWidget(card3)

        card4 = SettingCard(
            "⏳",
            get_text('wait_minutes_max', lang),
            get_text('wait_minutes_max_desc', lang),
            self.wait_minutes_max
        )
        self.cards.append(card4)
        layout.addWidget(card4)

        layout.addSpacing(10)

        self.save_button = QPushButton(get_text('save_settings', lang))
        self.save_button.setFixedSize(200, 50)
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent'].name()};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent'].darker(120).name()};
            }}
        """)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        lang = self.db.get_setting('language') or 'en'
        if self.save_button:
            self.save_button.setText(get_text('save_settings', lang))
        if self.cards:
            keys = [
                ('scan_delay_min', 'scan_delay_min_desc'),
                ('scan_delay_max', 'scan_delay_max_desc'),
                ('wait_minutes_min', 'wait_minutes_min_desc'),
                ('wait_minutes_max', 'wait_minutes_max_desc'),
            ]
            for i, card in enumerate(self.cards):
                if i < len(keys):
                    title_key, desc_key = keys[i]
                    layout = card.layout()
                    if layout and layout.count() >= 2:
                        text_layout = layout.itemAt(1).layout()
                        if text_layout and text_layout.count() >= 2:
                            title_label = text_layout.itemAt(0).widget()
                            desc_label = text_layout.itemAt(1).widget()
                            if title_label:
                                title_label.setText(get_text(title_key, lang))
                            if desc_label:
                                desc_label.setText(get_text(desc_key, lang))

    def save_settings(self):
        self.db.set_setting('scan_delay_min', str(self.scan_delay_min.value()))
        self.db.set_setting('scan_delay_max', str(self.scan_delay_max.value()))
        self.db.set_setting('wait_minutes_min', str(self.wait_minutes_min.value()))
        self.db.set_setting('wait_minutes_max', str(self.wait_minutes_max.value()))


class ScrapTF2App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = RaffleDatabase()
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
        logged_in = self.db.get_setting('logged_in')

        if not language:
            self.stack.setCurrentWidget(self.language_screen)
        elif logged_in != '1':
            self.show_login_screen()
        else:
            self.show_main_app()

    def show_login_screen(self):
        self.stack.setCurrentWidget(self.login_screen)

    def show_main_app(self):
        self.stack.setCurrentWidget(self.main_screen)
        self.init_workers()

    def create_main_screen(self):
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        self.status_page = self.create_status_page()
        self.settings_page = self.create_settings_page()

        self.content_stack.addWidget(self.status_page)
        self.content_stack.addWidget(self.settings_page)

        nav_frame = QFrame()
        nav_frame.setFixedWidth(70)
        nav_frame.setStyleSheet(f"background-color: {COLORS['nav_bg'].name()};")
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(10)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        status_btn = IconButton("📊")
        status_btn.setChecked(True)
        status_btn.clicked.connect(lambda: self.switch_page(0, status_btn))
        nav_layout.addWidget(status_btn)

        settings_btn = IconButton("⚙")
        settings_btn.clicked.connect(lambda: self.switch_page(1, settings_btn))
        nav_layout.addWidget(settings_btn)

        nav_layout.addStretch()

        main_layout.addWidget(nav_frame)

        return widget

    def create_settings_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(15)

        self.settings_panel = SettingsPanel(self.db)
        container_layout.addWidget(self.settings_panel)

        layout.addWidget(container)
        layout.addStretch()

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
        stats_frame.setStyleSheet(f"""
            background-color: {COLORS['card_bg'].name()};
            border-radius: 10px;
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 10, 15, 10)
        stats_layout.setSpacing(20)

        total_card = StatsCounter(get_text('total', lang), COLORS['accent'])
        self.total_counter = total_card.value_label
        stats_layout.addWidget(total_card)

        processed_card = StatsCounter(get_text('processed', lang), COLORS['success'])
        self.processed_counter = processed_card.value_label
        stats_layout.addWidget(processed_card)

        unprocessed_card = StatsCounter(get_text('pending', lang), COLORS['warning'])
        self.unprocessed_counter = unprocessed_card.value_label
        stats_layout.addWidget(unprocessed_card)

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

        app.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {COLORS['card_bg'].lighter(150).name()};
                border-radius: 10px;
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
            }}
        """)

    def init_workers(self):
        self.main_worker = None
        self.main_worker = MainWorker()
        self.main_worker.status_changed.connect(self.update_status)
        self.main_worker.start()

        self.raffle_stats_worker = RaffleStatsWorker()
        self.raffle_stats_worker.stats_updated.connect(self.update_raffle_stats)
        self.raffle_stats_worker.start()

        self.start_main_script()

    def animate_indicator(self):
        self.animation_step = (self.animation_step + 1) % 4
        opacity = [1.0, 0.6, 0.3, 0.6][self.animation_step]
        color = self.current_color
        
        r = int(color.red() * opacity)
        g = int(color.green() * opacity)
        b = int(color.blue() * opacity)
        
        self.status_indicator.setStyleSheet(f"""
            color: rgb({r}, {g}, {b});
            font-size: 24px;
        """)
        
        if self.progress_fill.width() > 0:
            max_width = self.progress_bar.width()
            progress_width = int(max_width * (self.animation_step + 1) / 4)
            self.progress_fill.setFixedWidth(progress_width)

    def set_state(self, state, color):
        self.current_color = color
        self.status_indicator.setStyleSheet(f"""
            color: {color.name()};
            font-size: 24px;
        """)
        self.state_label.setStyleSheet(f"""
            color: {color.name()};
            font-size: 20px;
            font-weight: bold;
        """)
        self.progress_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {color.name()};
                border-radius: 2px;
            }}
        """)
        
        if state in ['scanning', 'processing']:
            self.animation_timer.start(300)
        else:
            self.animation_timer.stop()
            self.progress_fill.setFixedWidth(0)

    def update_raffle_stats(self, stats):
        self.total_counter.setText(str(stats['total']))
        self.processed_counter.setText(str(stats['processed']))
        self.unprocessed_counter.setText(str(stats['unprocessed']))

    def update_status(self, status):
        state = status.get('state', '')
        lang = self.db.get_setting('language') or 'en'
        
        if not state:
            return
        
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
        elif state == 'stopped':
            self.status_card.state_label.setText(get_text('state_stopped', lang))
            self.status_card.set_state('stopped', COLORS['danger'])

    def start_main_script(self):
        if self.main_worker is None or not self.main_worker.isRunning():
            self.main_worker = MainWorker()
            self.main_worker.status_changed.connect(self.update_script_status)
            self.main_worker.start()

    def update_script_status(self, status):
        pass

    def closeEvent(self, event):
        if hasattr(self, 'main_worker') and self.main_worker and self.main_worker.isRunning():
            self.main_worker.stop()

        if hasattr(self, 'raffle_stats_worker') and self.raffle_stats_worker.isRunning():
            self.raffle_stats_worker.stop()

        if hasattr(self, 'login_screen') and self.login_screen.login_worker and self.login_screen.login_worker.isRunning():
            self.login_screen.login_worker.stop()

        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScrapTF2App()
    window.show()
    sys.exit(app.exec())
