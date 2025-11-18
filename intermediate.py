from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from oil_report1 import OilReportForm
from menu import MenuWindow


class IntermediateDialog(QDialog):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Warehouse 1 | หน้ากลางก่อนเข้าสู่เมนูหลัก")
        self.resize(800, 500)
        self.username = username

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        lbl = QLabel(f"👋 ยินดีต้อนรับ: {username}")
        lbl.setFont(QFont("THSarabunNew-Bold", 32))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("margin-bottom:20px;")
        layout.addWidget(lbl)

        buttons = [
            ("🛢️ บันทึกรับ–จ่ายน้ำมัน", self.open_oil_report),
            ("➡ บันทึกการทำงาน FM-OP-01", self.open_menu),
            ("🚪 ออกจากโปรแกรม", self.close_dialog),
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("THSarabunNew-Bold", 24))
            btn.setMinimumHeight(60)

            # ✅ กำหนดขนาดฟอนต์ตรงนี้บังคับ override stylesheet เดิม
            if "🚪" in text:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color:#ff6666; 
                        color:white; 
                        font-weight:bold; 
                        border-radius:6px;
                        font-size:24px;
                        font-family:'THSarabunNew-Bold';
                    }
                    QPushButton:hover { background-color:#ff4c4c; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color:#fff;
                        border:0.5px solid #bdbdbd;
                        border-radius:6px;
                        padding:8px 16px;
                        font-size:24px;
                        font-family:'THSarabunNew-Bold';
                    }
                    QPushButton:hover { background-color:#f0f0f0; }
                """)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        # ✅ ล้าง stylesheet ที่ถูกตั้งจาก app.py
        self.setStyleSheet("")

    def open_oil_report(self):
        self.oil_window = OilReportForm(parent=None)
        self.oil_window.setWindowFlags(Qt.Window)
        self.oil_window.show()
        self.oil_window.raise_()
        self.oil_window.activateWindow()

    def open_menu(self):
        self.menu_window = MenuWindow(self.username)
        self.menu_window.setWindowFlags(Qt.Window)
        self.menu_window.show()

    def close_dialog(self):
        """ปิดเฉพาะหน้าต่าง intermediate"""
        self.close()