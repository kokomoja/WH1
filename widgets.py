# widgets.py
from PyQt5.QtWidgets import QComboBox

def create_static_combo(items, include_all_label=None):
    cb = QComboBox()
    if include_all_label:
        cb.addItem(include_all_label)
    cb.addItems(items)
    return cb
