from PyQt6.QtGui import QColor

COLORS = {
    # Base surfaces — deep, slightly blue-tinted dark
    'background': QColor(14, 15, 22),
    'background_alt': QColor(19, 21, 30),
    'card_bg': QColor(26, 28, 40),
    'card_hover': QColor(34, 37, 54),
    'border': QColor(46, 50, 72),
    'border_strong': QColor(64, 70, 100),

    # Text
    'text': QColor(236, 238, 246),
    'text_secondary': QColor(150, 155, 178),

    # Accent — blue-purple with a secondary stop for gradients
    'accent': QColor(124, 108, 255),
    'accent2': QColor(96, 138, 255),

    # Semantic
    'success': QColor(64, 214, 153),
    'warning': QColor(255, 182, 72),
    'danger': QColor(255, 96, 109),

    # Misc
    'chart_grid': QColor(50, 54, 76),
    'nav_bg': QColor(19, 20, 30),
    'nav_active': QColor(36, 39, 56),
}


def rgba(color, alpha):
    """Return a 'rgba(r, g, b, a)' CSS string for the given QColor and 0..1 alpha."""
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha})"
