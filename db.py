import pyodbc
from datetime import date, time

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


# ----------------------------------------
# 📋 ดึงข้อมูลเอกสารหลัก
# ----------------------------------------
def list_records():
    conn = get_connection()
    cur = conn.cursor()
    q = """
        SELECT WH1_id, WH1_date, WH1_SM, WH1_lighter, WH1_start, WH1_stop, WH1_remark
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


# ----------------------------------------
# 📦 ดึงรายการสินค้า
# ----------------------------------------
def list_item_records(wh1_id):
    conn = get_connection()
    cur = conn.cursor()
    q = "SELECT product_name, qty_bag, qty_ton FROM WH1FMOP01_items WHERE WH1_id=?"
    cur.execute(q, (wh1_id,))
    rows = [
        {"product_name": r[0], "qty_bag": r[1], "qty_ton": r[2]}
        for r in cur.fetchall()
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


# ----------------------------------------
# 📦 ดึงและเพิ่มสินค้าในคลัง
# ----------------------------------------
def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT product_name FROM WH1_Products ORDER BY product_name ASC")
    rows = [r[0] for r in cur.fetchall()]
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
