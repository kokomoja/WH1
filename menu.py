from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication
from fmop01 import MainForm
from wh1_report import WH1ReportForm

class MenuWindow(QMainWindow):
    def __init__(self, username: str):
        super().__init__()
        self.setWindowTitle(f"Warehouse 1 | FM-OP-01 | เมนูหลัก ({username})")
        self.resize(800, 500)
        self.username = username

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)
        self.setCentralWidget(central)

        lbl = QLabel(f"👋 ยินดีต้อนรับ: {username}")
        lbl.setFont(QFont("THSarabunNew-Bold", 32))
        lbl.setStyleSheet("margin-bottom:20px;")
        layout.addWidget(lbl)

        buttons = [
            ("📋 บันทึก/แก้ไขข้อมูล (FM-OP-01)", self.open_main_form),
            ("📊 รายงาน / ค้นหา / Export Excel/PDF", self.open_report),
            ("🧾 เพิ่มการแก้ไขหมายเลขเอกสาร", self.open_edit_docno),
            ("🚪 ออกจากโปรแกรม", self.close_window),
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("THSarabunNew-Bold", 24))
            btn.setMinimumHeight(60)
            if "🚪" in text:
                btn.setStyleSheet("background-color:#ff6666; color:white; font-weight:bold;")
            btn.clicked.connect(handler)
            layout.addWidget(btn)

    def bring_to_front(self, w):
        w.show()
        w.raise_()
        w.activateWindow()

    def open_main_form(self):
        if not hasattr(self, 'main_window') or self.main_window is None:
            self.main_window = MainForm()
        self.bring_to_front(self.main_window)

    def open_report(self):
        if not hasattr(self, 'report_window') or self.report_window is None:
            self.report_window = WH1ReportForm()
        self.bring_to_front(self.report_window)

    def open_edit_docno(self):
        from edit_docno import EditDocNoWindow
        self.edit_docno_window = EditDocNoWindow()
        self.bring_to_front(self.edit_docno_window)

#    def logout(self):
#        reply = QMessageBox.question(self, "ยืนยันการออกจากระบบ", "คุณต้องการออกจากระบบหรือไม่?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#        if reply == QMessageBox.Yes:
#            QCoreApplication.quit()
            
    def get_menu_button_font(self):
        """ส่งคืนฟอนต์ของปุ่มในหน้าเมนูหลัก"""
        sample_btn = self.findChildren(QPushButton)[0]
        return sample_btn.font()
    
    def close_window(self):
        """ปิดเฉพาะหน้าต่างเมนูหลัก"""
        self.close()