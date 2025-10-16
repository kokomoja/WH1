# wh1_report.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDateEdit,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog)
from PyQt5.QtCore import QDate
from db import list_records
from utils import info, warn
from openpyxl import Workbook
from utils import setup_dateedit, info, setup_timeedit, confirm_dialog

class ReportWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("WH1FMOP01 | รายงาน / ค้นหา / Export")
        self.setStyleSheet("font-family:'TH Sarabun New'; font-size:14pt;")

        root = QVBoxLayout(self)

        # --- Filters ---
        f = QFormLayout()     
        self.d_from = setup_dateedit(QDateEdit(calendarPopup=True))
        self.d_from.setDate(QDate.currentDate().addMonths(-1))

        self.d_to = setup_dateedit(QDateEdit(calendarPopup=True))
        self.d_to.setDate(QDate.currentDate())

        
        
        self.ed_lighter = QLineEdit()
        self.ed_product = QLineEdit()
        f.addRow("จากวันที่", self.d_from)
        f.addRow("ถึงวันที่", self.d_to)
        f.addRow("เรือบรรทุก (contains)", self.ed_lighter)
        f.addRow("สินค้า (contains)", self.ed_product)
        root.addLayout(f)

        btn_row = QHBoxLayout()
        self.btn_search = QPushButton("ค้นหา")
        self.btn_export = QPushButton("Export Excel")
        btn_row.addWidget(self.btn_search); btn_row.addWidget(self.btn_export)
        root.addLayout(btn_row)

        # --- Table ---
        self.table = QTableWidget(0, 12)
        self.table.setHorizontalHeaderLabels([
            "WH1_id","WH1_date","WH1_lighter","WH1_start","WH1_stop","WH1_product",
            "WH1_blQty","WH1_blMt","WH1_hdQty","WH1_hdMt","WH1_loss","WH1_remark"
        ])
        root.addWidget(self.table)

        self.btn_search.clicked.connect(self.search)
        self.btn_export.clicked.connect(self.export_excel)

        self.search()  # initial

    def search(self):
        filters = {
            "date_from": self.d_from.date().toPyDate(),
            "date_to": self.d_to.date().toPyDate(),
            "lighter": self.ed_lighter.text().strip() or None,
            "product": self.ed_product.text().strip() or None
        }
        rows = list_records(filters)
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            vals = [r.get(k) for k in ["WH1_id","WH1_date","WH1_lighter","WH1_start","WH1_stop","WH1_product",
                                       "WH1_blQty","WH1_blMt","WH1_hdQty","WH1_hdMt","WH1_loss","WH1_remark"]]
            for c,v in enumerate(vals):
                self.table.setItem(i, c, QTableWidgetItem("" if v is None else str(v)))

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "บันทึก Excel", "", "Excel (*.xlsx)")
        if not path:
            return
        wb = Workbook(); ws = wb.active
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        ws.append(headers)
        for r in range(self.table.rowCount()):
            row_vals = [self.table.item(r, c).text() if self.table.item(r,c) else "" for c in range(self.table.columnCount())]
            ws.append(row_vals)
        wb.save(path)
        info(self, "Export", f"บันทึกไฟล์เรียบร้อย\n{path}")
