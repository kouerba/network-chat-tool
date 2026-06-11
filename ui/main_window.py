from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QDialog, QLabel, QLineEdit, QPushButton,
                            QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from network.udp_handler import UDPHandler
from network.tcp_handler import TCPHandler
from network.user_discovery import UserDiscovery
from network.message import Message, MessageType
from core.user_manager import UserManager, User
from core.config import Config
from ui.styles import DARK_STYLESHEET
from ui.chat_widget import ChatWidget
from ui.user_list_widget import UserListWidget
from utils.logger import Logger
from utils.encryption import Encryption
from utils.storage import Storage
import socket

class UserInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置用户信息")
        self.setModal(True)
        self.setStyleSheet(DARK_STYLESHEET)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        label = QLabel("请输入你的昵称：")
        label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        layout.addWidget(label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入昵称（2-20个字符）")
        self.name_input.setMinimumHeight(40)
        self.name_input.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(self.name_input)
        
        btn_layout = QHBoxLayout()
        
        ok_btn = QPushButton("确定")
        ok_btn.setMinimumHeight(35)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        self.setMinimumWidth(400)
    
    def get_username(self):
        return self.name_input.text().strip()

class MainWindow(QMainWindow):
    message_received_signal = pyqtSignal(Message)
    user_discovered_signal = pyqtSignal(User)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.setGeometry(100, 100, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        self.setMinimumSize(Config.MIN_WINDOW_WIDTH, Config.MIN_WINDOW_HEIGHT)
        self.setStyleSheet(DARK_STYLESHEET)
        
        Encryption.init()
        self.storage = Storage()
        self.logger = Logger.get_logger(__name__)
        self.user_manager = UserManager()
        
        self.udp_handler = None
        self.tcp_handler = None
        self.user_discovery = None
        
        self._show_user_setup_dialog()
        
        self.chat_tabs = None
        self.user_list = None
        self.group_chat = None
        
        self.message_received_signal.connect(self._on_message_received)
        self.user_discovered_signal.connect(self._on_user_discovered)
        
        self.setup_ui()
        self.start_network()
    
    def _show_user_setup_dialog(self):
        dialog = UserInputDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username = dialog.get_username()
            if username and 2 <= len(username) <= 20:
                self.user_manager.set_current_user(username)
            else:
                QMessageBox.warning(self, "错误", "昵称长度必须在2-20个字符之间")
                self._show_user_setup_dialog()
        else:
            import sys
            sys.exit()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        self.chat_tabs = QTabWidget()
        self.chat_tabs.setTabsClosable(False)
        
        self.group_chat = ChatWidget(None, self.user_manager)
        self.chat_tabs.addTab(self.group_chat, f"👥 群聊 (所有用户)")
        
        layout.addWidget(self.chat_tabs, 4)
        
        self.user_list = UserListWidget(self.user_manager)
        self.user_list.user_selected.connect(self._open_private_chat)
        layout.addWidget(self.user_list, 1)
        
        self.setLayout(layout)
    
    def start_network(self):
        try:
            self.udp_handler = UDPHandler(
                Config.UDP_BROADCAST_PORT,
                self._on_udp_message_received
            )
            self.udp_handler.start()
            
            self.tcp_handler = TCPHandler(
                Config.TCP_SERVER_PORT,
                self._on_tcp_message_received
            )
            self.tcp_handler.start()
            
            current_user = self.user_manager.current_user
            self.user_discovery = UserDiscovery(
                current_user.username,
                current_user.user_id,
                self.udp_handler,
                self._on_user_discovered
            )
            self.user_discovery.start()
            
            self.logger.info("Network services started")
            self._show_status(f"✅ 网络已连接 | 昵称: {current_user.username}")
        except Exception as e:
            self.logger.error(f"Failed to start network: {e}")
            QMessageBox.critical(self, "错误", f"网络启动失败: {e}")
    
    def _on_udp_message_received(self, message: Message):
        self.message_received_signal.emit(message)
    
    def _on_tcp_message_received(self, message: Message):
        self.message_received_signal.emit(message)
    
    def _on_user_discovered(self, user: User):
        self.user_discovered_signal.emit(user)
    
    def _on_message_received(self, message: Message):
        try:
            if message.msg_type == MessageType.BROADCAST:
                if message.from_id != self.user_manager.current_user.user_id:
                    self.group_chat.add_message(message)
                    self.storage.save_message(
                        message.msg_id, message.msg_type.value,
                        message.from_user, message.from_id,
                        None, None, message.content, message.timestamp
                    )
            
            elif message.msg_type == MessageType.HEARTBEAT:
                if message.from_id != self.user_manager.current_user.user_id:
                    user = User(
                        username=message.from_user,
                        user_id=message.from_id,
                        ip=message.content,
                        tcp_port=Config.TCP_SERVER_PORT,
                        is_online=True
                    )
                    self.user_manager.add_user(user)
                    self.user_list.update_user_list()
            
            elif message.msg_type == MessageType.PRIVATE:
                if message.to_id == self.user_manager.current_user.user_id:
                    self._open_private_chat(message.from_id, message.from_user)
                    for i in range(1, self.chat_tabs.count()):
                        widget = self.chat_tabs.widget(i)
                        if isinstance(widget, ChatWidget) and widget.peer_id == message.from_id:
                            widget.add_message(message)
                            self.chat_tabs.setCurrentIndex(i)
                            break
                    
                    self.storage.save_message(
                        message.msg_id, message.msg_type.value,
                        message.from_user, message.from_id,
                        message.to_user, message.to_id,
                        message.content, message.timestamp
                    )
        
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def _open_private_chat(self, user_id: str, username: str = None):
        for i in range(1, self.chat_tabs.count()):
            widget = self.chat_tabs.widget(i)
            if isinstance(widget, ChatWidget) and widget.peer_id == user_id:
                self.chat_tabs.setCurrentIndex(i)
                return
        
        peer_user = self.user_manager.get_user(user_id)
        if not peer_user and username:
            peer_user = User(username=username, user_id=user_id, is_online=True)
        
        if peer_user:
            chat_widget = ChatWidget(peer_user, self.user_manager)
            chat_widget.message_to_send.connect(self._send_private_message)
            self.chat_tabs.addTab(chat_widget, f"💬 {peer_user.username}")
            self.chat_tabs.setCurrentWidget(chat_widget)
    
    def _send_private_message(self, peer_id: str, content: str):
        try:
            current_user = self.user_manager.current_user
            peer_user = self.user_manager.get_user(peer_id)
            
            if not peer_user:
                QMessageBox.warning(self, "错误", "用户不在线")
                return
            
            message = Message(
                msg_type=MessageType.PRIVATE,
                from_user=current_user.username,
                from_id=current_user.user_id,
                to_user=peer_user.username,
                to_id=peer_id,
                content=content
            )
            
            if peer_user.ip and peer_user.tcp_port:
                conn = self.tcp_handler.connect_to_user(
                    peer_user.ip, peer_user.tcp_port, peer_id,
                    self._on_tcp_message_received
                )
                if conn:
                    conn.send_message(message)
        
        except Exception as e:
            self.logger.error(f"Failed to send private message: {e}")
            QMessageBox.critical(self, "错误", f"发送失败: {e}")
    
    def _show_status(self, message: str):
        self.statusBar().showMessage(message, 5000)
    
    def closeEvent(self, event):
        if self.udp_handler:
            self.udp_handler.stop()
        if self.tcp_handler:
            self.tcp_handler.stop()
        if self.user_discovery:
            self.user_discovery.stop()
        event.accept()
