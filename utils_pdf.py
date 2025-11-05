# utils_pdf.py
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from db import get_latest_revision
import os


# ============================================================
# 🔹 ฟังก์ชันลงทะเบียนฟอนต์ TH Sarabun
# ============================================================
def _register_th_sarabun():
    """ลงทะเบียนฟอนต์ TH Sarabun (Regular/Bold)"""
    font_dir = "fonts"
    regular_path = os.path.join(font_dir, "THSarabunNew.ttf")
    bold_path = os.path.join(font_dir, "THSarabunNew-Bold.ttf")

    try:
        if os.path.exists(regular_path):
            pdfmetrics.registerFont(TTFont("THSarabunNew", regular_path))
            print(f"✅ Register font: {regular_path}")
        else:
            print(f"⚠️ ไม่พบฟอนต์หลัก {regular_path}")

        if os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont("THSarabunNew-Bold", bold_path))
            print(f"✅ Register bold font: {bold_path}")
        else:
            print(f"⚠️ ไม่พบฟอนต์หนา {bold_path}")

    except Exception as e:
        print("⚠️ Error registering fonts:", e)


# ============================================================
# 🔹 สร้างรายงาน WH1 แนวนอน (PDF)
# ============================================================
def build_wh1_report_pdf(path: str, rows: list, title_text: str, subtitle_text: str):
    """สร้างรายงาน WH1 แนวนอน A4 จาก rows (list of dict)"""
    _register_th_sarabun()

    # ✅ ตั้งค่าเอกสาร
    doc = SimpleDocTemplate(
        path,
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
    )

    # ✅ สไตล์พื้นฐาน
    styles = getSampleStyleSheet()

    style_header = styles["Title"]
    style_header.fontName = "THSarabunNew-Bold"
    style_header.fontSize = 22
    style_header.alignment = 1
    style_header.leading = 20

    style_normal = styles["Normal"]
    style_normal.fontName = "THSarabunNew"
    style_normal.fontSize = 18
    style_normal.alignment = 1
    style_normal.leading = 20

    style_small = ParagraphStyle(
        "small",
        parent=style_normal,
        fontName="THSarabunNew",
        fontSize=10,
        leading=12,
        alignment=0,
    )

    story = []

    # ============================================================
    # 🔹 ส่วนหัวรายงาน
    # ============================================================
    rev = get_latest_revision()

    # หัวรายงานฝั่งซ้าย
    left_data = [
        [Paragraph("บริษัท พี.ซี.ปิโตรเลียมแอนด์เทอร์มินอล จำกัด", style_header)],
        [Paragraph("รายงานปฏิบัติการขนถ่ายสินค้า ประเภท ปูนถุงจัมโบ้", style_normal)],
        [Paragraph("คลังสินค้า 1 ท่าเรือพี.ซี.เทอร์มินอล", style_normal)],
    ]

    # กล่อง Revision ฝั่งขวา
    if rev:
        right_data = [
            [f"{rev['wh1rev_code']}"],
            [f"REV : {rev['wh1rev_rev']}"],
            [f"Effective Date : {rev['wh1rev_eff']}"],
        ]
        rev_box = Table(
            right_data,
            colWidths=[5 * cm],
            rowHeights=[0.5 * cm] * 3,
            style=TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "THSarabunNew"),
                ("FONTSIZE", (0, 0), (-1, -1), 14),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
    else:
        rev_box = Table([[Paragraph("", style_normal)]], colWidths=[5 * cm])

    # รวมตารางหัวรายงาน
    header_table = Table(
        [[
            Table(
                left_data,
                style=TableStyle([
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 150),
                ])
            ),
            rev_box
        ]],
        colWidths=[23 * cm, 5 * cm],
        style=TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ])
    )

    story += [header_table, Spacer(1, 15)]

    # ============================================================
    # 🔹 ตารางข้อมูลหลัก
    # ============================================================
    data = [["วันที่", "เวลาเริ่ม", "เวลาสิ้นสุด", "เที่ยวเรือ", "ชื่อเรือ", "ชื่อสินค้า", "จำนวน(ถุง)", "น้ำหนัก (ตัน)", "หมายเหตุ"]]
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
            f"{bag:,.2f}",
            f"{ton:,.2f}",
            str(r.get("WH1_remark") or ""),
        ])

    data.append(["", "", "", "", "", "รวมทั้งหมด", f"{total_bag:,.2f}", f"{total_ton:,.2f}", ""])

    table = Table(
        data,
        colWidths=[2.5 * cm, 2.5 * cm, 2.5 * cm, 2.0 * cm, 3.0 * cm, 5.0 * cm, 2.5 * cm, 2.5 * cm, 5.0 * cm],
    )

    table.setStyle(TableStyle([
        # ฟอนต์
        ("FONTNAME", (0, 0), (-1, -1), "THSarabunNew"),
        ("FONTSIZE", (0, 0), (-1, -1), 14),

        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "THSarabunNew-Bold"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),

        # เนื้อหา
        ("ALIGN", (0, 1), (5, -2), "CENTER"),
        ("ALIGN", (6, 1), (7, -2), "RIGHT"),
        ("VALIGN", (0, 1), (-1, -2), "MIDDLE"),

          # ✅ เพิ่มตรงนี้ (align คอลัมน์ "หมายเหตุ")
        ("ALIGN", (8, 1), (8, -2), "LEFT"),     # หมายเหตุ → ชิดซ้าย
        ("VALIGN", (8, 1), (8, -1), "MIDDLE"),  # จัดกลางแนวตั้ง

        # รวมผลรวม
        ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke),
        ("FONTNAME", (0, -1), (-1, -1), "THSarabunNew"),
        ("ALIGN", (0, -1), (5, -1), "CENTER"),
        ("ALIGN", (6, -1), (7, -1), "RIGHT"),
        ("ALIGN", (8, -1), (8, -1), "LEFT"),

        # เส้นตารางและระยะบรรทัด
        ("LEADING", (0, 0), (-1, -1), 14),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story += [table, Spacer(1, 15)]

    # ============================================================
    # 🔹 ส่วนท้ายรายงาน (ผู้รายงาน / หมายเหตุ)
    # ============================================================
    sign_block = [
        ["_______________", "_______________", "_______________"],
        ["ผู้รายงาน", "ผู้ตรวจสอบ", "หัวหน้าคลังสินค้า"],
    ]

    sign_table = Table(
        sign_block,
        colWidths=[6 * cm, 6 * cm, 6 * cm],
        style=TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "THSarabunNew"),
            ("FONTSIZE", (0, 0), (-1, 1), 14),
            ("ALIGN", (0, 0), (-1, 1), "CENTER"),
            ("VALIGN", (0, 0), (-1, 1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )

    main_col_widths = table._argW

    note_block = [[
        Paragraph("หมายเหตุ :", style_small),
        "",
        "",
        "",
        "",
        "",
        "",
        Paragraph("จัดเก็บเข้าแฟ้ม ... 2 ปี", style_small),
    ]]

    note_table = Table(
        note_block,
        colWidths=main_col_widths,
        style=TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "THSarabunNew"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (8, 0), (8, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 15),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),


            
        ])
    )

    story.append(sign_table)
    story.append(note_table)

    # ============================================================
    # 🔹 สร้างเอกสาร
    # ============================================================
    doc.build(story)
