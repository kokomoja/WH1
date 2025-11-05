from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QLabel, QHeaderView,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import QDate, Qt
from db import list_records, get_products, get_sm_list, get_lighters
from utils import info, warn, setup_dateedit
from utils_excel import export_tablewidget_to_excel
from utils_pdf import build_wh1_report_pdf
import os
from datetime import datetime

class WH1ReportForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle("WH1FMOP01 | รายงาน / ค้นหา / Export")
        self.resize(1350, 700)

        root = QVBoxLayout(self)

        # --- Filters ---
        filter_layout = QVBoxLayout()

        row_date = QHBoxLayout()
        row_date.setContentsMargins(0, 0, 0, 0)
        row_date.setSpacing(10)
        row_date.setAlignment(Qt.AlignLeft)

        row_date.addWidget(QLabel("จากวันที่"))
        self.d_from = setup_dateedit(QDateEdit(calendarPopup=True))
        self.d_from.setDate(QDate.currentDate().addMonths(-1))
        row_date.addWidget(self.d_from)

        row_date.addWidget(QLabel("ถึงวันที่"))
        self.d_to = setup_dateedit(QDateEdit(calendarPopup=True))
        self.d_to.setDate(QDate.currentDate())
        row_date.addWidget(self.d_to)

        self.d_from.setFixedWidth(110)
        self.d_to.setFixedWidth(110)

        filter_layout.addLayout(row_date)

        # Combos
        row_combo = QHBoxLayout()
        row_combo.setContentsMargins(0, 0, 0, 0)
        row_combo.setSpacing(10)
        row_combo.setAlignment(Qt.AlignLeft)

        row_combo.addWidget(QLabel("เที่ยวเรือ"))
        self.cb_sm = QComboBox()
        self.cb_sm.addItem("แสดงทั้งหมด")
        for sm in get_sm_list():
            self.cb_sm.addItem(sm)
        row_combo.addWidget(self.cb_sm)

        row_combo.addWidget(QLabel("ชื่อเรือ"))
        self.cb_lighter = QComboBox()
        self.cb_lighter.addItem("แสดงทั้งหมด")
        for l in get_lighters():
            self.cb_lighter.addItem(l)
        row_combo.addWidget(self.cb_lighter)

        row_combo.addWidget(QLabel("สินค้า"))
        self.cb_product = QComboBox()
        self.cb_product.addItem("แสดงทั้งหมด")
        for p in get_products():
            self.cb_product.addItem(p)
        row_combo.addWidget(self.cb_product)

        self.cb_sm.setFixedWidth(120)
        self.cb_lighter.setFixedWidth(180)
        self.cb_product.setFixedWidth(260)

        filter_layout.addLayout(row_combo)
        root.addLayout(filter_layout)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(20)
        btn_layout.setAlignment(Qt.AlignLeft)

        self.btn_search = QPushButton("ค้นหา")
        self.btn_search.setFixedSize(200, 40)
        self.btn_export = QPushButton("ส่งออก Excel")
        self.btn_export.setFixedSize(200, 40)
        self.btn_pdf = QPushButton("ส่งออก PDF")
        self.btn_pdf.setFixedSize(200, 40)

        btn_layout.addWidget(self.btn_search)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_pdf)
        root.addLayout(btn_layout)

        # --- Table ---
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "วันที่", "เวลาเริ่มต้น", "เวลาสิ้นสุด", "เที่ยวเรือ", "ชื่อเรือ", "ชื่อสินค้า", "จำนวน(ถุง)", "น้ำหนัก(ตัน)"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        root.addWidget(self.table)

        # Signals
        self.btn_search.clicked.connect(self.search)
        self.btn_export.clicked.connect(self.export_excel)
        self.btn_pdf.clicked.connect(self.export_pdf)

        self.search(None)

    def _collect_filters(self):
        sm = None if self.cb_sm.currentText() == "แสดงทั้งหมด" else self.cb_sm.currentText()
        lighter = None if self.cb_lighter.currentText() == "แสดงทั้งหมด" else self.cb_lighter.currentText()
        product = None if self.cb_product.currentText() == "แสดงทั้งหมด" else self.cb_product.currentText()
        return {
            "date_from": self.d_from.date().toPyDate(),
            "date_to": self.d_to.date().toPyDate(),
            "sm": sm, "lighter": lighter, "product": product
        }

    # ---------- SEARCH ----------
    def search(self, _=None):
        try:
            rows = list_records(self._collect_filters())
            self.table.setRowCount(0)
            for r in rows:
                i = self.table.rowCount()
                self.table.insertRow(i)
                vals = [
                    str(r.get("WH1_date")),
                    str(r.get("WH1_start") or ""),
                    str(r.get("WH1_stop") or ""),
                    str(r.get("WH1_SM") or ""),
                    str(r.get("WH1_lighter") or ""),
                    str(r.get("WH1_product") or ""),
                    f"{float(r.get('WH1_blQty') or 0):,.2f}",
                    f"{float(r.get('WH1_blMt') or 0):,.2f}"
                ]
                for c, v in enumerate(vals):
                    item = QTableWidgetItem(v)
                    if c in (6, 7):
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    else:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, c, item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"ไม่สามารถค้นหาข้อมูลได้\n\n{e}")

    # ---------- EXPORT EXCEL ----------
    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "บันทึก Excel", "", "Excel (*.xlsx)")
        if not path:
            return
        export_tablewidget_to_excel(self.table, path)
        info(self, "Export", f"บันทึกไฟล์ Excel เรียบร้อย\n{path}")

    # ---------- EXPORT PDF ----------
    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "บันทึกไฟล์ PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        # ถ้ามีไฟล์อยู่แล้ว เพิ่ม timestamp ท้ายชื่อ
        if os.path.exists(path):
            base, ext = os.path.splitext(path)
            path = base + "_" + datetime.now().strftime("%H%M%S") + ext

        rows = list_records(self._collect_filters())
        if not rows:
            warn(self, "ไม่มีข้อมูล", "ไม่พบข้อมูลสำหรับสร้างรายงาน")
            return

        title = "รายงานสรุปการขนถ่ายสินค้า (WH1FMOP01)"
        subtitle = f"ช่วงวันที่ {self.d_from.date().toString('dd/MM/yyyy')} - {self.d_to.date().toString('dd/MM/yyyy')}"
        build_wh1_report_pdf(path, rows, title, subtitle)
        info(self, "Export PDF", f"สร้างรายงาน PDF สำเร็จ\n{path}")
