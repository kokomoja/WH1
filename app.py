import sys, os, logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFontDatabase, QFont
from login import LoginDialog
from menu import MenuWindow
from config import FONTS, APP_STYLESHEET

logging.basicConfig(level=logging.INFO)


def load_fonts(paths):
    """โหลดฟอนต์จาก paths ที่กำหนด (เฉพาะไฟล์ที่มีอยู่จริง)"""
    loaded = []
    for path in paths:
        if os.path.exists(path):
            fid = QFontDatabase.addApplicationFont(path)
            if fid != -1:
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams:
                    loaded.append(fams[0])
                    logging.info("✅ โหลดฟอนต์สำเร็จ: %s", fams[0])
        else:
            logging.warning("⚠️ ไม่พบไฟล์ฟอนต์: %s", path)
    return loaded


def main():
    app = QApplication(sys.argv)
    fams = load_fonts(FONTS)

    # ✅ ถ้ามีฟอนต์ TH Sarabun ให้ใช้
    if fams:
        app.setFont(QFont(fams[0], 18))
        logging.info("🟢 ใช้ฟอนต์หลัก: %s", fams[0])

        # ✅ ปรับฟอนต์ popup และปุ่มให้ใหญ่ขึ้น
        app.setStyleSheet(APP_STYLESHEET + """
            QMessageBox, QDialog {
                font-family: '%s';
                font-size: 20px;
            }
            QMessageBox QPushButton, QDialog QPushButton {
                font-size: 12px;
                padding: 4px 12px;
                border: 1px solid #bdbdbd;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover, QDialog QPushButton:hover {
                background-color: #f0f0f0;
            }
        """ % fams[0])

    else:
        # ❌ ถ้าไม่มีฟอนต์เลย ให้ fallback ไปใช้ Tahoma พร้อมแจ้งเตือน
        app.setFont(QFont("Tahoma", 10))
        QMessageBox.warning(
            None,
            "Font Missing",
            (
                "⚠️ ไม่พบฟอนต์ TH Sarabun ในโฟลเดอร์ fonts/\n\n"
                "ระบบจะใช้ฟอนต์ Tahoma แทนชั่วคราว.\n"
                "หากต้องการให้แสดงผลสวยงาม โปรดวางไฟล์:\n"
                "fonts/THSarabunNew.ttf\n"
                "ในโฟลเดอร์เดียวกับโปรแกรมนี้."
            ),
        )
        logging.warning("⚠️ ไม่พบฟอนต์ Sarabun ใช้ Tahoma แทน")

        # ✅ ใช้สไตล์ default
        app.setStyleSheet(APP_STYLESHEET)

    # 🔐 เปิดหน้าล็อกอิน
    login = LoginDialog()
    if login.exec_() == login.Accepted:
        mw = MenuWindow(login.username or "user")
        mw.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
