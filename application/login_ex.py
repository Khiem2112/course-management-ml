import json
import hashlib
import sys, os

from PyQt6.QtWidgets import QMainWindow, QMessageBox, QLineEdit, QApplication
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt, QRect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.login import Ui_MainWindow
from media.resource_from_qt import *


class LoginApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # UI FIXED SIZE
        self.fixed_width = self.width()
        self.fixed_height = self.height()

        # JSON path
        self.json_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "media", "Email.json"
        )

        # Load danh sách user từ email.json
        self.users = self.load_users()

        # UI setup
        self.setup_icons()
        # Mặc định vào trang Welcome
        self.stackedWidget.setCurrentIndex(0)

        # ===== CHUYỂN TRANG =====
        self.btn_Login.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btn_Register.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.btn_Back.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_Back_2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_Back_3.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btn_ForgotPass.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))

        self.btn_Register_2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.btn_Login_3.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        # Buttons
        self.btn_Login_2.clicked.connect(self.login)
        self.btn_Register_4.clicked.connect(self.register)
        self.Finish_btn.clicked.connect(self.reset_password)

        # Email check icon
        self.email_status_action = QAction(self.Email_LineEdit)
        self.Email_LineEdit.addAction(self.email_status_action, QLineEdit.ActionPosition.TrailingPosition)
        self.email_status_action.setVisible(False)
        self.Email_LineEdit.textChanged.connect(self.check_email)

        # Password toggles
        self.add_toggle_action(self.Password_LineEdit)
        self.add_toggle_action(self.Password_LineEdit_2)
        self.add_toggle_action(self.NewPassword_LineEdit)
        self.add_toggle_action(self.RePassword_LineEdit)

        # Center UI when open
        self.center_window()
        self.setFixedSize(self.width(), self.height())  # giữ fixed size đúng ý bạn

    # Keep form at center even fullscreen
    def center_window(self):
        # Lấy màn hình chính
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Lấy kích thước cửa sổ login
        window_geometry = self.frameGeometry()

        # Tính vị trí trung tâm
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)

        # Di chuyển cửa sổ tới đúng vị trí
        self.move(window_geometry.topLeft())

    # Logo
    def setup_icons(self):
        self.image1.setPixmap(QPixmap(":/Images/images/Logo DUKI.png"))
        self.image2.setPixmap(QPixmap(":/Images/images/Logo DUKI.png"))
        self.image3.setPixmap(QPixmap(":/Images/images/Logo DUKI.png"))
        self.image4.setPixmap(QPixmap(":/Images/images/Logo DUKI.png"))


    # =================== JSON ===================
    def load_users(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_users(self):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=4, ensure_ascii=False)


    # =================== CHỨC NĂNG ===================
    def hash_password(self, pwd: str):
        return hashlib.sha256(pwd.encode()).hexdigest()

    # Check email exists
    def check_email(self):
        email = self.Email_LineEdit.text().strip()

        if not email:
            self.email_status_action.setVisible(False)
            return

        exists = any(u["email"] == email for u in self.users)
        icon = ":/Icons/images/icons/Login/check.png" if exists else ":/Icons/images/icons/Login/x.png"

        self.email_status_action.setIcon(QIcon(icon))
        self.email_status_action.setVisible(True)

    # Hide / Show password
    def add_toggle_action(self, line_edit):
        icon_open = QIcon(":/Icons/images/icons/Login/eye_open.png")
        icon_closed = QIcon(":/Icons/images/icons/Login/eye_closed.png")

        action = QAction(icon_open, "", line_edit)
        line_edit.addAction(action, QLineEdit.ActionPosition.TrailingPosition)
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)

        def toggle():
            if line_edit.echoMode() == QLineEdit.EchoMode.Password:
                line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
                action.setIcon(icon_closed)
            else:
                line_edit.setEchoMode(QLineEdit.EchoMode.Password)
                action.setIcon(icon_open)

        action.triggered.connect(toggle)

    # Login
    def login(self):
        email = self.Email_LineEdit.text().strip()
        pwd = self.Password_LineEdit.text()

        missing = []
        if not email:
            missing.append("Email")
        if not pwd:
            missing.append("Password")

        if missing:
            QMessageBox.warning(self, "Thiếu thông tin", f"Vui lòng nhập: {', '.join(missing)}")
            return

        hashed_pwd = self.hash_password(pwd)
        user = next((u for u in self.users if u["email"] == email), None)

        if not user:
            return QMessageBox.warning(self, "Login", "Email không tồn tại!")

        if user["password"] == hashed_pwd:
            QMessageBox.information(self, "Login", f"Xin chào {user['username']}!")
        else:
            QMessageBox.warning(self, "Login", "Sai mật khẩu!")

    # Register
    def register(self):
        user = self.UserName_LineEdit.text().strip()
        email = self.Email_LineEdit_2.text().strip()
        pwd = self.Password_LineEdit_2.text()

        missing = []
        if not user:
            missing.append("User Name")
        if not email:
            missing.append("Email")
        if not pwd:
            missing.append("Password")

        if missing:
            QMessageBox.warning(self, "Thiếu thông tin", f"Vui lòng nhập: {', '.join(missing)}")
            return

        if any(u["email"] == email for u in self.users):
            return QMessageBox.warning(self, "Register", "Email đã tồn tại!")

        self.users.append({
            "username": user,
            "email": email,
            "password": self.hash_password(pwd),
            "password_plain": pwd
        })
        self.save_users()

        QMessageBox.information(self, "Register", "Tạo tài khoản thành công!")
        self.stackedWidget.setCurrentIndex(1)

    # Reset password
    def reset_password(self):
        email = self.Email_LineEdit.text().strip()
        new_pwd = self.NewPassword_LineEdit.text()
        re_pwd = self.RePassword_LineEdit.text()

        missing = []
        if not email:
            missing.append("Email")
        if not new_pwd:
            missing.append("Mật khẩu mới")
        if not re_pwd:
            missing.append("Xác nhận mật khẩu")

        if missing:
            QMessageBox.warning(self, "Thiếu thông tin", f"Vui lòng nhập: {', '.join(missing)}")
            return

        if new_pwd != re_pwd:
            return QMessageBox.warning(self, "Reset", "Xác nhận mật khẩu không khớp!")

        for u in self.users:
            if u["email"] == email:
                u["password"] = self.hash_password(new_pwd)
                u["password_plain"] = new_pwd
                self.save_users()
                QMessageBox.information(self, "Reset", "Đổi mật khẩu thành công!")
                self.stackedWidget.setCurrentIndex(1)
                return

        QMessageBox.warning(self, "Reset", "Email không tồn tại!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())
