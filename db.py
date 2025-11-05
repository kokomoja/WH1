import pyodbc
from datetime import date
from utils import info, warn

# ----------------------------------------
# 🔗 การเชื่อมต่อ SQL Server
# ----------------------------------------
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=192.168.99.253,1433;"
        "DATABASE=wh1Db;"
        "UID=sa;PWD=@1234"
    )


def list_records(filters=None):
    conn = get_connection()
    cur = conn.cursor()

    q = """
        SELECT 
            H.WH1_id,
            H.WH1_date,
            H.WH1_SM,
            H.WH1_lighter,
            H.WH1_start,
            H.WH1_stop,
            I.product_name AS WH1_product,
            I.qty_bag AS WH1_blQty,
            I.qty_ton AS WH1_blMt,
            H.WH1_remark
        FROM WH1FMOP01 H
        LEFT JOIN WH1FMOP01_items I ON H.WH1_id = I.WH1_id
        WHERE 1=1
    """

    params = []
    if filters:
        if "date_from" in filters and filters["date_from"]:
            q += " AND H.WH1_date >= ?"
            params.append(filters["date_from"])
        if "date_to" in filters and filters["date_to"]:
            q += " AND H.WH1_date <= ?"
            params.append(filters["date_to"])
        if "sm" in filters and filters["sm"]:
            q += " AND H.WH1_SM = ?"
            params.append(filters["sm"])

        if "lighter" in filters and filters["lighter"]:
            q += " AND H.WH1_lighter = ?"
            params.append(filters["lighter"])

        if "product" in filters and filters["product"]:
            q += " AND I.product_name = ?"
            params.append(filters["product"])


    q += " ORDER BY H.WH1_date DESC, H.WH1_id DESC"

    cur.execute(q, params)
    rows = [
        dict((cur.description[i][0], value) for i, value in enumerate(row))
        for row in cur.fetchall()
    ]
    conn.close()
    return rows



# ----------------------------------------
# ➕ เพิ่มข้อมูลหัวเอกสาร
# ----------------------------------------
def create_record(header):
    conn = get_connection()
    cur = conn.cursor()
    q = """
        INSERT INTO WH1FMOP01
        (WH1_date, WH1_SM, WH1_lighter, WH1_start, WH1_stop, WH1_remark)
        OUTPUT INSERTED.WH1_id
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (
        header["WH1_date"],
        header["WH1_SM"],
        header["WH1_lighter"],
        header["WH1_start"],
        header["WH1_stop"],
        header["WH1_remark"],
    )
    cur.execute(q, params)
    new_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return new_id


# ----------------------------------------
# 📦 เพิ่มรายการสินค้า
# ----------------------------------------
def create_item_record(wh1_id, product_name, qty_bag, qty_ton):
    conn = get_connection()
    cur = conn.cursor()
    q = """
        INSERT INTO WH1FMOP01_items (WH1_id, product_name, qty_bag, qty_ton)
        VALUES (?, ?, ?, ?)
    """
    cur.execute(q, (wh1_id, product_name, qty_bag, qty_ton))
    conn.commit()
    conn.close()

# === ดึงเฉพาะหัวเอกสาร ไม่ join ===
def list_headers():
    conn = get_connection()
    cur = conn.cursor()
    q = """
        SELECT WH1_id, WH1_date, WH1_SM, WH1_lighter,
               WH1_start, WH1_stop, WH1_remark
        FROM WH1FMOP01
        ORDER BY WH1_date DESC, WH1_id DESC
    """
    cur.execute(q)
    rows = [
        dict((cur.description[i][0], value) for i, value in enumerate(row))
        for row in cur.fetchall()
    ]
    conn.close()
    return rows


# === ดึงรายการสินค้าในเอกสารแต่ละใบ ===
def list_item_records(wh1_id):
    conn = get_connection()
    cur = conn.cursor()
    q = """
        SELECT product_name, qty_bag, qty_ton
        FROM WH1FMOP01_items
        WHERE WH1_id = ?
        ORDER BY item_id ASC
    """
    cur.execute(q, (wh1_id,))
    rows = [
        dict((cur.description[i][0], value) for i, value in enumerate(row))
        for row in cur.fetchall()
    ]
    conn.close()
    return rows



# ----------------------------------------
# ✏️ อัปเดตเอกสารหลัก
# ----------------------------------------
def update_record(record_id, header):
    conn = get_connection()
    cur = conn.cursor()
    q = """
        UPDATE WH1FMOP01
        SET WH1_date=?, WH1_SM=?, WH1_lighter=?, WH1_start=?, WH1_stop=?, WH1_remark=?
        WHERE WH1_id=?
    """
    params = (
        header["WH1_date"],
        header["WH1_SM"],
        header["WH1_lighter"],
        header["WH1_start"],
        header["WH1_stop"],
        header["WH1_remark"],
        record_id,
    )
    cur.execute(q, params)
    conn.commit()
    conn.close()


# ----------------------------------------
# 🗑️ ลบข้อมูลเอกสาร + รายการสินค้า
# ----------------------------------------
def delete_record(record_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM WH1FMOP01_items WHERE WH1_id=?", (record_id,))
    cur.execute("DELETE FROM WH1FMOP01 WHERE WH1_id=?", (record_id,))
    conn.commit()
    conn.close()


def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT product_name FROM WH1_Products ORDER BY product_name ASC")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows

def get_sm_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT WH1_SM FROM WH1FMOP01 ORDER BY WH1_SM")
    rows = [r[0] for r in cur.fetchall() if r[0]]
    conn.close()
    return rows

def get_lighters():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT WH1_lighter FROM WH1FMOP01 ORDER BY WH1_lighter")
    rows = [r[0] for r in cur.fetchall() if r[0]]
    conn.close()
    return rows


def add_product(name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO WH1_Products (product_name) VALUES (?)", (name,))
        conn.commit()
    except Exception as e:
        print("⚠️ Error adding product:", e)
    finally:
        conn.close()



# ----------------------------------------
# 🔐 ตรวจสอบผู้ใช้เข้าสู่ระบบ
# ----------------------------------------
def auth_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    q = "SELECT user_id, username FROM WH1_users WHERE username=? AND password=?"
    cur.execute(q, (username, password))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"user_id": row[0], "username": row[1]}
    else:
        return None

def delete_items_by_header(wh1_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM WH1FMOP01_items WHERE WH1_id=?", (wh1_id,))
    conn.commit()
    conn.close()

def get_latest_revision():
    """ดึงข้อมูลล่าสุดจาก WH1_Revision (id มากสุด)"""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT TOP 1 wh1rev_code, wh1rev_rev, wh1rev_eff
            FROM WH1_Revision
            ORDER BY wh1rev_id DESC
        """)
        row = cur.fetchone()
        if row:
            return {
                "wh1rev_code": row[0],
                "wh1rev_rev": row[1],
                "wh1rev_eff": str(row[2])
            }
        else:
            return None

def list_revisions():
    """อ่านข้อมูลทั้งหมดจาก WH1_Revision"""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT wh1rev_id, wh1rev_code, wh1rev_rev, wh1rev_eff FROM WH1_Revision ORDER BY wh1rev_id DESC")
        columns = [col[0] for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def insert_revision(code, rev, eff_date):
    """เพิ่มข้อมูลใหม่"""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO WH1_Revision (wh1rev_code, wh1rev_rev, wh1rev_eff) VALUES (?, ?, ?)",
            (code, rev, eff_date)
        )
        conn.commit()

def update_revision(rev_id, code, rev, eff_date):
    """แก้ไขข้อมูล"""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE WH1_Revision SET wh1rev_code=?, wh1rev_rev=?, wh1rev_eff=? WHERE wh1rev_id=?",
            (code, rev, eff_date, rev_id)
        )
        conn.commit()

def delete_revision(rev_id):
    """ลบข้อมูล"""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM WH1_Revision WHERE wh1rev_id=?", (rev_id,))
        conn.commit()