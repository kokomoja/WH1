import sys, os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont
from login import LoginDialog
from menu import MenuWindow

def main():
    app = QApplication(sys.argv)

    # ===== โหลดฟอนต์ TH Sarabun =====
    font_paths = [
        os.path.join("fonts", "THSarabunNew.ttf"),
        os.path.join("fonts", "THSarabunNew Bold.ttf"),
        os.path.join("fonts", "THSarabunNew Italic.ttf"),
        os.path.join("fonts", "THSarabunNew BoldItalic.ttf"),
    ]

    loaded_fonts = []
    for path in font_paths:
        if os.path.exists(path):
            font_id = QFontDatabase.addApplicationFont(path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                loaded_fonts.extend(families)
                print(f"✅ โหลดฟอนต์: {families[0]}")
            else:
                print(f"⚠️ โหลดฟอนต์ไม่สำเร็จ: {path}")
        else:
            print(f"ℹ️ ไม่พบไฟล์ฟอนต์: {path}")

    # ตั้งค่าฟอนต์เริ่มต้น
    if loaded_fonts:
        app.setFont(QFont(loaded_fonts[0], 18))
    else:
        app.setFont(QFont("Tahoma", 10))
        print("⚠️ ไม่มีฟอนต์ TH Sarabun ใช้ Tahoma แทน")

    # เริ่มโปรแกรม
    login = LoginDialog()
    if login.exec_() == login.Accepted:
        mw = MenuWindow(login.username or "user")
        mw.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
