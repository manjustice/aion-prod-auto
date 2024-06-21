import numpy as np
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
    QFrame,
    QMessageBox
)
from PyQt5.QtGui import QPixmap, QDrag, QImage
from PyQt5.QtCore import Qt, QMimeData

from app.block import Item
from app.production_window import ProductionWindow
from app.custom_exception import CantFindAionError, CantFindAionProdWindowError
from config import root_logger


class ImageLabelItem(QWidget):
    def __init__(self, prod_item: Item, pixmap, parent=None):
        super().__init__(parent)
        self.drag_start_position = None

        self.prod_item = prod_item
        self.pixmap_label = QLabel(self)
        self.pixmap_label.setPixmap(pixmap)
        self.pixmap_label.setFixedSize(pixmap.size())
        self.pixmap_label.setFrameShape(QFrame.Box)

        self.delete_button = QPushButton("❌", self)
        self.delete_button.setFixedSize(40, 25)
        self.delete_button.clicked.connect(self.delete_image)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self.pixmap_label)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)
        self.setFixedSize(self.sizeHint())
        self.setAcceptDrops(True)
        self.setEnabled(True)

        self.to_produce = True

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        self.startDrag()

    def startDrag(self):
        self.parent().layout().removeWidget(self)
        drag = QDrag(self)
        mime_data = QMimeData()
        drag.setMimeData(mime_data)
        drag.setHotSpot(self.drag_start_position)
        drag.setPixmap(self.pixmap_label.pixmap())
        drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()
        source = event.source()
        if source and source != self:
            self.swap_images(source, self)
            event.acceptProposedAction()

    def swap_images(self, source, target):
        source_index = self.parent().layout().indexOf(source)
        target_index = self.parent().layout().indexOf(target)

        if source_index < target_index:
            self.parent().layout().insertWidget(target_index + 1, source)
        else:
            self.parent().layout().insertWidget(target_index, source)
        self.parent().layout().update()

    def delete_image(self):
        self.parent().layout().removeWidget(self)
        self.deleteLater()
        self.to_produce = False


class BotGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aion Prod Auto")
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setGeometry(300, 300, 400, 300)

        main_layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_area_widget)

        self.image_layout = QVBoxLayout(self.scroll_area_widget)
        self.image_layout.setSpacing(3)
        self.image_layout.setAlignment(Qt.AlignTop)

        main_layout.addWidget(self.scroll_area)

        button_layout = QHBoxLayout()

        self.update_button = QPushButton("Get Items")
        self.update_button.clicked.connect(self.update_images)
        button_layout.addWidget(self.update_button)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_production)
        button_layout.addWidget(self.start_button)

        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.image_labels = []

        self.prod_window: ProductionWindow | None = None

    def add_image(self, item: Item):
        height, width, channel = item.item_array.shape
        bytes_per_line = width * channel
        q_image = QImage(item.item_array.data, width, height, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(q_image)
        pixmap = pixmap.scaled(300, 18, Qt.KeepAspectRatio)

        label = ImageLabelItem(item, pixmap, self)
        label.setFixedSize(label.sizeHint())
        self.image_layout.addWidget(label)
        self.image_labels.append(label)

    def update_images(self):
        try:
            self.prod_window = ProductionWindow()
        except CantFindAionError:
            self.activate_main_window()
            self.show_error_popup("Cannot find Aion. Please make sure the application is running and try again.")
        except CantFindAionProdWindowError:
            self.activate_main_window()
            self.show_error_popup("Cannot find Production window. Please open it and press 'Get Items' again")
        except Exception as e:
            root_logger.debug(e)

        if self.prod_window is not None and self.prod_window.items:
            for label in self.image_labels:
                self.image_layout.removeWidget(label)
                label.deleteLater()

            self.image_labels = []

            for item in self.prod_window.items:
                self.add_image(item)

        self.activate_main_window()

    def show_error_popup(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def activate_main_window(self):
        self.activateWindow()

    def start_production(self):
        items_to_produce = []
        try:
            for image_item in self.image_labels:
                if image_item.to_produce:
                    items_to_produce.append(image_item.prod_item)

            if items_to_produce:
                self.prod_window.start_make_items(items_to_produce)
        except Exception as e:
            root_logger.error(e, exc_info=True)
