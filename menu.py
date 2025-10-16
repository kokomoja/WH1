from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication
from main import MainForm
from wh1_report import ReportWindow

class MenuWindow(QMainWindow):
    def __init__(self, username: str):
        super().__init__()
        self.setWindowTitle(f"Warehouse 1 | FM-OP-01 | เมนูหลัก ({username})")
        self.resize(800, 500)
        self.username = username

        # --- Layout ---
        central = QWidget()
        layout = QVBoxLayout(central)
        self.setCentralWidget(central)

        # ข้อความต้อนรับ
        lbl = QLabel(f"👋 ยินดีต้อนรับ: {username}")
        lbl.setFont(QFont("TH Sarabun New", 18, QFont.Bold))
        lbl.setStyleSheet("margin:10px;")
        layout.addWidget(lbl)

        # ปุ่มเปิดหน้าฟอร์ม CRUD
        btn_main = QPushButton("📋 บันทึก/แก้ไขข้อมูล (FM-OP-01)")
        btn_main.clicked.connect(self.open_main_form)
        layout.addWidget(btn_main)

        # ปุ่มเปิดรายงาน
        btn_report = QPushButton("📊 รายงาน / ค้นหา / Export Excel")
        btn_report.clicked.connect(self.open_report)
        layout.addWidget(btn_report)

        # ปุ่มออกจากระบบ
        btn_logout = QPushButton("🚪 ออกจากระบบ")
        btn_logout.setStyleSheet("background-color:#ff6666; color:white; font-weight:bold;")
        btn_logout.clicked.connect(self.logout)
        layout.addWidget(btn_logout)

        # ตัวแปรหน้าต่าง
        self.main_window = None
        self.report_window = None

    def open_main_form(self):
        """เปิดฟอร์ม CRUD เป็นหน้าต่างแยก"""
        self.main_window = MainForm()
        self.main_window.show()

    def open_report(self):
        """เปิดหน้ารายงาน"""
        if self.report_window is None:
            self.report_window = ReportWindow(self)
        self.report_window.show()
        self.report_window.raise_()

    def logout(self):
        """ปุ่มออกจากระบบ"""
        reply = QMessageBox.question(
            self, "ยืนยันการออกจากระบบ",
            "คุณต้องการออกจากระบบหรือไม่?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QCoreApplication.quit()  # ✅ ปิดทั้งโปรแกรมทั้งหมด
