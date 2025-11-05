# edit_docno.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from db import list_revisions, insert_revision, update_revision, delete_revision
from utils import confirm_dialog
from datetime import date
from utils import thai_to_arabic
from utils import setup_dateedit

class EditDocNoWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧾 เพิ่ม/แก้ไขหมายเลขเอกสาร (WH1_Revision)")
        self.resize(800, 500)
        self.current_id = None

        layout = QVBoxLayout(self)

        lbl_header = QLabel("เพิ่ม / แก้ไข / ลบ ข้อมูลการแก้ไขหมายเลขเอกสาร")
        lbl_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_header)

        # ฟอร์มกรอกข้อมูล
        form = QHBoxLayout()
        self.ed_code = QLineEdit()
        self.ed_code.setPlaceholderText("ISO Code")
        self.ed_code.setFixedWidth(200)

        self.ed_rev = QLineEdit()
        self.ed_rev.setPlaceholderText("Revision")
        self.ed_rev.setFixedWidth(200)

        self.ed_eff = setup_dateedit(QDateEdit(calendarPopup=True), "yyyy-MM-dd")
        self.ed_eff.setDate(QDate.currentDate())
        self.ed_eff.setFixedWidth(150)

        self.btn_save = QPushButton("💾 บันทึก")
        self.btn_update = QPushButton("✏️ แก้ไข")
        self.btn_delete = QPushButton("🗑️ ลบ")
        self.btn_clear = QPushButton("🔄 เคลียร์")

        for b in [self.btn_save, self.btn_update, self.btn_delete, self.btn_clear]:
            b.setMinimumHeight(35)

        form.addWidget(self.ed_code)
        form.addWidget(self.ed_rev)
        form.addWidget(self.ed_eff)
        form.addWidget(self.btn_save)
        form.addWidget(self.btn_update)
        form.addWidget(self.btn_delete)
        form.addWidget(self.btn_clear)
        layout.addLayout(form)

        # ตารางแสดงข้อมูล
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "ISO Code", "Revision", "Effective Date"])
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 150)
        layout.addWidget(self.table)

        # โหลดข้อมูล
        self.load_data()

        # Event bindings
        self.table.cellClicked.connect(self.on_row_clicked)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_update.clicked.connect(self.on_update)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_clear.clicked.connect(self.clear_form)

    # -------------------------
    # ฟังก์ชัน CRUD
    # -------------------------
    def load_data(self):
        self.table.setRowCount(0)
        rows = list_revisions()
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(r["wh1rev_id"])))
            self.table.setItem(i, 1, QTableWidgetItem(r["wh1rev_code"]))
            self.table.setItem(i, 2, QTableWidgetItem(r["wh1rev_rev"]))
            self.table.setItem(i, 3, QTableWidgetItem(thai_to_arabic(str(r["wh1rev_eff"]))))


    def clear_form(self):
        self.current_id = None
        self.ed_code.clear()
        self.ed_rev.clear()
        self.ed_eff.setDate(QDate.currentDate())

    def on_save(self):
        code = self.ed_code.text().strip()
        rev = self.ed_rev.text().strip()
        eff = self.ed_eff.date().toPyDate()
        if not code or not rev:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอกข้อมูลให้ครบ")
            return
        insert_revision(code, rev, eff)
        QMessageBox.information(self, "สำเร็จ", "บันทึกข้อมูลเรียบร้อย ✅")
        self.load_data()
        self.clear_form()

    def on_update(self):
        if not self.current_id:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกข้อมูลก่อนแก้ไข")
            return
        code = self.ed_code.text().strip()
        rev = self.ed_rev.text().strip()
        eff = self.ed_eff.date().toPyDate()
        update_revision(self.current_id, code, rev, eff)
        QMessageBox.information(self, "สำเร็จ", "แก้ไขข้อมูลเรียบร้อย ✅")
        self.load_data()
        self.clear_form()

    def on_delete(self):
        if not self.current_id:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกข้อมูลที่จะลบ")
            return
        if confirm_dialog(self, "ยืนยัน", "ต้องการลบข้อมูลนี้หรือไม่?"):
            delete_revision(self.current_id)
            QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลเรียบร้อย ✅")
            self.load_data()
            self.clear_form()

    def on_row_clicked(self, row, _):
        """เมื่อคลิกแถวในตาราง — โหลดข้อมูลกลับไปฟอร์ม"""
        self.current_id = int(self.table.item(row, 0).text())
        self.ed_code.setText(self.table.item(row, 1).text())
        self.ed_rev.setText(self.table.item(row, 2).text())
        eff_text = thai_to_arabic(self.table.item(row, 3).text())
        self.ed_eff.setDate(QDate.fromString(eff_text, "yyyy-MM-dd"))
