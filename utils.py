# utils.py
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QLocale

def info(parent, title, text):
    QMessageBox.information(parent, title, text)

def warn(parent, title, text):
    QMessageBox.warning(parent, title, text)

def ask(parent, title, text) -> bool:
    return QMessageBox.question(
        parent, title, text, QMessageBox.Yes | QMessageBox.No
    ) == QMessageBox.Yes

def setup_dateedit(dateedit, format_str="yyyy-MM-dd"):
    """ตั้งค่า QDateEdit ให้ใช้เลขอารบิก และฟอร์แมตตามที่กำหนด"""
    locale = QLocale(QLocale.English, QLocale.UnitedStates)
    dateedit.setLocale(locale)
    dateedit.setDisplayFormat(format_str)
    return dateedit

def setup_timeedit(timeedit, format_str="HH:mm:ss"):
    """ตั้งค่า QTimeEdit ให้ใช้เลขอารบิก และ format ตามต้องการ"""
    from PyQt5.QtCore import QLocale
    locale = QLocale(QLocale.English, QLocale.UnitedStates)
    timeedit.setLocale(locale)
    timeedit.setDisplayFormat(format_str)
    return timeedit

def thai_to_arabic(text: str) -> str:
    """แปลงเลขไทยเป็นเลขอารบิก"""
    if not text:
        return ""
    trans = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")
    return str(text).translate(trans)

def confirm_dialog(parent, title, message) -> bool:
    reply = QMessageBox.question(
        parent, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    return reply == QMessageBox.Yes
