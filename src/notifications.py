import platform
import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from .utils import get_asset_path

class NotificationManager:
    def __init__(self):
        self.system = platform.system()
        self.setup_notifier()
        
    def setup_notifier(self):
        """Configura il sistema di notifiche appropriato per la piattaforma"""
        if self.system == "Windows":
            try:
                from win10toast import ToastNotifier
                self.notifier = ToastNotifier()
                self.notification_type = "win10toast"
            except:
                self.setup_qt_tray()
        elif self.system == "Darwin":  # macOS
            try:
                import Foundation
                NSUserNotification = Foundation.NSUserNotification  # Usa l'import
                self.notification_type = "macos"
            except:
                self.setup_qt_tray()
        else:
            self.setup_qt_tray()
            
    def setup_qt_tray(self):
        """Configura le notifiche tramite QSystemTrayIcon come fallback"""
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(get_asset_path('logo_abe.png')))
        self.notification_type = "qt"
        
    def notify(self, title, message, duration=5, callback=None):
        """Invia una notifica usando il sistema appropriato"""
        if self.notification_type == "win10toast":
            self.notifier.show_toast(
                title,
                message,
                duration=duration,
                icon_path=None,
                threaded=True
            )
        elif self.notification_type == "macos":
            # Import solo quando necessario
            from Foundation import NSUserNotification, NSUserNotificationCenter
            
            notification = NSUserNotification.alloc().init()
            notification.setTitle_(title)
            notification.setInformativeText_(message)
            
            if callback:
                notification.setHasActionButton_(True)
                notification.setActionButtonTitle_("Apri")
            
            center = NSUserNotificationCenter.defaultUserNotificationCenter()
            center.deliverNotification_(notification)
        else:
            # Fallback su QSystemTrayIcon
            self.tray_icon.show()
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                duration * 1000
            )
            if callback:
                self.tray_icon.messageClicked.connect(callback)

# Istanza singleton del gestore notifiche
notification_manager = NotificationManager() 