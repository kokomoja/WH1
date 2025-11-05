# utils_excel.py
from openpyxl import Workbook

def export_tablewidget_to_excel(table_widget, path: str):
    """ส่งออก QTableWidget เป็นไฟล์ Excel (.xlsx)"""
    wb = Workbook()
    ws = wb.active

    headers = [
        table_widget.horizontalHeaderItem(c).text()
        for c in range(table_widget.columnCount())
    ]
    ws.append(headers)

    for r in range(table_widget.rowCount()):
        row_vals = []
        for c in range(table_widget.columnCount()):
            item = table_widget.item(r, c)
            row_vals.append(item.text() if item else "")
        ws.append(row_vals)

    wb.save(path)
