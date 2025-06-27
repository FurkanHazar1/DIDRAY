import sys
import os
import cv2

from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QFileDialog, QLineEdit, QDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QFrame, QGridLayout, QProgressBar, QGroupBox, QComboBox
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from db_manager import DBManager
from detector_pt import PyTorchDetector
from video_stream import VideoStreamThread
from utils import get_model_path, get_icon_path


class ModernButton(QPushButton):
    """Modern styled button with hover effects"""
    def __init__(self, text, primary=False, danger=False):
        super().__init__(text)
        self.primary = primary
        self.danger = danger
        self.setStyleSheet(self.get_style())
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 7, QFont.Medium))
        
    def get_style(self):
        if self.danger:
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #e74c3c, stop:1 #c0392b);
                    color: white;
                    border: none;
                    padding: 12px 18px;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 8pt;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #ec7063, stop:1 #d5392b);
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #c0392b, stop:1 #a93226);
                }
                QPushButton:disabled {
                    background: #95a5a6;
                    color: #7f8c8d;
                }
            """
        elif self.primary:
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    border: none;
                    padding: 12px 18px;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 8pt;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #5dade2, stop:1 #3498db);
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #2980b9, stop:1 #1f4e79);
                }
                QPushButton:disabled {
                    background: #95a5a6;
                    color: #7f8c8d;
                }
            """
        else:
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #34495e, stop:1 #2c3e50);
                    color: white;
                    border: none;
                    padding: 12px 18px;
                    border-radius: 6px;
                    font-weight: 500;
                    font-size: 8pt;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #4a6278, stop:1 #34495e);
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #2c3e50, stop:1 #1b2631);
                }
                QPushButton:disabled {
                    background: #95a5a6;
                    color: #7f8c8d;
                }
            """

class ModernLineEdit(QLineEdit):
    """Modern styled line edit"""
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                background: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px 16px;
                color: white;
                font-size: 11pt;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: #34495e;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        self.setMinimumHeight(45)

class ModernCard(QFrame):
    """Modern card container"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: #2c3e50;
                border-radius: 12px;
                border: 1px solid #34495e;
            }
        """)
        self.setFrameStyle(QFrame.StyledPanel)

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.role = None
        self.username = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("X-Ray Security System - Login")
        icon_path = get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(550, 650)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #1a252f, stop:1 #2c3e50);
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(35)
        main_layout.setContentsMargins(45, 45, 45, 45)
        
        # Logo/Title area
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("DIDRAY SECURITY")
        title_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 26pt;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Dangerous Item Detection on X-Ray Scans")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 10pt;
                font-family: 'Segoe UI';
                margin-bottom: 20px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Login form card
        form_card = ModernCard()
        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(25)
        form_layout.setContentsMargins(35, 35, 35, 35)
        
        # Username input
        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #ecf0f1; font-weight: 600; margin-bottom: 5px;")
        self.username_input = ModernLineEdit("Enter your username")
        
        # Password input
        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #ecf0f1; font-weight: 600; margin-bottom: 5px;")
        self.password_input = ModernLineEdit("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # Login button
        self.login_btn = ModernButton("LOGIN", primary=True)
        self.login_btn.clicked.connect(self.login)
        
        # Add to form layout
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_btn)
        
        # Add to main layout
        main_layout.addWidget(title_frame)
        main_layout.addWidget(form_card)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Enable Enter key
        self.password_input.returnPressed.connect(self.login)
        self.username_input.returnPressed.connect(self.login)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        role = self.db.validate_user(username, password)
        if role:
            self.role = role
            self.username = username
            self.db.log_user_login(username, role)
            self.accept()
        else:
            msg = QMessageBox(self)
            msg.setStyleSheet("""
                QMessageBox {
                    background: #2c3e50;
                    color: white;
                }
                QMessageBox QPushButton {
                    background: #e74c3c;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 80px;
                }
            """)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Authentication Failed")
            msg.setText("Invalid username or password!")
            msg.exec_()

class AdminPanelDialog(QDialog):
    def __init__(self, db, role, current_user):
        super().__init__()
        self.db = db
        self.role = role
        self.current_user = current_user
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Administration Panel")
        self.setMinimumSize(1250, 1000)
        self.setStyleSheet("""
            QDialog {
                background: #1a252f;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40,40, 40, 40)
        
        # Header
        header = QLabel("User Management")
        header.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 24pt;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        
        # Users table card
        table_card = ModernCard()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(40, 40, 40, 40)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Actions"])
        
        # Tablo boyutlarını container'a sığdıracak şekilde ayarla
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, self.table.horizontalHeader().ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, self.table.horizontalHeader().ResizeToContents)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background: #34495e;
                color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #2c3e50;
            }
            QTableWidget::item {
                padding: 35px 25px;
                border-bottom: 1px solid #2c3e50;
            }
            QTableWidget::item:selected {
                background: #3498db;
            }
            QHeaderView::section {
                background: #2c3e50;
                color: white;
                padding: 25px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Satır yüksekliğini arttır
        self.table.verticalHeader().setDefaultSectionSize(80)
        
        table_layout.addWidget(self.table)
        
        # Add user form card - aynı kalıyor
        form_card = ModernCard()
        form_layout = QGridLayout(form_card)
        form_layout.setSpacing(25)
        form_layout.setContentsMargins(40, 40, 40, 40)
        
        form_title = QLabel("Add New User")
        form_title.setStyleSheet("color: #3498db; font-size: 16pt; font-weight: bold;")
        
        self.username_input = ModernLineEdit("Username")
        self.password_input = ModernLineEdit("Password")
        
        if self.role == "admin":
            self.role_combo = QComboBox()
            self.role_combo.addItems(["personel", "şef"])
            self.role_combo.setStyleSheet("""
                QComboBox {
                    background: #2c3e50;
                    border: 2px solid #34495e;
                    border-radius: 8px;
                    padding: 12px 16px;
                    color: white;
                    font-size: 11pt;
                    min-height: 21px;
                }
                QComboBox:focus {
                    border: 2px solid #3498db;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    width: 12px;
                    height: 12px;
                }
                QComboBox QAbstractItemView {
                    background: #2c3e50;
                    color: white;
                    border: 1px solid #34495e;
                    border-radius: 4px;
                }
            """)
        
        self.add_btn = ModernButton("Add User", primary=True)
        self.add_btn.clicked.connect(self.add_user)
        
        # Layout form with better spacing
        form_layout.addWidget(form_title, 0, 0, 1, 3)
        form_layout.addWidget(QLabel("Username:"), 1, 0)
        form_layout.addWidget(self.username_input, 1, 1, 1, 2)
        form_layout.addWidget(QLabel("Password:"), 2, 0)
        form_layout.addWidget(self.password_input, 2, 1, 1, 2)
        
        if self.role == "admin":
            form_layout.addWidget(QLabel("Role:"), 3, 0)
            form_layout.addWidget(self.role_combo, 3, 1, 1, 2)
            
        form_layout.addWidget(self.add_btn, 4, 1)
        
        # Style labels
        for i in range(form_layout.count()):
            widget = form_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget != form_title:
                widget.setStyleSheet("color: #ecf0f1; font-weight: 600;")
        
        # Add to main layout with better proportions
        main_layout.addWidget(header)
        main_layout.addWidget(table_card, 3)
        main_layout.addWidget(form_card, 1)
        
        self.setLayout(main_layout)
        self.load_users()

    def load_users(self):
        self.table.setRowCount(0)
        users = self.db.get_all_users()
        for row_idx, (user_id, username, role) in enumerate(users):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(user_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(username))
            self.table.setItem(row_idx, 2, QTableWidgetItem(role))
            
            btn_delete = ModernButton("Delete", danger=True)
            btn_delete.setMinimumWidth(80)
            btn_delete.setMaximumWidth(80)
            btn_delete.setMinimumHeight(40)
            btn_delete.clicked.connect(lambda _, uid=user_id, u=username: self.delete_user(uid, u))
            
            # Butonu doğrudan ekle
            self.table.setCellWidget(row_idx, 3, btn_delete)
    def add_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if self.role == "admin":
            role = self.role_combo.currentText()
        else:
            role = "personel"

        if username and password:
            self.db.add_user(username, password, role)
            self.db.add_log(self.current_user, f"{role} kullanıcısı eklendi: {username}")
            self.load_users()
            self.username_input.clear()
            self.password_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Please fill all fields!")

    def delete_user(self, user_id, username):
        if self.role == "şef":
            user = [u for u in self.db.get_all_users() if u[0] == user_id]
            if user and user[0][2] != "personel":
                QMessageBox.warning(self, "Permission Denied", "You can only delete personnel!")
                return
                
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete user '{username}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_user(user_id)
            self.db.add_log(self.current_user, f"Kullanıcı silindi: {username}")
            self.load_users()

class RecordViewerDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Detection History")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet("""
            QDialog {
                background: #1a252f;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Detection History")
        title.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 24pt;
                font-weight: bold;
            }
        """)
        
        self.export_btn = ModernButton("Export CSV", primary=True)
        self.export_btn.clicked.connect(self.export_csv)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.export_btn)
        
        # Table card
        table_card = ModernCard()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(25, 25, 25, 25)
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "Classes", "Confidences", "Mode",
            "Image Path", "Operator", "Role", "View", "Delete"
        ])
        
        self.table.setStyleSheet("""
            QTableWidget {
                background: #34495e;
                color: white;
                border: none;
                border-radius: 8px;
                gridline-color: #2c3e50;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #2c3e50;
            }
            QTableWidget::item:selected {
                background: #3498db;
            }
            QHeaderView::section {
                background: #2c3e50;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Set optimized column widths
        column_widths = [140, 220, 140, 90, 240, 120, 100, 100, 100]
        for i, width in enumerate(column_widths):
            self.table.setColumnWidth(i, width)
        
        table_layout.addWidget(self.table)
        
        # Add to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(table_card)
        
        self.setLayout(main_layout)
        self.load_data()

    def load_data(self):
        records = self.db.fetch_all_detections()
        self.table.setRowCount(len(records))

        for row_idx, record in enumerate(records):
            timestamp, classes, confs, mode, path, operator, role = record

            self.table.setItem(row_idx, 0, QTableWidgetItem(timestamp))
            self.table.setItem(row_idx, 1, QTableWidgetItem(classes))
            self.table.setItem(row_idx, 2, QTableWidgetItem(confs))
            self.table.setItem(row_idx, 3, QTableWidgetItem(mode))
            self.table.setItem(row_idx, 4, QTableWidgetItem(path))
            self.table.setItem(row_idx, 5, QTableWidgetItem(operator))
            self.table.setItem(row_idx, 6, QTableWidgetItem(role))

            # View button
            btn_show = ModernButton("View")
            btn_show.setMinimumWidth(80)
            btn_show.setMaximumWidth(80)
            btn_show.setMinimumHeight(35)
            btn_show.clicked.connect(lambda _, p=path: self.show_image(p))
            self.table.setCellWidget(row_idx, 7, btn_show)

            # Delete button
            btn_delete = ModernButton("Delete", danger=True)
            btn_delete.setMinimumWidth(80)
            btn_delete.setMaximumWidth(80)
            btn_delete.setMinimumHeight(35)
            btn_delete.clicked.connect(lambda _, t=timestamp, p=path: self.delete_record(t, p))
            self.table.setCellWidget(row_idx, 8, btn_delete)

    def delete_record(self, timestamp, path):
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this record?", 
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_detection(timestamp)
            if os.path.exists(path):
                os.remove(path)
            self.load_data()

    def show_image(self, path):
        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", "Image not found!")
            return
            
        viewer = QDialog(self)
        viewer.setWindowTitle("Image Preview")
        viewer.setStyleSheet("""
            QDialog {
                background: #2c3e50;
            }
        """)
        viewer.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # Create image display with optimized scaling
        label = QLabel()
        original_pixmap = QPixmap(path)
        
        # Calculate optimal display size
        viewer_size = viewer.size()
        display_width = viewer_size.width() - 50
        display_height = viewer_size.height() - 50
        
        # Scale image while maintaining aspect ratio
        scaled_pixmap = original_pixmap.scaled(
            display_width, display_height, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("border: 2px solid #34495e; border-radius: 8px;")
        
        layout.addWidget(label)
        viewer.setLayout(layout)
        viewer.exec_()

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if filename:
            self.db.export_detections_to_csv(filename)
            QMessageBox.information(self, "Success", "CSV file saved successfully!")

class ImageDisplayWidget(QLabel):
    """Custom widget for displaying images with modern styling and optimized scaling"""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setStyleSheet("""
            QLabel {
                background: #2c3e50;
                border: 2px dashed #34495e;
                border-radius: 12px;
                color: #95a5a6;
                font-size: 14pt;
                font-weight: 500;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Drop image here or click 'Load Image'")
        self.setScaledContents(False)

class XrayDetectionApp(QWidget):
    def __init__(self, db, role, username):
        super().__init__()
        self.db = db
        self.role = role
        self.username = username
        # Model path'i otomatik belirle
        self.detector = PyTorchDetector()  # Model path parametresini kaldır
        self.original_image = None
        self.video_thread = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("X-Ray Threat Detection System")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet("""
            QWidget {
                background: #1a252f;
                color: white;
                font-family: 'Segoe UI';
            }
        """)
        
        # Main layout with optimized spacing
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Left panel (controls)
        left_panel = self.create_control_panel()
        left_panel.setFixedWidth(350)
        
        # Right panel (image display)
        right_panel = self.create_display_panel()
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
    def create_control_panel(self):
        panel = ModernCard()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Control Panel")
        header.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 20pt;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        # User info section
        user_info = QGroupBox("Session Info")
        user_info.setStyleSheet("""
            QGroupBox {
                color: #ecf0f1;
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)
        user_layout = QVBoxLayout(user_info)
        user_layout.setSpacing(5)
        
        username_label = QLabel(f"User: {self.username}")
        role_label = QLabel(f"Role: {self.role.title()}")
        username_label.setStyleSheet("color: #ecf0f1; margin: 3px;")
        role_label.setStyleSheet("color: #ecf0f1; margin: 3px;")
        
        user_layout.addWidget(username_label)
        user_layout.addWidget(role_label)
        
        # Detection controls section
        detection_group = QGroupBox("Detection Controls")
        detection_group.setStyleSheet(user_info.styleSheet())
        detection_layout = QVBoxLayout(detection_group)
        detection_layout.setSpacing(10)
        
        self.btn_load = ModernButton("📁 Load Image", primary=True)
        self.btn_load.clicked.connect(self.load_image)
        
        self.btn_detect = ModernButton("🔍 Run Detection", primary=True)
        self.btn_detect.clicked.connect(self.run_detection)
        self.btn_detect.setEnabled(False)
        
        self.btn_video = ModernButton("🎥 Process Video")
        self.btn_video.clicked.connect(self.start_video_stream)
        
        self.btn_pause_resume = ModernButton("⏸ Pause Video")
        self.btn_pause_resume.setEnabled(False)
        self.btn_pause_resume.clicked.connect(self.toggle_video_pause)
        
        detection_layout.addWidget(self.btn_load)
        detection_layout.addWidget(self.btn_detect)
        detection_layout.addWidget(self.btn_video)
        detection_layout.addWidget(self.btn_pause_resume)

        # Management controls (for authorized users)
        if self.role in ["şef", "admin"]:
            management_group = QGroupBox("Management")
            management_group.setStyleSheet(user_info.styleSheet())
            management_layout = QVBoxLayout(management_group)
            management_layout.setSpacing(10)
            
            self.btn_records = ModernButton("📊 Detection History")
            self.btn_records.clicked.connect(self.show_records)
            
            self.btn_admin = ModernButton("⚙️ User Management")
            self.btn_admin.clicked.connect(self.open_admin_panel)
            
            management_layout.addWidget(self.btn_records)
            management_layout.addWidget(self.btn_admin)
            
            layout.addWidget(management_group)
        
        # Progress bar with cleaner styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 8px;
                background: #2c3e50;
                text-align: center;
                color: white;
                font-weight: bold;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #3498db, stop:1 #2980b9);
                border-radius: 6px;
            }
        """)
        self.progress_bar.setVisible(False)
        
        # Status label with improved styling
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-weight: bold;
                font-size: 12pt;
                padding: 8px;
                background: rgba(46, 204, 113, 0.1);
                border-radius: 6px;
                border: 1px solid #2ecc71;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout with optimized spacing
        layout.addWidget(header)
        layout.addWidget(user_info)
        layout.addWidget(detection_group)
        layout.addStretch()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        return panel
        
    def toggle_video_pause(self):
        if self.video_thread:
            if self.video_thread.paused:
                self.video_thread.resume()
                self.btn_pause_resume.setText("⏸ Pause Video")
                self.update_status("Video resumed", "#2ecc71")
            else:
                self.video_thread.pause()
                self.btn_pause_resume.setText("▶ Resume Video")
                self.update_status("Video paused", "#f39c12")

    def create_display_panel(self):
        panel = ModernCard()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with improved spacing
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        title = QLabel("Image Analysis")
        title.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 20pt;
                font-weight: bold;
            }
        """)
        
        # Detection info panel with better styling
        self.detection_info = QLabel("No detections")
        self.detection_info.setStyleSheet("""
            QLabel {
                background: rgba(52, 73, 94, 0.8);
                color: #ecf0f1;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 150px;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.detection_info)
        
        # Image display with optimized container
        self.image_label = ImageDisplayWidget()
        
        # Add to layout
        layout.addLayout(header_layout)
        layout.addWidget(self.image_label, 1)
        
        return panel

    def update_status(self, message, color="#2ecc71"):
        self.status_label.setText(message)
        rgb_values = self.hex_to_rgb(color)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                font-size: 12pt;
                padding: 8px;
                background: rgba({rgb_values}, 0.1);
                border-radius: 6px;
                border: 1px solid {color};
            }}
        """)
        
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return ', '.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", 
            "Images (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        if file_path:
            try:
                self.original_image = cv2.imread(file_path)
                if self.original_image is not None:
                    self.display_image(self.original_image)
                    self.btn_detect.setEnabled(True)
                    self.update_status("Image loaded successfully", "#2ecc71")
                    self.detection_info.setText("Image ready for analysis")
                else:
                    self.update_status("Failed to load image", "#e74c3c")
            except Exception as e:
                self.update_status(f"Error loading image: {str(e)}", "#e74c3c")

    def run_detection(self):
        if self.original_image is not None:
            try:
                self.update_status("Running detection...", "#f39c12")
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)  # Indeterminate progress
                
                # Run detection
                detections = self.detector.detect(self.original_image)
                img = self.original_image.copy()
                
                # Draw detections with improved visualization
                for det in detections:
                    x1, y1, x2, y2 = det['bbox']
                    cls_name = det['class']
                    conf = det['score']
                    
                    # Draw bounding box with better styling
                    cv2.rectangle(img, (x1, y1), (x2, y2), (52, 152, 219), 3)
                    
                    # Draw label with improved background
                    label = f"{cls_name} {conf:.2f}"
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(img, (x1, y1 - label_size[1] - 10), 
                                (x1 + label_size[0], y1), (52, 152, 219), -1)
                    cv2.putText(img, label, (x1, y1 - 5), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                self.display_image(img)
                self.progress_bar.setVisible(False)
                
                # Update detection info with better formatting
                if detections:
                    class_names = list(set([det['class'] for det in detections]))
                    detection_count = len(detections)
                    
                    self.detection_info.setText(f"⚠️ {detection_count} threats detected: {', '.join(class_names)}")
                    self.detection_info.setStyleSheet("""
                        QLabel {
                            background: rgba(231, 76, 60, 0.8);
                            color: white;
                            padding: 8px 15px;
                            border-radius: 6px;
                            font-weight: bold;
                            min-width: 150px;
                        }
                    """)
                    
                    # Save detection with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    os.makedirs("results", exist_ok=True)
                    save_path = f"results/detect_{timestamp}.jpg"
                    cv2.imwrite(save_path, img)
                    
                    self.db.insert_detection(class_names, save_path, mode="image", 
                                           operator=self.username, role=self.role)
                    self.db.add_log(self.username, f"Detection completed: {class_names}")
                    
                    self.update_status(f"⚠️ {detection_count} threats detected!", "#e74c3c")
                else:
                    self.detection_info.setText("✅ No threats detected")
                    self.detection_info.setStyleSheet("""
                        QLabel {
                            background: rgba(46, 204, 113, 0.8);
                            color: white;
                            padding: 8px 15px;
                            border-radius: 6px;
                            font-weight: bold;
                            min-width: 150px;
                        }
                    """)
                    self.update_status("Analysis complete - No threats found", "#2ecc71")
                    
            except Exception as e:
                self.progress_bar.setVisible(False)
                self.update_status(f"Detection error: {str(e)}", "#e74c3c")

    def display_image(self, img):
        """Optimized image display with improved scaling"""
        try:
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, channel = img_rgb.shape
            bytes_per_line = channel * width
            
            # Create QImage
            q_img = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Get display widget dimensions
            display_size = self.image_label.size()
            available_width = display_size.width() - 20  # Account for padding
            available_height = display_size.height() - 20
            
            # Create pixmap and scale with high quality
            original_pixmap = QPixmap.fromImage(q_img)
            scaled_pixmap = original_pixmap.scaled(
                available_width, 
                available_height, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            # Set the scaled pixmap
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setStyleSheet("""
                QLabel {
                    background: #2c3e50;
                    border: 2px solid #34495e;
                    border-radius: 12px;
                }
            """)
        except Exception as e:
            self.update_status(f"Display error: {str(e)}", "#e74c3c")

    def start_video_stream(self):
        video_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", 
            "Videos (*.mp4 *.avi *.mov *.mkv)"
        )
        if not video_path:
            return

        try:
            if self.video_thread:
                self.video_thread.stop()
            
            self.btn_pause_resume.setEnabled(True)

            self.video_thread = VideoStreamThread(
                db_manager=self.db,  # model_path parametresini kaldır
                operator=self.username,
                role=self.role,
                source=video_path
            )
            self.video_thread.frame_updated.connect(self.display_image)
            # Video stream'den detection bilgilerini almak için yeni sinyal bağlantısı
            self.video_thread.detection_updated.connect(self.update_detection_info)
            self.video_thread.start()
            
            self.update_status("Processing video stream...", "#f39c12")
            
        except Exception as e:
            self.update_status(f"Video processing error: {str(e)}", "#e74c3c")

    def update_detection_info(self, detections):
        """Video stream'den gelen detection bilgilerini güncelle"""
        try:
            if detections and len(detections) > 0:
                # Tespit edilen sınıfları topla
                class_names = list(set([det['class'] for det in detections if 'class' in det]))
                detection_count = len(detections)
                
                # Detection info'yu güncelle
                if class_names:
                    self.detection_info.setText(f"⚠️ {detection_count} threats detected: {', '.join(class_names)}")
                    self.detection_info.setStyleSheet("""
                        QLabel {
                            background: rgba(231, 76, 60, 0.8);
                            color: white;
                            padding: 8px 15px;
                            border-radius: 6px;
                            font-weight: bold;
                            min-width: 150px;
                        }
                    """)
                    self.update_status(f"⚠️ {detection_count} threats detected!", "#e74c3c")
                else:
                    self.detection_info.setText("✅ Processing video...")
                    self.detection_info.setStyleSheet("""
                        QLabel {
                            background: rgba(241, 196, 15, 0.8);
                            color: white;
                            padding: 8px 15px;
                            border-radius: 6px;
                            font-weight: bold;
                            min-width: 150px;
                        }
                    """)
            else:
                self.detection_info.setText("✅ No threats detected")
                self.detection_info.setStyleSheet("""
                    QLabel {
                        background: rgba(46, 204, 113, 0.8);
                        color: white;
                        padding: 8px 15px;
                        border-radius: 6px;
                        font-weight: bold;
                        min-width: 150px;
                    }
                """)
        except Exception as e:
            print(f"Detection info update error: {str(e)}")

    def show_records(self):
        dialog = RecordViewerDialog(self.db)
        dialog.exec_()

    def open_admin_panel(self):
        dialog = AdminPanelDialog(self.db, self.role, self.username)
        dialog.exec_()
        
    def closeEvent(self, event):
        """Handle application close event"""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()
        event.accept()

def apply_dark_theme(app):
    """Apply modern dark theme to the application"""
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 37, 47))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(44, 62, 80))
    palette.setColor(QPalette.AlternateBase, QColor(52, 73, 94))
    palette.setColor(QPalette.ToolTipBase, QColor(44, 62, 80))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(52, 73, 94))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(52, 152, 219))
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)

# Program Entry Point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    icon_path = get_icon_path()
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))
        print(f"[ICON] Icon yüklendi: {icon_path}")
    
    # Apply modern dark theme
    apply_dark_theme(app)
    
    # Set application properties
    app.setApplicationName("DIDRay Security System")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Security Solutions")
    
    # Initialize database
    db = DBManager()
    
    # Create default users if they don't exist
    try:
        db.add_user("admin", "admin123", "admin")
        db.add_user("şef1", "123456", "şef")
        db.add_user("personel1", "111111", "personel")
    except:
        pass  # Users might already exist
    
    # Show login dialog
    login_dialog = LoginDialog(db)
    if login_dialog.exec_() == QDialog.Accepted:
        role = login_dialog.role
        username = login_dialog.username
        
        # Create and show main application
        window = XrayDetectionApp(db, role, username)
        window.show()
        
        sys.exit(app.exec_())
    else:
        sys.exit()