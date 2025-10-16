from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QLineEdit,
    QDateEdit, QTimeEdit, QTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QLabel, QComboBox, QInputDialog, QSizePolicy
)
from PyQt5.QtCore import QDate, QTime, Qt
from PyQt5.QtGui import QFont
from db import (
    list_records, create_record, update_record, delete_record,
    create_item_record, list_item_records, get_products, add_product
)
from utils import setup_dateedit, setup_timeedit, confirm_dialog


class MainForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 FM-OP-01 | ฟอร์มบันทึกข้อมูล")
        self.resize(1150, 800)
        self.current_id = None

        # ฟอนต์หลัก
        self.setFont(QFont("TH Sarabun New", 14))

        # === กล่องหลัก (แนวตั้ง) ===
        root = QVBoxLayout(self)
        root.setSpacing(20)  # ระยะห่างระหว่างแถว

        # === แถวที่ 1: ID ===
        row1 = QHBoxLayout()
        lbl_id = QLabel("Sequence (ID):")
        self.ed_id = QLineEdit()
        self.ed_id.setReadOnly(True)
        self.ed_id.setFixedWidth(120)
        self.ed_id.setStyleSheet("background-color:#f0f0f0; color:gray;")
        row1.addWidget(lbl_id)
        row1.addWidget(self.ed_id)
        row1.addStretch()  # ✅ ป้องกันการขยาย
        root.addLayout(row1)

        # === แถวที่ 2: วันที่ / ชุดเรือ / ชื่อเรือ ===
        row2 = QHBoxLayout()
        self.d_date = setup_dateedit(QDateEdit(calendarPopup=True))
        self.d_date.setDate(QDate.currentDate())
        self.d_date.setFixedWidth(150)

        self.ed_sm = QLineEdit()
        self.ed_sm.setFixedWidth(120)

        self.ed_lighter = QLineEdit()
        self.ed_lighter.setFixedWidth(200)

        row2.addWidget(QLabel("วันที่:"))
        row2.addWidget(self.d_date)
        row2.addSpacing(30)
        row2.addWidget(QLabel("ชุดเรือ:"))
        row2.addWidget(self.ed_sm)
        row2.addSpacing(30)
        row2.addWidget(QLabel("ชื่อเรือ:"))
        row2.addWidget(self.ed_lighter)
        row2.addStretch()
        root.addLayout(row2)

        # === แถวที่ 3: เวลาเริ่ม / เวลาสิ้นสุด ===
        row3 = QHBoxLayout()
        self.t_start = setup_timeedit(QTimeEdit())
        self.t_start.setTime(QTime(8, 0))
        self.t_start.setFixedWidth(100)

        self.t_stop = setup_timeedit(QTimeEdit())
        self.t_stop.setTime(QTime(22, 0))
        self.t_stop.setFixedWidth(100)

        row3.addWidget(QLabel("เวลาเริ่ม:"))
        row3.addWidget(self.t_start)
        row3.addSpacing(30)
        row3.addWidget(QLabel("เวลาสิ้นสุด:"))
        row3.addWidget(self.t_stop)
        row3.addStretch()
        root.addLayout(row3)

        # === แถวที่ 4: หมายเหตุ ===
        row4 = QHBoxLayout()
        self.ed_remark = QTextEdit()
        self.ed_remark.setFixedHeight(60)
        self.ed_remark.setFixedWidth(450)
        row4.addWidget(QLabel("หมายเหตุ:"))
        row4.addWidget(self.ed_remark)
        row4.addStretch()
        root.addLayout(row4)       

        # === ตารางสินค้า ===
        lbl_items = QLabel("รายการสินค้า (รับเข้า)")
        lbl_items.setFont(QFont("TH Sarabun New", 16, QFont.Bold))
        root.addWidget(lbl_items)

        self.tbl_items = QTableWidget(0, 3)
        self.tbl_items.setHorizontalHeaderLabels(["สินค้า", "ถุง (รับเข้า)", "ตัน (รับเข้า)"])
        self.tbl_items.setColumnWidth(0, 300)
        self.tbl_items.setColumnWidth(1, 150)
        self.tbl_items.setColumnWidth(2, 150)
        root.addWidget(self.tbl_items)

        row_btn_item = QHBoxLayout()
        self.btn_add_item = QPushButton("➕ เพิ่มรายการสินค้า")
        self.btn_add_item.clicked.connect(self.add_item_row)
        self.btn_del_item = QPushButton("🗑️ ลบรายการที่เลือก")
        self.btn_del_item.clicked.connect(self.delete_selected_item)
        row_btn_item.addWidget(self.btn_add_item)
        row_btn_item.addWidget(self.btn_del_item)
        root.addLayout(row_btn_item)

        # === ปุ่ม CRUD ===
        row_btn = QHBoxLayout()
        self.btn_save = QPushButton("💾 บันทึกใหม่")
        self.btn_update = QPushButton("✏️ แก้ไขข้อมูล")
        self.btn_delete = QPushButton("🗑️ ลบข้อมูล")
        self.btn_clear = QPushButton("🔄 เคลียร์ฟอร์ม")
        self.btn_refresh = QPushButton("📋 โหลดข้อมูล")

        for b in [self.btn_save, self.btn_update, self.btn_delete, self.btn_clear, self.btn_refresh]:
            b.setMinimumHeight(38)
            b.setFont(QFont("TH Sarabun New", 14, QFont.Bold))
            row_btn.addWidget(b)
        root.addLayout(row_btn)

        # === ตารางแสดงข้อมูลหลัก ===
        self.table = QTableWidget(0, 7)
        headers = ["ID", "วันที่", "ชุดเรือ", "ชื่อเรือ", "เวลาเริ่ม", "เวลาสิ้นสุด", "หมายเหตุ"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.cellClicked.connect(self.on_row_clicked)
        root.addWidget(self.table)

        self.load_table()

        self.btn_save.clicked.connect(self.on_save)
        self.btn_update.clicked.connect(self.on_update)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_refresh.clicked.connect(self.load_table)

    # -------------------------------------------------------
    # ส่วนของสินค้า
    # -------------------------------------------------------
    def add_item_row(self):
        row = self.tbl_items.rowCount()
        self.tbl_items.insertRow(row)

        cb = QComboBox()
        cb.addItems(get_products())
        cb.setEditable(False)

        btn_add = QPushButton("➕")
        btn_add.setFixedWidth(35)
        btn_add.clicked.connect(self.add_new_product)

        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(cb)
        layout.addWidget(btn_add)
        self.tbl_items.setCellWidget(row, 0, cell_widget)

        self.tbl_items.setItem(row, 1, QTableWidgetItem("0"))
        self.tbl_items.setItem(row, 2, QTableWidgetItem("0"))

    def add_new_product(self):
        text, ok = QInputDialog.getText(self, "เพิ่มสินค้าใหม่", "ชื่อสินค้า:")
        if ok and text.strip():
            add_product(text.strip())
            QMessageBox.information(self, "สำเร็จ", f"เพิ่มสินค้าใหม่: {text.strip()}")

    def delete_selected_item(self):
        row = self.tbl_items.currentRow()
        if row >= 0:
            self.tbl_items.removeRow(row)

    # -------------------------------------------------------
    # CRUD
    # -------------------------------------------------------
    def clear_form(self):
        self.current_id = None
        self.ed_id.clear()
        self.d_date.setDate(QDate.currentDate())
        self.ed_sm.clear()
        self.ed_lighter.clear()
        self.t_start.setTime(QTime(8, 0))
        self.t_stop.setTime(QTime(22, 0))
        self.ed_remark.clear()
        self.tbl_items.setRowCount(0)

    def load_table(self):
        self.table.setRowCount(0)
        rows = list_records()
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            for c, k in enumerate(["WH1_id", "WH1_date", "WH1_SM", "WH1_lighter", "WH1_start", "WH1_stop", "WH1_remark"]):
                self.table.setItem(i, c, QTableWidgetItem("" if r[k] is None else str(r[k])))

    def on_row_clicked(self, row, _):
        """โหลดข้อมูลจากแถวที่เลือกขึ้นฟอร์ม"""
        self.current_id = int(self.table.item(row, 0).text())
        self.ed_id.setText(str(self.current_id))

        # วันที่
        date_text = self.table.item(row, 1).text()
        if date_text:
            try:
                qdate = QDate.fromString(date_text, "yyyy-MM-dd")
                if not qdate.isValid():
                    qdate = QDate.fromString(date_text, "dd/MM/yyyy")
                self.d_date.setDate(qdate)
            except Exception:
                pass

        # ชุดเรือ / ชื่อเรือ
        self.ed_sm.setText(self.table.item(row, 2).text())
        self.ed_lighter.setText(self.table.item(row, 3).text())

        # เวลาเริ่ม
        start_text = self.table.item(row, 4).text()
        if start_text:
            try:
                qtime = QTime.fromString(start_text.strip(), "HH:mm:ss")
                if not qtime.isValid():
                    qtime = QTime.fromString(start_text.strip(), "HH:mm")
                self.t_start.setTime(qtime)
            except Exception:
                pass

        # เวลาสิ้นสุด
        stop_text = self.table.item(row, 5).text()
        if stop_text:
            try:
                qtime = QTime.fromString(stop_text.strip(), "HH:mm:ss")
                if not qtime.isValid():
                    qtime = QTime.fromString(stop_text.strip(), "HH:mm")
                self.t_stop.setTime(qtime)
            except Exception:
                pass

        # หมายเหตุ
        self.ed_remark.setPlainText(self.table.item(row, 6).text())

        # โหลดรายการสินค้า
        self.tbl_items.setRowCount(0)
        for it in list_item_records(self.current_id):
            r = self.tbl_items.rowCount()
            self.tbl_items.insertRow(r)
            cb = QComboBox()
            cb.addItems(get_products())
            cb.setCurrentText(it["product_name"])

            btn_add = QPushButton("➕")
            btn_add.setFixedWidth(35)
            btn_add.clicked.connect(self.add_new_product)

            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(cb)
            layout.addWidget(btn_add)
            self.tbl_items.setCellWidget(r, 0, cell_widget)

            self.tbl_items.setItem(r, 1, QTableWidgetItem(str(it["qty_bag"])))
            self.tbl_items.setItem(r, 2, QTableWidgetItem(str(it["qty_ton"])))

    def on_save(self):
        header = {
            "WH1_date": self.d_date.date().toPyDate(),
            "WH1_SM": self.ed_sm.text(),
            "WH1_lighter": self.ed_lighter.text(),
            "WH1_start": self.t_start.time().toPyTime(),
            "WH1_stop": self.t_stop.time().toPyTime(),
            "WH1_remark": self.ed_remark.toPlainText(),
        }
        new_id = create_record(header)

        for r in range(self.tbl_items.rowCount()):
            cell_widget = self.tbl_items.cellWidget(r, 0)
            cb = cell_widget.findChild(QComboBox)
            product = cb.currentText() if cb else ""
            bag = float(self.tbl_items.item(r, 1).text() or 0)
            ton = float(self.tbl_items.item(r, 2).text() or 0)
            create_item_record(new_id, product, bag, ton)

        QMessageBox.information(self, "สำเร็จ", f"เพิ่มข้อมูลเรียบร้อย (ID {new_id})")
        self.load_table()
        self.clear_form()

    def on_update(self):
        if not self.current_id:
            QMessageBox.warning(self, "เตือน", "กรุณาเลือกข้อมูลก่อนแก้ไข")
            return

        header = {
            "WH1_date": self.d_date.date().toPyDate(),
            "WH1_SM": self.ed_sm.text(),
            "WH1_lighter": self.ed_lighter.text(),
            "WH1_start": self.t_start.time().toPyTime(),
            "WH1_stop": self.t_stop.time().toPyTime(),
            "WH1_remark": self.ed_remark.toPlainText(),
        }

        # ✅ อัปเดตหัวเอกสาร
        update_record(self.current_id, header)

        # ✅ ลบรายการสินค้าเก่าทั้งหมดก่อน
        from db import delete_items_by_header
        delete_items_by_header(self.current_id)

        # ✅ เพิ่มรายการสินค้าใหม่จากตาราง
        for r in range(self.tbl_items.rowCount()):
            cell_widget = self.tbl_items.cellWidget(r, 0)
            cb = cell_widget.findChild(QComboBox)
            product = cb.currentText() if cb else ""
            bag = float(self.tbl_items.item(r, 1).text() or 0)
            ton = float(self.tbl_items.item(r, 2).text() or 0)
            create_item_record(self.current_id, product, bag, ton)

        QMessageBox.information(self, "สำเร็จ", "อัปเดตข้อมูลเรียบร้อย ✅")
        self.load_table()


    def on_delete(self):
        if not self.current_id:
            QMessageBox.warning(self, "เตือน", "กรุณาเลือกข้อมูลที่จะลบ")
            return
        if confirm_dialog(self, "ยืนยัน", "ต้องการลบข้อมูลนี้หรือไม่?"):
            delete_record(self.current_id)
            QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลเรียบร้อย ✅")
            self.load_table()
