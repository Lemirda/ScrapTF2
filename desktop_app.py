"""Модуль для создания графического интерфейса приложения"""
import sys
import os
import time
import asyncio

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QProgressBar, QFrame, QSizePolicy,
    QPushButton, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor

from db_manager import RaffleDatabase
import main

COLORS = {
    'background': QColor(18, 18, 18),
    'card_bg': QColor(30, 30, 30),
    'text': QColor(240, 240, 240),
    'text_secondary': QColor(180, 180, 180),
    'accent': QColor(75, 107, 251),
    'success': QColor(75, 225, 140),
    'warning': QColor(255, 170, 0),
    'danger': QColor(255, 88, 88),
    'chart_grid': QColor(60, 60, 60),
    'nav_bg': QColor(25, 25, 25),
    'nav_active': QColor(40, 40, 40)
}


class ConsoleOutput(QObject):
    """Класс для перенаправления вывода консоли"""
    text_written = pyqtSignal(str)

    def write(self, text):
        if text.strip():
            self.text_written.emit(text.strip())

    def flush(self):
        pass


class MainWorker(QThread):
    """Рабочий поток для запуска основного скрипта"""
    status_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        self.status_changed.emit("running")
        asyncio.run(main.main())
        self.status_changed.emit("stopped")

    def stop(self):
        self.running = False
        self.terminate()
        self.wait()


class RaffleStatsWorker(QThread):
    """Рабочий поток для сбора статистики раздач"""
    stats_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            db = RaffleDatabase()
            stats = db.get_stats()
            db.close()
            self.stats_updated.emit(stats)
            time.sleep(5)  # Обновление каждые 5 секунд

    def stop(self):
        self.running = False
        self.terminate()
        self.wait()


class ModernProgressBar(QProgressBar):
    """Современный стилизованный прогресс-бар"""

    def __init__(self, parent=None, color=COLORS['accent']):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setMaximumHeight(8)
        self.color = color
        self.apply_style()

    def apply_style(self):
        """Применение стилей к прогресс-бару"""
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['card_bg'].darker(120).name()};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {self.color.name()};
                border-radius: 4px;
            }}
        """)


class StatsCard(QFrame):
    """Карточка для отображения статистики"""

    def __init__(self, title, icon_text, color=COLORS['accent'], parent=None):
        super().__init__(parent)
        self.color = color
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.apply_style()
        self.create_layout(title, icon_text)

    def apply_style(self):
        """Применение стилей к карточке"""
        self.setStyleSheet(f"""
            StatsCard {{
                background-color: {COLORS['card_bg'].name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(150)

    def create_layout(self, title, icon_text):
        """Создание элементов карточки"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {COLORS['text_secondary'].name()}; font-size: 14px;")

        # Значение
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(
            f"color: {COLORS['text'].name()}; font-size: 24px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Дополнительная информация
        self.details_label = QLabel("")
        self.details_label.setStyleSheet(
            f"color: {COLORS['text_secondary'].name()}; font-size: 12px;")
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Прогресс-бар
        self.progress_bar = ModernProgressBar(color=self.color)

        # Иконка
        icon_label = self.create_icon_label(icon_text)

        # Верхняя часть с иконкой и заголовком
        header_layout = QHBoxLayout()
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label, 1)

        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addWidget(self.details_label)
        layout.addWidget(self.progress_bar)

    def create_icon_label(self, icon_text):
        """Создание иконки карточки"""
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
    """Счетчик для отображения статистики раздач"""

    def __init__(self, title, color=COLORS['accent'], parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.apply_style()
        self.create_layout(title, color)

    def apply_style(self):
        """Применение стилей к счетчику"""
        self.setStyleSheet(f"""
            StatsCounter {{
                background-color: {COLORS['card_bg'].name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)

    def create_layout(self, title, color):
        """Создание элементов счетчика"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {COLORS['text_secondary'].name()}; font-size: 14px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Значение
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(
            f"color: {color.name()}; font-size: 32px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)


class ModernConsole(QTextEdit):
    """Современная стилизованная консоль"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.auto_scroll = True
        self.apply_style()

    def apply_style(self):
        """Применение стилей к консоли"""
        # Базовый стиль консоли
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['card_bg'].darker(120).name()};
                color: {COLORS['text'].name()};
                border-radius: 10px;
                padding: 10px;
                border: none;
            }}
        """)

        # Стиль для полосы прокрутки
        scrollbar_style = f"""
            QScrollBar:vertical {{
                background-color: {COLORS['card_bg'].darker(120).name()};
                width: 14px;
                margin: 0px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['card_bg'].lighter(150).name()};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['accent'].name()};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """

        self.verticalScrollBar().setStyleSheet(scrollbar_style)

    def append(self, text):
        """Добавление текста с проверкой положения скроллбара"""
        # Проверяем, находится ли скроллбар внизу перед добавлением текста
        scrollbar = self.verticalScrollBar()
        at_bottom = scrollbar.value() >= scrollbar.maximum() - 10

        # Добавляем текст
        super().append(text)

        # Обновляем события, чтобы получить актуальное значение максимума скроллбара
        QApplication.processEvents()

        # Если скроллбар был внизу, прокручиваем вниз
        if at_bottom and self.auto_scroll:
            scrollbar.setValue(scrollbar.maximum())

    def showEvent(self, event):
        """Обработка события показа"""
        super().showEvent(event)
        if self.auto_scroll:
            QApplication.processEvents()
            scrollbar = self.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())


class NavButton(QPushButton):
    """Кнопка для навигации"""

    def __init__(self, text, icon_text="", parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_text = icon_text
        self.apply_style()

        # Если есть иконка, создаём кастомный макет
        if icon_text:
            self.create_icon_layout(icon_text)

    def apply_style(self):
        """Применение стилей к кнопке"""
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
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)

    def create_icon_layout(self, icon_text):
        """Создание макета с иконкой для кнопки"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)

        # Создаем метку для иконки
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet(f"""
            background-color: transparent;
            color: {COLORS['accent'].name()};
            font-size: 18px;
            padding: 0px;
        """)
        icon_label.setFixedWidth(25)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Создаем метку для текста
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

        # Переопределяем метод установки checked для обновления стилей дочерних виджетов
        original_set_checked = self.setChecked

        def new_set_checked(checked):
            original_set_checked(checked)
            if checked:
                icon_label.setStyleSheet(f"""
                    background-color: transparent;
                    color: {COLORS['accent'].name()};
                    font-size: 18px;
                    padding: 0px;
                """)
                text_label.setStyleSheet(f"""
                    background-color: transparent;
                    color: {COLORS['accent'].name()};
                    font-size: inherit;
                    font-weight: inherit;
                    padding: 0px;
                """)
            else:
                icon_label.setStyleSheet(f"""
                    background-color: transparent;
                    color: {COLORS['accent'].name()};
                    font-size: 18px;
                    padding: 0px;
                """)
                text_label.setStyleSheet(f"""
                    background-color: transparent;
                    color: {COLORS['text'].name()};
                    font-size: inherit;
                    font-weight: inherit;
                    padding: 0px;
                """)

        self.setChecked = new_set_checked

        # Инициализируем стили в соответствии с текущим состоянием
        if self.isChecked():
            text_label.setStyleSheet(f"""
                background-color: transparent;
                color: {COLORS['accent'].name()};
                font-size: inherit;
                font-weight: inherit;
                padding: 0px;
            """)
        else:
            text_label.setStyleSheet(f"""
                background-color: transparent;
                color: {COLORS['text'].name()};
                font-size: inherit;
                font-weight: inherit;
                padding: 0px;
            """)


class ScrapTFApp(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_workers()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Настройка основного окна
        self.setWindowTitle("ScrapTF Raffles")
        self.setMinimumSize(1200, 800)
        self.load_icon()
        self.setup_dark_theme()

        # Создание центрального виджета и основного макета
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Создание интерфейса
        self.create_ui()

    def load_icon(self):
        """Загрузка иконки приложения"""
        # Сначала пробуем найти иконку в той же папке, где и исполняемый файл
        icon_path = os.path.join(os.path.dirname(sys.executable if getattr(
            sys, 'frozen', False) else __file__), "icon.ico")

        # Если файл не найден, ищем в родительской директории
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(os.path.dirname(
                sys.executable if getattr(sys, 'frozen', False) else __file__)), "icon.ico")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("[Система] Иконка приложения не найдена:", icon_path)

    def init_workers(self):
        """Инициализация рабочих потоков"""
        # Перенаправление вывода консоли
        self.console_output = ConsoleOutput()
        self.console_output.text_written.connect(self.update_console)
        sys.stdout = self.console_output

        # Рабочие потоки
        self.main_worker = None
        self.raffle_stats_worker = RaffleStatsWorker()
        self.raffle_stats_worker.stats_updated.connect(
            self.update_raffle_stats)
        self.raffle_stats_worker.start()

        # Запуск основного скрипта
        self.start_main_script()

        # Вывод начального сообщения
        print("[Система] Приложение запущено")

    def setup_dark_theme(self):
        """Установка темной темы для всего приложения"""
        app = QApplication.instance()
        palette = QPalette()

        palette.setColor(QPalette.ColorRole.Window, COLORS['background'])
        palette.setColor(QPalette.ColorRole.WindowText, COLORS['text'])
        palette.setColor(QPalette.ColorRole.Base, COLORS['card_bg'])
        palette.setColor(QPalette.ColorRole.AlternateBase,
                         COLORS['card_bg'].darker(120))
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
        """Создание пользовательского интерфейса"""
        # Создаем навигационную панель и контент
        self.create_nav_panel()
        self.create_content_area()

        # Добавляем компоненты в основной макет
        self.main_layout.addWidget(self.nav_panel)
        self.main_layout.addWidget(self.content_container, 1)

    def create_nav_panel(self):
        """Создание левой навигационной панели"""
        self.nav_panel = QFrame()
        self.nav_panel.setStyleSheet(f"""
            background-color: {COLORS['nav_bg'].name()};
            border-right: 1px solid {COLORS['card_bg'].lighter(120).name()};
        """)
        self.nav_panel.setFixedWidth(220)

        # Макет для навигационной панели
        nav_layout = QVBoxLayout(self.nav_panel)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(10)

        # Заголовок приложения
        app_title = QLabel("ScrapTF Raffles")
        app_title.setStyleSheet(f"""
            color: {COLORS['text'].name()};
            font-size: 18px;
            font-weight: bold;
            padding-bottom: 15px;
        """)
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(app_title)

        # Навигационные кнопки
        self.home_btn = NavButton("Главная")
        self.home_btn.setChecked(True)
        self.home_btn.clicked.connect(lambda: self.switch_page(0))

        self.logs_btn = NavButton("Логи")
        self.logs_btn.clicked.connect(lambda: self.switch_page(1))

        # Добавляем кнопки в навигационную панель
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.logs_btn)
        nav_layout.addStretch()

        # Версия приложения внизу
        version_label = QLabel("v1.0")
        version_label.setStyleSheet(
            f"color: {COLORS['text_secondary'].name()}; font-size: 12px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(version_label)

    def create_content_area(self):
        """Создание основной области контента"""
        # Контейнер для контента
        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Стек для переключения между страницами
        self.pages_stack = QStackedWidget()

        # Создание страниц
        self.create_home_page()
        self.create_logs_page()

        # Добавляем страницы в стек
        self.pages_stack.addWidget(self.home_page)
        self.pages_stack.addWidget(self.logs_page)

        content_layout.addWidget(self.pages_stack)

    def create_home_page(self):
        """Создание главной страницы"""
        self.home_page = QWidget()
        home_layout = QVBoxLayout(self.home_page)
        home_layout.setContentsMargins(0, 0, 0, 0)
        home_layout.setSpacing(20)

        # Заголовок страницы
        home_header = QLabel("Общая статистика")
        home_header.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COLORS['text'].name()};")
        home_layout.addWidget(home_header)

        # Счетчики статистики
        stats_cards = QHBoxLayout()

        # Карточка с общей статистикой
        total_card = StatsCard("Всего раздач", "📊", COLORS['accent'])
        self.total_counter = total_card.value_label
        stats_cards.addWidget(total_card)

        # Карточка с обработанными раздачами
        processed_card = StatsCard("Обработано раздач", "✅", COLORS['success'])
        self.processed_counter = processed_card.value_label
        stats_cards.addWidget(processed_card)

        # Карточка с ожидающими раздачами
        unprocessed_card = StatsCard(
            "Ожидают обработки", "⏳", COLORS['warning'])
        self.unprocessed_counter = unprocessed_card.value_label
        stats_cards.addWidget(unprocessed_card)

        home_layout.addLayout(stats_cards)

        # Дополнительная статистика
        additional_stats_header = QLabel("Дополнительная статистика")
        additional_stats_header.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {COLORS['text'].name()};")
        home_layout.addWidget(additional_stats_header)

        # Здесь можно добавить графики или другие элементы статистики
        stats_placeholder = QFrame()
        stats_placeholder.setFrameShape(QFrame.Shape.StyledPanel)
        stats_placeholder.setStyleSheet(f"""
            background-color: {COLORS['card_bg'].name()};
            border-radius: 10px;
            min-height: 300px;
        """)
        home_layout.addWidget(stats_placeholder, 1)

    def create_logs_page(self):
        """Создание страницы логов"""
        self.logs_page = QWidget()
        logs_layout = QVBoxLayout(self.logs_page)
        logs_layout.setContentsMargins(0, 0, 0, 0)
        logs_layout.setSpacing(10)

        # Заголовок страницы
        logs_header = QLabel("Логи операций")
        logs_header.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COLORS['text'].name()};")
        logs_layout.addWidget(logs_header)

        # Консоль для логов
        self.console = ModernConsole()
        logs_layout.addWidget(self.console, 1)

    def switch_page(self, page_index):
        """Переключение между страницами"""
        self.pages_stack.setCurrentIndex(page_index)

        # Обновляем состояние кнопок
        self.home_btn.setChecked(page_index == 0)
        self.logs_btn.setChecked(page_index == 1)

    def update_console(self, text):
        """Обновление консоли"""
        # Определяем цвет текста в зависимости от содержимого
        color = COLORS['text'].name()
        if "ошибка" in text.lower() or "error" in text.lower():
            color = COLORS['danger'].name()
        elif "успешно" in text.lower() or "success" in text.lower():
            color = COLORS['success'].name()
        elif "предупреждение" in text.lower() or "warning" in text.lower():
            color = COLORS['warning'].name()
        elif "[система]" in text.lower():
            color = COLORS['accent'].name()

        # Добавляем текст с форматированием
        self.console.append(f'<span style="color:{color};">{text}</span>')

    def update_raffle_stats(self, stats):
        """Обновление статистики раздач"""
        self.total_counter.setText(str(stats['total']))
        self.processed_counter.setText(str(stats['processed']))
        self.unprocessed_counter.setText(str(stats['unprocessed']))

    def start_main_script(self):
        """Запуск основного скрипта"""
        if self.main_worker is None or not self.main_worker.isRunning():
            self.main_worker = MainWorker()
            self.main_worker.status_changed.connect(self.update_script_status)
            self.main_worker.start()

    def update_script_status(self, status):
        """Обновление статуса скрипта"""
        if status == "running":
            print("[Система] Основной скрипт запущен")
        else:
            print("[Система] Основной скрипт остановлен")

    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        # Остановка рабочих потоков
        if self.main_worker and self.main_worker.isRunning():
            self.main_worker.stop()

        if self.raffle_stats_worker.isRunning():
            self.raffle_stats_worker.stop()

        # Восстановление стандартного вывода
        sys.stdout = sys.__stdout__

        super().closeEvent(event)

    def showEvent(self, event):
        """Обработка события показа окна"""
        super().showEvent(event)
        # Обновляем интерфейс при показе окна
        QApplication.processEvents()

        # Обновляем скроллбар консоли
        if hasattr(self, 'console'):
            scrollbar = self.console.verticalScrollBar()
            if self.console.auto_scroll:
                scrollbar.setValue(scrollbar.maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ScrapTFApp()
    window.show()
    sys.exit(app.exec())
