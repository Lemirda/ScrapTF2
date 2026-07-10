TRANSLATIONS = {
    'en': {
        'select_language': 'Select Language',
        'login_to_steam': 'Login to Steam',
        'login_description': 'Please log in to your Steam account on scrap.tf',
        'done': 'Done',
        'scan_parameters': 'Scan Parameters',
        'wait_section': 'Waiting',
        'scan_delay_min': 'Min Scan Delay',
        'scan_delay_max': 'Max Scan Delay',
        'wait_minutes_min': 'Min Wait Time',
        'wait_minutes_max': 'Max Wait Time',
        'scan_delay_min_desc': 'Minimum seconds after opening a page so all elements '
                               '(buttons, data) fully load before the bot acts.',
        'scan_delay_max_desc': 'Maximum seconds after opening a page so all elements '
                               '(buttons, data) fully load before the bot acts.',
        'wait_minutes_min_desc': 'Minimum minutes to wait after joining all raffles before '
                                 'returning, refreshing the page and joining again — mimics a real human.',
        'wait_minutes_max_desc': 'Maximum minutes to wait after joining all raffles before '
                                 'returning, refreshing the page and joining again — mimics a real human.',
        'relogin': 'Switch Account',
        'total': 'Total',
        'processed': 'Processed',
        'pending': 'Pending',
        'state_starting': 'Starting...',
        'state_scanning': 'Scanning...',
        'state_processing': 'Processing...',
        'state_waiting': 'Waiting',
        'state_stopped': 'Stopped',
        'step_scan': 'Scan',
        'step_process': 'Process',
        'step_wait': 'Waiting',
        'nav_status': 'Dashboard',
        'nav_settings': 'Settings',
    },
    'ru': {
        'select_language': 'Выберите язык',
        'login_to_steam': 'Вход в Steam',
        'login_description': 'Пожалуйста, войдите в свой аккаунт Steam на сайте scrap.tf',
        'done': 'Готово',
        'scan_parameters': 'Параметры сканирования',
        'wait_section': 'Ожидание',
        'scan_delay_min': 'Мин. задержка сканирования',
        'scan_delay_max': 'Макс. задержка сканирования',
        'wait_minutes_min': 'Мин. время ожидания',
        'wait_minutes_max': 'Макс. время ожидания',
        'scan_delay_min_desc': 'Минимальное время в секундах после открытия страницы, чтобы все элементы '
                               '(кнопки, данные) успели полностью загрузиться, прежде чем бот начнёт действовать.',
        'scan_delay_max_desc': 'Максимальное время в секундах после открытия страницы, чтобы все элементы '
                               '(кнопки, данные) успели полностью загрузиться, прежде чем бот начнёт действовать.',
        'wait_minutes_min_desc': 'Минимальное время в минутах ожидания после вступления во все розыгрыши, '
                                 'прежде чем вернуться, обновить страницу и войти снова — '
                                 'имитация поведения реального человека.',
        'wait_minutes_max_desc': 'Максимальное время в минутах ожидания после вступления во все розыгрыши, '
                                 'прежде чем вернуться, обновить страницу и войти снова — '
                                 'имитация поведения реального человека.',
        'relogin': 'Сменить аккаунт',
        'total': 'Всего',
        'processed': 'Обработано',
        'pending': 'Ожидают',
        'state_starting': 'Запускается...',
        'state_scanning': 'Сканирование...',
        'state_processing': 'Обработка...',
        'state_waiting': 'Ожидание',
        'state_stopped': 'Остановлено',
        'step_scan': 'Скан',
        'step_process': 'Обраб',
        'step_wait': 'Ожидание',
        'nav_status': 'Панель',
        'nav_settings': 'Настройки',
    }
}


def get_text(key, language='en'):
    return TRANSLATIONS.get(language, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))
