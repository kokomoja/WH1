from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QSpacerItem,
    QDateEdit, QTimeEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QLabel, QComboBox, QSizePolicy, QInputDialog
)
from PyQt5.QtCore import QDate, QTime, Qt
from PyQt5.QtGui import QFont
from db import (
    list_headers, list_item_records, create_record, create_item_record,
    update_record, delete_record, delete_items_by_header, get_products, add_product
)
from utils import setup_dateedit, setup_timeedit, confirm_dialog

class MainForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 FM-OP-01 | ฟอร์มบันทึกข้อมูล")
        self.resize(1150, 800)
        self.current_id = None

        root = QVBoxLayout(self)
        root.setSpacing(20)

        # Row 1: Header fields
        row1 = QHBoxLayout()
        row1.setAlignment(Qt.AlignLeft)

        lbl_id = QLabel("Sequence (ID):")
        self.ed_id = QLineEdit()
        self.ed_id.setReadOnly(True)
        self.ed_id.setFixedWidth(120)
        self.ed_id.setStyleSheet("background-color:#f0f0f0; color:gray;")

        self.d_date = setup_dateedit(QDateEdit(calendarPopup=True))
        self.d_date.setDate(QDate.currentDate())
        self.d_date.setFixedWidth(150)

        self.ed_sm = QLineEdit()
        self.ed_sm.setFixedWidth(120)

        self.ed_lighter = QLineEdit()
        self.ed_lighter.setFixedWidth(200)

        row1.addWidget(lbl_id)
        row1.addWidget(self.ed_id)
        row1.addWidget(QLabel("วันที่:"))
        row1.addWidget(self.d_date)
        row1.addWidget(QLabel("ชุดเรือ:"))
        row1.addWidget(self.ed_sm)
        row1.addWidget(QLabel("ชื่อเรือ:"))
        row1.addWidget(self.ed_lighter)
        row1.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        row1.addStretch()
        root.addLayout(row1)

        # Row 2: Time + Remark
        row2 = QHBoxLayout()
        row2.setAlignment(Qt.AlignLeft)

        self.t_start = setup_timeedit(QTimeEdit())
        self.t_start.setTime(QTime(8, 0))
        self.t_start.setFixedWidth(90)

        self.t_stop = setup_timeedit(QTimeEdit())
        self.t_stop.setTime(QTime(22, 0))
        self.t_stop.setFixedWidth(90)

        self.ed_remark = QLineEdit()
        self.ed_remark.setFixedWidth(475)

        row2.addWidget(QLabel("เวลาเริ่ม:"))
        row2.addWidget(self.t_start)
        row2.addWidget(QLabel("เวลาสิ้นสุด:"))
        row2.addWidget(self.t_stop)
        row2.addWidget(QLabel("หมายเหตุ:"))
        row2.addWidget(self.ed_remark)
        row2.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        row2.addStretch()
        root.addLayout(row2)

        # Items table
        lbl_items = QLabel("รายการสินค้า (รับเข้า)")
        lbl_items.setFont(QFont("THSarabunNew-Bold", 24))
        root.addWidget(lbl_items)

        self.tbl_items = QTableWidget(0, 3)
        self.tbl_items.setHorizontalHeaderLabels(["สินค้า", "ถุง (รับเข้า)", "ตัน (รับเข้า)"])
        self.tbl_items.setColumnWidth(0, 300)
        self.tbl_items.setColumnWidth(1, 150)
        self.tbl_items.setColumnWidth(2, 150)
        root.addWidget(self.tbl_items)

        self.tbl_items.itemChanged.connect(self.on_item_changed)

        row_btn_item = QHBoxLayout()
        self.btn_add_item = QPushButton("➕ เพิ่มรายการสินค้า")
        self.btn_add_item.clicked.connect(self.add_item_row)
        self.btn_del_item = QPushButton("🗑️ ลบรายการที่เลือก")
        self.btn_del_item.clicked.connect(self.delete_selected_item)
        row_btn_item.addWidget(self.btn_add_item)
        row_btn_item.addWidget(self.btn_del_item)
        root.addLayout(row_btn_item)

        # CRUD buttons
        row_btn = QHBoxLayout()
        self.btn_save = QPushButton("💾 บันทึกใหม่")
        self.btn_update = QPushButton("✏️ แก้ไขข้อมูล")
        self.btn_delete = QPushButton("🗑️ ลบข้อมูล")
        self.btn_clear = QPushButton("🔄 เคลียร์ฟอร์ม")
        self.btn_refresh = QPushButton("📋 โหลดข้อมูล")

        for b in [self.btn_save, self.btn_update, self.btn_delete, self.btn_clear, self.btn_refresh]:
            b.setFont(QFont("THSarabunNew-Bold", 20))
            row_btn.addWidget(b)
        root.addLayout(row_btn)

        # Main table (headers only)
        self.table = QTableWidget(0, 7)
        headers = ["ID", "วันที่", "ชุดเรือ", "ชื่อเรือ", "เวลาเริ่ม", "เวลาสิ้นสุด", "หมายเหตุ"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.cellClicked.connect(self.on_row_clicked)
        root.addWidget(self.table)

        self.load_table()

        # Signals
        self.btn_save.clicked.connect(self.on_save)
        self.btn_update.clicked.connect(self.on_update)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_refresh.clicked.connect(self.load_table)

    # ---------- Items ----------
    def add_item_row(self):
        row = self.tbl_items.rowCount()
        self.tbl_items.insertRow(row)

        cb = QComboBox()
        cb.addItems(get_products())
        cb.setEditable(False)

        btn_add = QPushButton("➕")
        btn_add.setFixedWidth(35)
        btn_add.clicked.connect(self.add_new_product)

        cell = QWidget()
        h = QHBoxLayout(cell)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(cb)
        h.addWidget(btn_add)
        self.tbl_items.setCellWidget(row, 0, cell)

        self.tbl_items.setItem(row, 1, QTableWidgetItem("0"))
        self.tbl_items.setItem(row, 2, QTableWidgetItem("0"))

    def add_new_product(self):
        text, ok = QInputDialog.getText(self, "เพิ่มสินค้าใหม่", "ชื่อสินค้าใหม่:")
        if ok and text.strip():
            add_product(text.strip())
            QMessageBox.information(self, "สำเร็จ", f"เพิ่มสินค้าใหม่: {text.strip()}")

    def delete_selected_item(self):
        row = self.tbl_items.currentRow()
        if row >= 0:
            self.tbl_items.removeRow(row)

    # ---------- CRUD ----------
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
        rows = list_headers()
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            vals = [
                str(r.get("WH1_id")),
                str(r.get("WH1_date")),
                str(r.get("WH1_SM")),
                str(r.get("WH1_lighter")),
                str(r.get("WH1_start") or ""),
                str(r.get("WH1_stop") or ""),
                str(r.get("WH1_remark") or "")
            ]
            for c, v in enumerate(vals):
                self.table.setItem(i, c, QTableWidgetItem(v))

    def on_row_clicked(self, row, _):
        self.current_id = int(self.table.item(row, 0).text())

        self.d_date.setDate(QDate.fromString(self.table.item(row, 1).text(), "yyyy-MM-dd"))
        self.ed_sm.setText(self.table.item(row, 2).text())
        self.ed_lighter.setText(self.table.item(row, 3).text())
        self.t_start.setTime(QTime.fromString(self.table.item(row, 4).text(), "HH:mm:ss"))
        self.t_stop.setTime(QTime.fromString(self.table.item(row, 5).text(), "HH:mm:ss"))
        self.ed_remark.setText(self.table.item(row, 6).text())

        self.tbl_items.setRowCount(0)
        items = list_item_records(self.current_id)
        for it in items:
            r = self.tbl_items.rowCount()
            self.tbl_items.insertRow(r)

            cb = QComboBox()
            cb.addItems(get_products())
            cb.setCurrentText(it["product_name"])

            btn_add = QPushButton("➕")
            btn_add.setFixedWidth(35)
            btn_add.clicked.connect(self.add_new_product)

            cell = QWidget()
            h = QHBoxLayout(cell)
            h.setContentsMargins(0, 0, 0, 0)
            h.addWidget(cb)
            h.addWidget(btn_add)
            self.tbl_items.setCellWidget(r, 0, cell)

            self.tbl_items.setItem(r, 1, QTableWidgetItem(str(it["qty_bag"])))
            self.tbl_items.setItem(r, 2, QTableWidgetItem(str(it["qty_ton"])))

    def on_item_changed(self, item):
        """ถ้าปรับ 'ตัน (รับเข้า)' => คำนวณถุง = ตัน / 1.5 (ตัวอย่างสูตร)"""
        if item and item.column() == 2:
            try:
                val = float(item.text()) if item.text().strip() else 0.0
                bag = val / 1.5
            except ValueError:
                bag = 0.0
            self.tbl_items.blockSignals(True)
            self.tbl_items.setItem(item.row(), 1, QTableWidgetItem(f"{bag:.2f}"))
            self.tbl_items.blockSignals(False)

    def on_save(self):
        header = {
            "WH1_date": self.d_date.date().toPyDate(),
            "WH1_SM": self.ed_sm.text(),
            "WH1_lighter": self.ed_lighter.text(),
            "WH1_start": self.t_start.time().toPyTime(),
            "WH1_stop": self.t_stop.time().toPyTime(),
            "WH1_remark": self.ed_remark.text(),
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
            "WH1_remark": self.ed_remark.text(),
        }
        update_record(self.current_id, header)
        delete_items_by_header(self.current_id)

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
            self.clear_form()
