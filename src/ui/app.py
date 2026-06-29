import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSizePolicy, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QTextCursor, QTextOption
from ui.styles import COLORS
from ui.workers import ConsoleOutput, MainWorker, RaffleStatsWorker
from config import get_application_path


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


class ModernConsole(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auto_scroll = True
        self.apply_style()
        self.create_layout()

    def apply_style(self):
        self.setStyleSheet(f"""
            ModernConsole {{
                background-color: {COLORS['card_bg'].darker(120).name()};
                border-radius: 10px;
            }}
            QTextEdit {{
                background-color: transparent;
                color: {COLORS['text'].name()};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                font-weight: 600;
                border: none;
            }}
        """)

    def create_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        layout.addWidget(self.text_edit)

    def append(self, text):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(text + "<br>")
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()


class NavButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_text = icon_text
        self.apply_style()

        if icon_text:
            self.create_icon_layout(icon_text)

    def apply_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['nav_bg'].name()};
                color: {COLORS['text'].name()};
                border: none;
                border-radius: 5px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:checked {{
                background-color: {COLORS['nav_active'].name()};
                color: {COLORS['accent'].name()};
                border-left: 3px solid {COLORS['accent'].name()};
            }}
            QPushButton:hover {{
                background-color: {COLORS['nav_active'].name()};
            }}
            QPushButton > QLabel {{
                background-color: transparent;
                color: inherit;
            }}
        """)
        self.setMinimumHeight(48)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def create_icon_layout(self, icon_text):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)

        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet(f"""
            background-color: transparent;
            color: {COLORS['accent'].name()};
            font-size: 18px;
            padding: 0px;
        """)
        icon_label.setFixedWidth(25)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_label = QLabel(self.text())
        text_label.setStyleSheet("""
            background-color: transparent;
            color: inherit;
            font-size: inherit;
            font-weight: inherit;
            padding: 0px;
        """)
        text_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()


class ScrapTFApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_workers()

    def init_ui(self):
        self.setWindowTitle("ScrapTF")
        self.setMinimumSize(1200, 800)
        self.load_icon()
        self.setup_dark_theme()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.create_ui()

    def load_icon(self):
        icon_path = os.path.join(get_application_path(), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("[Система] Иконка приложения не найдена:", icon_path)

    def init_workers(self):
        self.console_output = ConsoleOutput()
        self.console_output.text_written.connect(self.update_console)
        sys.stdout = self.console_output

        self.main_worker = None
        self.raffle_stats_worker = RaffleStatsWorker()
        self.raffle_stats_worker.stats_updated.connect(self.update_raffle_stats)
        self.raffle_stats_worker.start()

        self.start_main_script()

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

    def create_ui(self):
        self.create_main_content()

    def create_main_content(self):
        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        self.main_layout.addWidget(self.content_container, 1)

        self.create_stats_section(content_layout)
        self.create_logs_section(content_layout)

    def create_stats_section(self, parent_layout):
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            background-color: {COLORS['card_bg'].name()};
            border-radius: 10px;
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 10, 15, 10)
        stats_layout.setSpacing(20)

        total_card = StatsCounter("Всего", COLORS['accent'])
        self.total_counter = total_card.value_label
        stats_layout.addWidget(total_card)

        processed_card = StatsCounter("Обработано", COLORS['success'])
        self.processed_counter = processed_card.value_label
        stats_layout.addWidget(processed_card)

        unprocessed_card = StatsCounter("Ожидают", COLORS['warning'])
        self.unprocessed_counter = unprocessed_card.value_label
        stats_layout.addWidget(unprocessed_card)

        parent_layout.addWidget(stats_frame)

    def create_logs_section(self, parent_layout):
        self.console = ModernConsole()
        parent_layout.addWidget(self.console, 1)

    def update_console(self, text):
        color = COLORS['text'].name()
        if "ошибка" in text.lower() or "error" in text.lower():
            color = COLORS['danger'].name()
        elif "успешно" in text.lower() or "success" in text.lower():
            color = COLORS['success'].name()
        elif "предупреждение" in text.lower() or "warning" in text.lower():
            color = COLORS['warning'].name()
        elif "[система]" in text.lower():
            color = COLORS['accent'].name()

        escaped_text = text.replace("<", "&lt;").replace(">", "&gt;")
        self.console.append(f'<span style="color:{color};">{escaped_text}</span>')

    def update_raffle_stats(self, stats):
        self.total_counter.setText(str(stats['total']))
        self.processed_counter.setText(str(stats['processed']))
        self.unprocessed_counter.setText(str(stats['unprocessed']))

    def start_main_script(self):
        if self.main_worker is None or not self.main_worker.isRunning():
            self.main_worker = MainWorker()
            self.main_worker.status_changed.connect(self.update_script_status)
            self.main_worker.start()

    def update_script_status(self, status):
        pass

    def closeEvent(self, event):
        if self.main_worker and self.main_worker.isRunning():
            self.main_worker.stop()

        if self.raffle_stats_worker.isRunning():
            self.raffle_stats_worker.stop()

        sys.stdout = sys.__stdout__

        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScrapTFApp()
    window.show()
    sys.exit(app.exec())
