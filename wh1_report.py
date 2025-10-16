from PyQt5.QtWidgets import ( 
    QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QLabel, QHeaderView, QTableWidgetItem,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import QDate, Qt
from openpyxl import Workbook
from db import list_records, get_products, get_sm_list, get_lighters   # ✅ เพิ่มฟังก์ชันใหม่
from utils import info, warn, setup_dateedit

# ==== สำหรับ PDF ====
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os


class WH1ReportForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle("WH1FMOP01 | รายงาน / ค้นหา / Export")
        self.setStyleSheet("font-family:'TH Sarabun New'; font-size:14pt;")
        self.resize(1350, 700)

        root = QVBoxLayout(self)

        # --- Filters ---
        filter_layout = QVBoxLayout()

 # ✅ แถววันที่ (เริ่มต้น–สิ้นสุด)
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
                
        self.d_from.setFixedWidth(100)
        self.d_to.setFixedWidth(100)

        filter_layout.addLayout(row_date)

        # ✅ แถว combobox (เที่ยวเรือ–ชื่อเรือ–สินค้า)
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

        self.cb_sm.setFixedWidth(100)
        self.cb_lighter.setFixedWidth(150)
        self.cb_product.setFixedWidth(250)

        filter_layout.addLayout(row_combo)

        root.addLayout(filter_layout)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(20)                # ✅ ระยะห่าง 20px
        btn_layout.setAlignment(Qt.AlignLeft)    # ✅ จัดชิดซ้าย

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

        # ✅ ปรับขนาดคอลัมน์ตามข้อมูล
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        root.addWidget(self.table)

        # --- Signals ---
        self.btn_search.clicked.connect(self.search)
        self.btn_export.clicked.connect(self.export_excel)
        self.btn_pdf.clicked.connect(self.export_pdf)

        self.search(None)

    # -------------------------------------------------------------
    # 🔍 SEARCH
    # -------------------------------------------------------------
    def search(self, _=None):
        try:
            sm_filter = None if self.cb_sm.currentText() == "แสดงทั้งหมด" else self.cb_sm.currentText()
            lighter_filter = None if self.cb_lighter.currentText() == "แสดงทั้งหมด" else self.cb_lighter.currentText()
            product_filter = None if self.cb_product.currentText() == "แสดงทั้งหมด" else self.cb_product.currentText()

            filters = {
                "date_from": self.d_from.date().toPyDate(),
                "date_to": self.d_to.date().toPyDate(),
                "sm": sm_filter,
                "lighter": lighter_filter,
                "product": product_filter
            }

            rows = list_records(filters)
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

                    # ✅ align right เฉพาะถุงและตัน
                    if c in (6, 7):
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    else:
                        item.setTextAlignment(Qt.AlignCenter)

                    self.table.setItem(i, c, item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"ไม่สามารถค้นหาข้อมูลได้\n\n{e}")
            
    # -------------------------------------------------------------
    # 📊 EXPORT EXCEL
    # -------------------------------------------------------------
    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "บันทึก Excel", "", "Excel (*.xlsx)")
        if not path:
            return
        wb = Workbook()
        ws = wb.active
        headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
        ws.append(headers)

        for r in range(self.table.rowCount()):
            row_vals = [
                self.table.item(r, c).text() if self.table.item(r, c) else ""
                for c in range(self.table.columnCount())
            ]
            append(row_vals)
        wb.save(path)
        info(self, "Export", f"บันทึกไฟล์ Excel เรียบร้อย\n{path}")

    # -------------------------------------------------------------
    # 📄 EXPORT PDF
    # -------------------------------------------------------------
    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "บันทึกไฟล์ PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        if os.path.exists(path):
            base, ext = os.path.splitext(path)
            path = base + "_" + datetime.now().strftime("%H%M%S") + ext

        filters = {
            "date_from": self.d_from.date().toPyDate(),
            "date_to": self.d_to.date().toPyDate(),
            "sm": self.ed_sm.text().strip() or None,
            "lighter": self.ed_lighter.text().strip() or None,
            "product": None if self.cb_product.currentText() == "แสดงทั้งหมด" else self.cb_product.currentText().strip()
            }
        rows = list_records(filters)
        if not rows:
            warn(self, "ไม่มีข้อมูล", "ไม่พบข้อมูลสำหรับสร้างรายงาน")
            return

        pdfmetrics.registerFont(TTFont("THSarabunNew", "THSarabunNew.ttf"))

        doc = SimpleDocTemplate(path, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        style_title = styles["Title"]
        style_title.fontName = "THSarabunNew"
        style_title.fontSize = 20
        style_normal = styles["Normal"]
        style_normal.fontName = "THSarabunNew"
        style_normal.fontSize = 14

        story = []
        title = Paragraph("รายงานสรุปการขนถ่ายสินค้า (WH1FMOP01)", style_title)
        sub = Paragraph(
            f"ช่วงวันที่ {self.d_from.date().toString('dd/MM/yyyy')} - {self.d_to.date().toString('dd/MM/yyyy')}",
            style_normal
        )
        story.extend([title, sub, Spacer(1, 12)])

        # ✅ เพิ่มคอลัมน์สินค้า/เที่ยวเรือ
        data = [["วันที่", "เวลาเริ่ม", "เวลาสิ้นสุด", "เที่ยวเรือ", "ชื่อสินค้า", "จำนวนถุง", "น้ำหนัก (ตัน)"]]

        total_bag, total_ton = 0, 0.0
        for r in rows:
            bag = float(r.get("WH1_blQty") or 0)
            ton = float(r.get("WH1_blMt") or 0)
            total_bag += bag
            total_ton += ton
            data.append([
                str(r.get("WH1_date")),
                str(r.get("WH1_start") or ""),
                str(r.get("WH1_stop") or ""),
                str(r.get("WH1_SM") or ""),
                str(r.get("WH1_lighter") or ""),
                str(r.get("WH1_product") or ""),
                f"{bag:,.2f}",   # ✅
                f"{ton:,.2f}"    # ✅
            ])

        data.append(["", "", "", "รวมทั้งหมด", "", "", f"{total_bag:,.2f} ถุง", f"{total_ton:,.2f} ตัน"])

        table = Table(data, colWidths=[2.5*cm, 2.0*cm, 2.0*cm, 2.5*cm, 4.0*cm, 3.0*cm, 3.0*cm])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "THSarabunNew"),
            ("FONTSIZE", (0, 0), (-1, -1), 14),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (5, 1), (6, -1), "CENTER"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke),
        ]))

        story.append(table)
        doc.build(story)
        info(self, "Export PDF", f"สร้างรายงาน PDF สำเร็จ\n{path}")
