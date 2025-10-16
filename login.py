from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QMessageBox
from db import auth_user

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FM-OP-01 | Login")
        self.resize(350, 200)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Username"))
        self.ed_user = QLineEdit()
        layout.addWidget(self.ed_user)

        layout.addWidget(QLabel("Password"))
        self.ed_pass = QLineEdit()
        self.ed_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.ed_pass)

        self.ed_user.setText("1")
        self.ed_pass.setText("1")
        
        self.cb_show = QCheckBox("แสดงรหัสผ่าน")
        self.cb_show.stateChanged.connect(self.toggle_password)
        layout.addWidget(self.cb_show)

        row = QHBoxLayout()
        btn_ok = QPushButton("เข้าสู่ระบบ")
        btn_cancel = QPushButton("ยกเลิก")
        row.addWidget(btn_ok)
        row.addWidget(btn_cancel)
        layout.addLayout(row)

        btn_ok.clicked.connect(self.check_login)
        btn_cancel.clicked.connect(self.reject)

        self.username = None

    def toggle_password(self):
        self.ed_pass.setEchoMode(QLineEdit.Normal if self.cb_show.isChecked() else QLineEdit.Password)

    def check_login(self):
        u, p = self.ed_user.text().strip(), self.ed_pass.text().strip()
        if not u or not p:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณากรอก Username/Password")
            return
        user = auth_user(u, p)
        if user:
            self.username = user["username"]
            QMessageBox.information(self, "สำเร็จ", f"เข้าสู่ระบบเรียบร้อย ✅\nยินดีต้อนรับ {self.username}")
            self.accept()
        else:
            QMessageBox.critical(self, "ผิดพลาด", "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง ❌")
