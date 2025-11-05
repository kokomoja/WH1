import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "driver": os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}"),
    "server": os.getenv("DB_SERVER", "localhost,1433"),
    "database": os.getenv("DB_NAME", "wh1Db"),
    "uid": os.getenv("DB_USER", "sa"),
    "pwd": os.getenv("DB_PASS", ""),
}

FONTS = [p for p in [
    os.getenv("FONT_1", "fonts/THSarabunNew.ttf"),
    os.getenv("FONT_2", "fonts/THSarabunNew-Bold.ttf"),
    os.getenv("FONT_3", "fonts/THSarabunNew-Italic.ttf"),
    os.getenv("FONT_4", "fonts/THSarabunNew-BoldItalic.ttf"),
] if p]

APP_STYLESHEET = """
QWidget {
    background-color: #fafafa;
    color: #222;
    font-family: 'THSarabunNew', 'Tahoma';
    font-size: 18px;           /* ✅ ลดขนาดฟอนต์ widget ทั่วไป */
}

/* ✅ ปุ่มทั่วไป */
QPushButton {
    background-color: #ffffff;
    border: 0.5px solid #bdbdbd;
    border-radius: 6px;
    padding: 4px 10px;         /* ✅ ปรับ padding เล็กลง */
    font-size: 24px;           /* ✅ ลดขนาดข้อความในปุ่ม */
    color: #222;
}
QPushButton:hover {
    background-color: #f0f0f0;
    border: 1px solid #9e9e9e;
}
QPushButton:pressed {
    background-color: #e0e0e0;
    border: 1px solid #757575;
}
QPushButton:disabled {
    background-color: #eeeeee;
    color: #999999;
    border: 1px solid #cccccc;
}

/* ✅ ปุ่มหลัก (เช่น Export, Save) */
QPushButton#primary {
    background-color: #1976d2;
    color: white;
    border: 1px solid #1565c0;
    font-size: 20px;           /* ✅ ขนาดเล็กลงเล็กน้อย */
}
QPushButton#primary:hover {
    background-color: #1565c0;
}
QPushButton#primary:pressed {
    background-color: #0d47a1;
}

/* ✅ ช่องกรอกข้อมูล */
QLineEdit, QComboBox, QDateEdit, QTimeEdit {
    border: 1px solid #bdbdbd;
    border-radius: 4px;
    padding: 3px;              /* ✅ ช่องกรอกเล็กลง */
    background-color: white;
    font-size: 14px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
    border: 1px solid #1976d2;
}

/* ✅ ตาราง */
QTableWidget {
    border: 1px solid #bdbdbd;
    gridline-color: #bdbdbd;
    background-color: #ffffff;
    alternate-background-color: #f7f7f7;
    font-size: 16px;         /* ✅ ข้อความในตารางเล็กลง */
}
QHeaderView::section {
    background-color: #e0e0e0;
    padding: 3px;
    border: 1px solid #bdbdbd;
    font-weight: bold;
    font-size: 16px;
}
"""