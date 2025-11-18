from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QBrush
from db import get_connection, get_tanks
from utils import setup_dateedit


class OilReportForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛢️ บันทึกรับ–จ่ายน้ำมัน (Daily Report)")
        self.resize(1500, 950)
        self.current_date = QDate.currentDate()
        self.tanks = get_tanks() or ["1", "2", "3"]
        self.page = 0

        root = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("วันที่:"))
        self.d_date = setup_dateedit(QDateEdit(calendarPopup=True))
        self.d_date.setDate(self.current_date)
        self.d_date.setFixedWidth(150)
        self.d_date.dateChanged.connect(self.load_data)
        top_bar.addWidget(self.d_date)

        btn_add = QPushButton("➕ เพิ่มถังน้ำมัน")
        btn_add.setFont(QFont("THSarabunNew-Bold", 20))
        btn_add.clicked.connect(self.add_row)
        top_bar.addWidget(btn_add)

        btn_remove = QPushButton("🗑️ ลบถังที่เลือก")
        btn_remove.setFont(QFont("THSarabunNew-Bold", 20))
        btn_remove.clicked.connect(self.remove_selected_row)
        top_bar.addWidget(btn_remove)

        top_bar.addStretch()
        root.addLayout(top_bar)

        headers = [
            "ถัง", "ยอด\nยกมา", "คงเหลือ\nเช้า", "ผลต่าง\n(เข้า)",
            "รับ\nเข้า", "รวม", "จ่าย\nตามบิล", "คง\nเหลือ",
            "มิเตอร์\nเริ่ม", "มิเตอร์\nสิ้นสุด", "ยอดตาม\nมิเตอร์",
            "คงเหลือ\nเย็น", "ผลต่าง\n(เย็น)"
        ]
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setFont(QFont("THSarabunNew", 18))
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setStyleSheet("QTableWidget::item { padding: 6px; }")

        col_widths = [50, 70, 70, 70, 70, 70, 70, 70, 100, 100, 70, 70, 70]
        for i, w in enumerate(col_widths):
            self.table.setColumnWidth(i, w)

        root.addWidget(self.table)
        self.add_default_tanks()
        self.table.itemChanged.connect(self.on_cell_changed)

        action_bar = QHBoxLayout()
        buttons = {
            "💾 บันทึกข้อมูลวันนี้": self.save_data,
            "🗑️ ลบข้อมูลวันนี้": self.delete_today,
            "🧹 ล้างฟอร์ม": self.clear_form
        }
        for text, func in buttons.items():
            btn = QPushButton(text)
            btn.setFont(QFont("THSarabunNew-Bold", 20))
            btn.setFixedWidth(230)
            btn.clicked.connect(func)
            action_bar.addWidget(btn)
        action_bar.addStretch()
        root.addLayout(action_bar)

        lower_area = QHBoxLayout()

        # ---------------- LEFT : HISTORY ----------------
        left_hist = QVBoxLayout()

        lbl_hist = QLabel("📜 ข้อมูลย้อนหลังและผลรวม")
        lbl_hist.setFont(QFont("THSarabunNew-Bold", 22))
        lbl_hist.setStyleSheet("margin-top:10px; margin-bottom:5px;")
        left_hist.addWidget(lbl_hist)

        headers_hist = ["วันที่", "จำนวน\nถัง", "ยกมา\nรวม", "รับเข้า\nรวม", "จ่ายรวม", "คงเหลือ\nรวม"]
  
        self.table_hist = QTableWidget(0, len(headers_hist))
        self.table_hist.setHorizontalHeaderLabels(headers_hist)
        self.table_hist.setFont(QFont("THSarabunNew", 18))

        self.table_hist.horizontalHeader().setFixedHeight(45)
        self.table_hist.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # ⭐ ปิด Stretch

        # --- Fix Column Width ---
        col_widths = [110, 60, 70, 70, 70, 70]
        total_width = sum(col_widths)

        for i, w in enumerate(col_widths):
            self.table_hist.setColumnWidth(i, w)

        # --- Fix Total Table Width ---
        self.table_hist.setFixedWidth(total_width + 40)  # ⭐ +20 padding กัน scrollbar
        self.table_hist.itemClicked.connect(self.load_selected_date)
        left_hist.addWidget(self.table_hist)


        # ---------------- RIGHT : MACHINE ISSUE ----------------
        right_machine = QVBoxLayout()

        lbl_machine = QLabel("🚚 การจ่ายน้ำมันให้เครื่องจักร / รถบรรทุก")
        lbl_machine.setFont(QFont("THSarabunNew-Bold", 22))
        lbl_machine.setStyleSheet("margin-top:10px; margin-bottom:5px;")
        right_machine.addWidget(lbl_machine)

        headers_machine = ["ถัง", "เครื่องจักร/รถ", "มิเตอร์สุทธิ"]

        self.tbl_machine = QTableWidget(0, len(headers_machine))
        self.tbl_machine.setHorizontalHeaderLabels(headers_machine)
        self.tbl_machine.setFont(QFont("THSarabunNew", 18))

        self.tbl_machine.horizontalHeader().setFixedHeight(45)
        self.tbl_machine.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # ⭐ ปิด Stretch

        # --- Fix Column Width ---
        col_widths = [50, 130, 80]
        total_width = sum(col_widths)

        for i, w in enumerate(col_widths):
            self.tbl_machine.setColumnWidth(i, w)

        # --- Fix Total Table Width ---
        self.tbl_machine.setFixedWidth(total_width + 40)  # ⭐ +20 padding กัน scrollbar
        self.tbl_machine.itemChanged.connect(self.on_machine_net_changed)
        right_machine.addWidget(self.tbl_machine)

        mach_bar = QHBoxLayout()

        buttons_m = [
            ("➕ เพิ่ม", self.add_machine_row),
            ("➖ ลบ", self.delete_selected_machine_row), 
            ("💾 บันทึก", self.save_machine_issue_data),
            ("🧹 ล้างฟอร์ม", self.clear_machine_issue_form),
        ]

        for text, func in buttons_m:
            btn = QPushButton(text)
            btn.setFont(QFont("THSarabunNew-Bold", 20))
            btn.clicked.connect(func)
            mach_bar.addWidget(btn)

        mach_bar.addStretch()
        right_machine.addLayout(mach_bar)

        # -------- ADD TO ROOT --------
        lower_area.addLayout(left_hist, 3)      # ⭐ สัดส่วนสวยที่สุด
        lower_area.addLayout(right_machine, 2)

        root.addLayout(lower_area)

        nav_bar = QHBoxLayout()
        self.btn_prev = QPushButton("◀ วันถัดไป")
        self.btn_next = QPushButton("วันก่อนหน้า ▶")
        for b in (self.btn_prev, self.btn_next):
            b.setFont(QFont("THSarabunNew-Bold", 20))
            b.setFixedWidth(180)
            nav_bar.addWidget(b)

        nav_bar.addStretch()
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        root.addLayout(nav_bar)

        self.load_history()
        self.load_data()
        self.adjust_table_height()

    def fmt_num(self, val):
        try:
            return f"{float(val):,.0f}"
        except:
            return "0"

    def adjust_table_height(self):
        header_h = self.table.horizontalHeader().height()
        rows_h = self.table.verticalHeader().length()
        total_height = header_h + rows_h + 40
        self.table.setMinimumHeight(total_height)
        self.table.setMaximumHeight(total_height)

    def add_row(self):
        r = self.table.rowCount()

        if r > 0 and self.table.item(r - 1, 0) and self.table.item(r - 1, 0).text() == "รวม":
            r -= 1

        if r >= 5:
            QMessageBox.warning(self, "จำกัดแถว", "สามารถเพิ่มได้สูงสุด 5 แถวเท่านั้น")
            return

        self.table.insertRow(r)

        cb = QComboBox()
        cb.addItems(self.tanks)
        cb.setEditable(True)
        cb.setCurrentText(str(r + 1))
        self.table.setCellWidget(r, 0, cb)

        for c in range(1, self.table.columnCount()):
            item = QTableWidgetItem("0")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            if c in [3, 5, 7, 8, 9, 12]:
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            
            else:
                item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                item.setBackground(QBrush(QColor("#FFF59D")))
                item.setToolTip("กรอกข้อมูลได้")

            self.table.setItem(r, c, item)

        self.update_total_row()
        self.adjust_table_height()


    def add_default_tanks(self):
        """โหลดถังเริ่มต้นจำนวน 5 ถัง"""
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        for i, tank_no in enumerate(self.tanks[:5], start=1):
            self.add_row()
            cb = self.table.cellWidget(i - 1, 0)
            if cb:
                cb.setCurrentText(str(i))

        self.table.blockSignals(False)
        self.update_total_row()
        self.adjust_table_height()

    def delete_selected_machine_row(self):
        """ลบเฉพาะแถวที่เลือกในตารางเครื่องจักร"""
        row = self.tbl_machine.currentRow()

        if row < 0:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกแถวที่ต้องการลบ")
            return

        self.tbl_machine.removeRow(row)

    def remove_selected_row(self):
        row = self.table.currentRow()
        if row < 0:
            return

        if self.table.item(row, 0) and self.table.item(row, 0).text() == "รวม":
            QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถลบแถวรวมได้")
            return

        self.table.removeRow(row)
        self.update_total_row()
        self.adjust_table_height()


    def clear_form(self):
        self.add_default_tanks()
        self.adjust_table_height()

    def on_cell_changed(self, item):
        if not item:
            return

        row = item.row()

        if self.table.item(row, 0) and self.table.item(row, 0).text() == "รวม":
            return

        self.recalculate_row(row)
        self.update_total_row()
        self.adjust_table_height()

    def recalculate_row(self, row):
        """คำนวณค่าต่าง ๆ ภายในแถวเดียว"""

        self.table.blockSignals(True)

        def get_float(col):
            try:
                t = self.table.item(row, col).text().replace(",", "")
                return float(t)
            except:
                return 0.0

        def set_val(col, val, computed=True):
            txt = self.fmt_num(val)
            item = self.table.item(row, col)
            if not item:
                item = QTableWidgetItem()
                self.table.setItem(row, col, item)

            item.setText(txt)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            if computed:
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            else:
                item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                item.setBackground(QBrush(QColor("#FFF59D")))

        oil_prev = get_float(1)
        oil_morning = get_float(2)
        oil_in = get_float(4)
        oil_bill_out = get_float(6)
        oil_evening = get_float(11)
        meter_start = get_float(8)
        meter_stop = get_float(9)
        meter_diff = get_float(10)

        if meter_diff < 0:
            meter_diff = 0

        oil_diff_morning = oil_morning - oil_prev
        oil_sum = oil_morning + oil_in
        oil_balance = oil_sum - oil_bill_out
        oil_diff_evening = oil_evening - oil_balance

        meter_stop = max(meter_start + meter_diff, 0)

        set_val(3, oil_diff_morning)     
        set_val(5, oil_sum)               
        set_val(7, oil_balance)         
        set_val(12, oil_diff_evening)    
        set_val(9, meter_stop)           

        self.table.blockSignals(False)

    def update_total_row(self):
        self.table.blockSignals(True)
        rows = self.table.rowCount()

        if rows > 0 and self.table.item(rows - 1, 0) and self.table.item(rows - 1, 0).text() == "รวม":
            self.table.removeRow(rows - 1)
            rows -= 1

        if rows == 0:
            self.table.blockSignals(False)
            return

        r = self.table.rowCount()
        self.table.insertRow(r)

        label = QTableWidgetItem("รวม")
        label.setTextAlignment(Qt.AlignCenter)
        label.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(r, 0, label)

        cols_to_sum = [1, 3, 4, 5, 6, 7, 10, 11, 12]
        sums = {c: 0 for c in cols_to_sum}

        for i in range(rows):
            for c in cols_to_sum:
                try:
                    v = float(self.table.item(i, c).text().replace(",", ""))
                    sums[c] += v
                except:
                    pass

        for c in range(1, self.table.columnCount()):
            if c in sums:
                item = QTableWidgetItem(self.fmt_num(sums[c]))
            else:
                item = QTableWidgetItem("")

            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(r, c, item)

        self.table.blockSignals(False)
        self.adjust_table_height()

    def save_data(self):
        date_val = self.d_date.date().toPyDate()

        confirm = QMessageBox.question(
            self, "ยืนยันการบันทึก",
            f"ต้องการบันทึกข้อมูลวันที่ {date_val} ใช่หรือไม่?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM WH1_OilDailyReport WHERE oil_date=?", (date_val,))

        rows = self.table.rowCount()
        if rows > 0 and self.table.item(rows - 1, 0).text() == "รวม":
            rows -= 1

        for r in range(rows):
            cb = self.table.cellWidget(r, 0)
            if not cb:
                continue

            tank = cb.currentText()
            vals = []

            for c in range(1, 13):
                try:
                    t = self.table.item(r, c).text().replace(",", "")
                    vals.append(float(t))
                except:
                    vals.append(0)

            cur.execute("""
                INSERT INTO WH1_OilDailyReport
                (oil_date, tank_no, oil_prev, oil_morning, oil_in, oil_bill_out,
                 meter_start, meter_stop, oil_evening)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (date_val, tank, vals[0], vals[1], vals[3], vals[5], vals[7], vals[8], vals[10]))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "สำเร็จ", f"บันทึกข้อมูลวันที่ {date_val} เรียบร้อยแล้ว")
        self.load_history()
        self.load_data()
        self.adjust_table_height()

    def load_data(self):
        """โหลดข้อมูลประจำวันที่เลือก พร้อมแสดงค่าจาก DB ทั้งหมด"""
        date_val = self.d_date.date().toPyDate()
        prev_data = self.get_previous_day_data(date_val)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT tank_no, oil_prev, oil_morning, oil_diff_morning,
                oil_in, oil_sum, oil_bill_out, oil_balance,
                meter_start, meter_stop, meter_diff,
                oil_evening, oil_diff_evening
            FROM WH1_OilDailyReport
            WHERE oil_date=?
            ORDER BY tank_no
        """, (date_val,))
        rows = cur.fetchall()
        conn.close()

        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.table.verticalHeader().setDefaultSectionSize(50)

        if rows:
            for row_data in rows:
                r = self.table.rowCount()
                self.table.insertRow(r)

                cb = QComboBox()
                cb.addItems(self.tanks)
                cb.setEditable(True)
                cb.setCurrentText(str(row_data[0]))
                self.table.setCellWidget(r, 0, cb)

                for c, val in enumerate(row_data[1:], start=1):

                    if c == 10 and val is None:
                        val = max((row_data[9] or 0) - (row_data[8] or 0), 0)

                    txt = self.fmt_num(val)
                    item = QTableWidgetItem(txt)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    if c in [3, 5, 7, 8, 9, 12]:
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    else:
                        item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
                        item.setBackground(QBrush(QColor("#FFF59D")))

                    self.table.setItem(r, c, item)

            self.table.blockSignals(False)

        else:
            if prev_data:
                for tank_no, pdata in prev_data.items():
                    r = self.table.rowCount()
                    self.table.insertRow(r)

                    cb = QComboBox()
                    cb.addItems(self.tanks)
                    cb.setEditable(True)
                    cb.setCurrentText(str(tank_no))
                    self.table.setCellWidget(r, 0, cb)

                    for c in range(1, self.table.columnCount()):
                        item = QTableWidgetItem("0")
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                        if c in [3, 5, 7, 8, 9, 12]:
                            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        else:
                            item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
                            item.setBackground(QBrush(QColor("#FFF59D")))

                        self.table.setItem(r, c, item)

                    self.table.item(r, 1).setText(self.fmt_num(pdata["balance"]))
                    self.table.item(r, 8).setText(self.fmt_num(pdata["meter_stop"]))

                self.table.blockSignals(False)

            else:
                r = self.table.rowCount()
                self.table.insertRow(r)

                cb = QComboBox()
                cb.addItems(self.tanks)
                cb.setEditable(True)
                cb.setCurrentText("1")
                self.table.setCellWidget(r, 0, cb)

                for c in range(1, self.table.columnCount()):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    if c in [3, 5, 7, 8, 9, 12]:
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    else:
                        item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
                        item.setBackground(QBrush(QColor("#FFF59D")))

                    self.table.setItem(r, c, item)

                self.table.blockSignals(False)

        for r in range(self.table.rowCount()):
            self.recalculate_row(r)

        self.update_total_row()
        self.adjust_table_height()


    def get_previous_day_data(self, current_date):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT TOP 1 oil_date
            FROM WH1_OilDailyReport
            WHERE oil_date < ?
            ORDER BY oil_date DESC
        """, (current_date,))
        prev = cur.fetchone()

        if not prev:
            conn.close()
            return {}

        prev_date = prev[0]

        cur.execute("""
            SELECT tank_no, oil_balance, meter_stop
            FROM WH1_OilDailyReport
            WHERE oil_date = ?
        """, (prev_date,))
        rows = cur.fetchall()
        conn.close()

        return {
            str(tank): {
                "balance": float(balance or 0),
                "meter_stop": float(m_stop or 0)
            }
            for tank, balance, m_stop in rows
        }

    def load_selected_date(self, item):
        row = item.row()
        date_txt = self.table_hist.item(row, 0).text()
        qd = QDate.fromString(date_txt, "yyyy-MM-dd")
        if qd.isValid():
            self.d_date.setDate(qd)
            self.load_machine_issue_data()

    def delete_today(self):
        date_val = self.d_date.date().toPyDate()

        confirm = QMessageBox.warning(
            self,
            "ยืนยันการลบ",
            f"⚠️ ต้องการลบข้อมูลวันที่ {date_val} หรือไม่?\nข้อมูลนี้จะหายถาวร!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM WH1_OilDailyReport WHERE oil_date=?", (date_val,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "สำเร็จ", f"ลบข้อมูลวันที่ {date_val} เรียบร้อยแล้ว")

        self.load_history()
        self.clear_form()
        self.adjust_table_height()

    def load_history(self):
        conn = get_connection()
        cur = conn.cursor()
        offset = self.page * 10

        cur.execute(f"""
            SELECT oil_date,
                   COUNT(DISTINCT tank_no) AS cnt_tank,
                   SUM(oil_prev),
                   SUM(oil_in),
                   SUM(oil_bill_out),
                   SUM(oil_balance)
            FROM WH1_OilDailyReport
            GROUP BY oil_date
            ORDER BY oil_date DESC
            OFFSET {offset} ROWS FETCH NEXT 10 ROWS ONLY
        """)

        rows = cur.fetchall()
        conn.close()

        self.table_hist.setRowCount(0)
        for row_data in rows:
            r = self.table_hist.rowCount()
            self.table_hist.insertRow(r)
            for c, val in enumerate(row_data):
                if c >= 2:
                    text = self.fmt_num(val)
                else:
                    text = str(val)
                item = QTableWidgetItem(text)
                if c in [0,1]:
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_hist.setItem(r, c, item)

        self.btn_prev.setEnabled(self.page > 0)
        self.btn_next.setEnabled(len(rows) == 10)

    def add_machine_row(self):
        from db import get_machines

        r = self.tbl_machine.rowCount()
        self.tbl_machine.insertRow(r)

        # tank_no
        cb_tank = QComboBox()
        cb_tank.setEditable(False)
        cb_tank.addItems([str(t) for t in self.tanks])
        cb_tank.setFont(QFont("THSarabunNew", 18))
        self.tbl_machine.setCellWidget(r, 0, cb_tank)

        # machine_name
        cb_machine = QComboBox()
        cb_machine.setEditable(True)
        cb_machine.addItems(get_machines())
        cb_machine.setFont(QFont("THSarabunNew", 18))
        self.tbl_machine.setCellWidget(r, 1, cb_machine)

        # net only (editable)
        item = QTableWidgetItem("")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
        self.tbl_machine.setItem(r, 2, item)

    def load_machine_issue_data(self):
        from db import get_connection, get_machines

        date_val = self.d_date.date().toPyDate()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT tank_no, machine_name, meter_net
            FROM WH1_OilMachineIssue
            WHERE issue_date=?
            ORDER BY tank_no, machine_name
        """, (date_val,))
        rows = cur.fetchall()
        conn.close()

        machine_list = get_machines()

        self.tbl_machine.blockSignals(True)
        self.tbl_machine.setRowCount(0)

        for row_data in rows:
            r = self.tbl_machine.rowCount()
            self.tbl_machine.insertRow(r)

            # tank_no
            cb_tank = QComboBox()
            cb_tank.setEditable(False)
            cb_tank.addItems([str(t) for t in self.tanks])
            cb_tank.setCurrentText(str(row_data[0]))
            self.tbl_machine.setCellWidget(r, 0, cb_tank)

            # machine
            cb_machine = QComboBox()
            cb_machine.setEditable(True)
            cb_machine.addItems(machine_list)
            cb_machine.setCurrentText(row_data[1])
            self.tbl_machine.setCellWidget(r, 1, cb_machine)

            # net
            item = QTableWidgetItem(f"{float(row_data[2]):,.0f}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
            self.tbl_machine.setItem(r, 2, item)

        self.tbl_machine.blockSignals(False)


    def save_machine_issue_data(self):
        from db import get_connection

        date_val = self.d_date.date().toPyDate()

        conn = get_connection()
        cur = conn.cursor()

        # ลบข้อมูลเก่าในวันเดียวกัน
        cur.execute("DELETE FROM WH1_OilMachineIssue WHERE issue_date=?", (date_val,))

        def to_float(txt):
            try:
                return float(txt.replace(",", ""))
            except:
                return 0.0

        # บันทึกเฉพาะข้อมูล 3 คอลัมน์: tank, machine, net
        for r in range(self.tbl_machine.rowCount()):

            cb_tank = self.tbl_machine.cellWidget(r, 0)
            cb_machine = self.tbl_machine.cellWidget(r, 1)

            tank_no = cb_tank.currentText().strip() if cb_tank else ""
            machine = cb_machine.currentText().strip() if cb_machine else ""

            # net อยู่ column 2
            net_item = self.tbl_machine.item(r, 2)
            net = to_float(net_item.text()) if net_item else 0.0

            cur.execute("""
                INSERT INTO WH1_OilMachineIssue(issue_date, tank_no, machine_name, meter_net)
                VALUES (?, ?, ?, ?)
            """, (date_val, tank_no, machine, net))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "สำเร็จ", f"บันทึกข้อมูลจ่ายน้ำมัน {date_val} เรียบร้อยแล้ว")

    def on_machine_net_changed(self, item):
        """อัปเดตค่ามิเตอร์สุทธิจากตารางเครื่องจักร → ตารางหลัก (แยกตามถัง)"""

        if not item:
            return

        row = item.row()
        col = item.column()

        # ทำงานเฉพาะคอลัมน์ "สุทธิ" (index 2)
        if col != 2:
            return

        # อ่านหมายเลขถังของแถวนั้น
        cb_tank = self.tbl_machine.cellWidget(row, 0)
        if not cb_tank:
            return

        tank_no = cb_tank.currentText().strip()
        if not tank_no:
            return

        # ------------------------------------------
        # รวมยอดมิเตอร์สุทธิของถังนั้นทั้งหมดใน tbl_machine
        # ------------------------------------------
        total_net = 0
        for r in range(self.tbl_machine.rowCount()):
            cb = self.tbl_machine.cellWidget(r, 0)
            if not cb:
                continue

            if cb.currentText().strip() == tank_no:
                net_item = self.tbl_machine.item(r, 2)
                if net_item:
                    try:
                        total_net += float(net_item.text().replace(",", ""))
                    except:
                        pass

        # ------------------------------------------
        # อัปเดตกลับตารางหลัก (column 10 = ยอดตามมิเตอร์)
        # ------------------------------------------
        self.table.blockSignals(True)  # ป้องกันการ loop

        for r in range(self.table.rowCount()):
            cb_main = self.table.cellWidget(r, 0)
            if not cb_main:
                continue

            # ข้ามแถวรวม
            if cb_main.currentText().strip() == "รวม":
                continue

            if cb_main.currentText().strip() == tank_no:

                # อัปเดต column 10 (ยอดตามมิเตอร์)
                cell = self.table.item(r, 10)
                if cell:
                    cell.setText(f"{total_net:,.0f}")
                    cell.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                # คำนวณค่าทั้งแถวใหม่
                self.recalculate_row(r)

        self.table.blockSignals(False)

        # อัปเดตแถวรวม (ต้องเรียกหลังปลด blockSignals)
        self.update_total_row()

    def clear_machine_issue_form(self):
        self.tbl_machine.setRowCount(0)

    def delete_machine_issue_today(self):
        from db import get_connection
        date_val = self.d_date.date().toPyDate()

        confirm = QMessageBox.warning(
            self, "ยืนยันการลบ",
            f"ต้องการลบข้อมูลจ่ายน้ำมันของวันที่ {date_val} หรือไม่?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM WH1_OilMachineIssue WHERE issue_date=?", (date_val,))
        conn.commit()
        conn.close()

        self.tbl_machine.setRowCount(0)
        QMessageBox.information(self, "ลบสำเร็จ", f"ลบข้อมูลวันที่ {date_val} เรียบร้อยแล้ว")

    def next_page(self):
        """เลื่อนไปหน้าถัดไปของข้อมูลย้อนหลัง"""
        self.page += 1
        self.load_history()

    def prev_page(self):
        """เลื่อนไปหน้าก่อนหน้า"""
        if self.page > 0:
            self.page -= 1
        self.load_history()
