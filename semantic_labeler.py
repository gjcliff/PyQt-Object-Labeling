import os
import sys
import argparse
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
)
from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtCore import Qt, QRect, QPoint


class MainWindow(QWidget):
    def __init__(self, images_dir, depths_dir):
        super().__init__()

        self.image_width = 720
        self.image_height = 960
        self.button_width = 50
        self.button_height = 50
        self.spacing = 10
        self.window_width = self.image_width * 2 + self.spacing * 5
        self.window_height = self.image_height + self.spacing * 2

        self.setWindowTitle("Image Viewer")
        self.setGeometry(
            0,
            0,
            self.window_width,
            self.window_height,
        )

        # Create labels for left and right images
        self.left_image_label = QLabel(self)
        # top left x, top left y, width, height
        self.left_image_label.setGeometry(
            self.spacing, self.spacing, self.image_width, self.image_height
        )

        self.right_image_label = QLabel(self)
        # top left x, top left y, width, height
        self.right_image_label.setGeometry(
            self.image_width + self.spacing,
            self.spacing,
            self.image_width,
            self.image_height,
        )

        # Navigation buttons for the left image
        self.left_button = QPushButton("<", self)
        self.right_button = QPushButton(">", self)

        # Set button styles
        button_style = "background-color: black; border: none;\
                    font-size: 24px; color: white;"
        self.left_button.setStyleSheet(button_style)
        self.right_button.setStyleSheet(button_style)

        # Layout to arrange images side by side
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.left_image_label)
        self.layout.addWidget(self.right_image_label)
        self.setLayout(self.layout)

        # Set up the buttons' positions using absolute positioning
        self.left_button.setGeometry(
            QRect(
                self.spacing,
                int(self.image_height / 2),
                self.button_width,
                self.button_height,
            )
        )
        self.right_button.setGeometry(
            QRect(
                self.image_width + self.spacing - self.button_width + 1,
                int(self.image_height / 2),
                self.button_width,
                self.button_height,
            )
        )

        # Variables for bounding box
        self.start_point = None
        self.end_point = None
        self.current_label = None
        self.bounding_boxes = {}  # Store bounding boxes as {label: (coords)}

        # Load images from directories
        self.images = self.load_images(images_dir)
        self.depths = self.load_images(depths_dir)
        self.current_index = 0  # Start with the first pair

        # Connect buttons to methods
        self.left_button.clicked.connect(self.show_previous_images)
        self.right_button.clicked.connect(self.show_next_images)

    def load_images(self, dir_path):
        """Load all image file paths from the directory."""
        images = []
        for filename in os.listdir(dir_path):
            if filename.endswith(".jpg"):  # Add more file types if needed
                images.append(os.path.join(dir_path, filename))
        images.sort()  # Sort files (optional, but ensures correct order)
        return images

    def display_images(self):
        """Display the current pair of images."""
        if 0 <= self.current_index < len(self.images):
            # Load left image
            left_image_path = self.images[self.current_index]
            left_pixmap = QPixmap(left_image_path)
            self.left_image_label.setPixmap(
                left_pixmap.scaled(
                    self.image_width,
                    self.image_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

            # Load right image
            right_image_path = self.depths[self.current_index]
            right_pixmap = QPixmap(right_image_path)
            self.right_image_label.setPixmap(
                right_pixmap.scaled(
                    self.image_width,
                    self.image_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def show_previous_images(self):
        """Show the previous pair of images."""
        self.current_index = (self.current_index - 1) % len(self.images)
        self.display_images()

    def show_next_images(self):
        """Show the next pair of images."""
        self.current_index = (self.current_index + 1) % len(self.images)
        self.display_images()

    def mousePressEvent(self, event):
        """Start drawing a bounding box."""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            if self.left_image_label.geometry().contains(pos):
                self.start_point = pos - self.left_image_label.geometry().topLeft()
            elif self.right_image_label.geometry().contains(pos):
                self.start_point = pos - self.right_image_label.geometry().topLeft()
            self.end_point = self.start_point

    def mouseMoveEvent(self, event):
        """Update the bounding box during mouse drag."""
        if self.start_point:
            pos = event.pos()
            if self.left_image_label.geometry().contains(pos):
                self.end_point = pos - self.left_image_label.geometry().topLeft()
            elif self.right_image_label.geometry().contains(pos):
                self.end_point = pos - self.right_image_label.geometry().topLeft()
            self.update()

    def mouseReleaseEvent(self, event):
        """Finish drawing the bounding box."""
        if event.button() == Qt.MouseButton.LeftButton and self.start_point:
            # Save the bounding box coordinates
            box_coords = QRect(self.start_point, self.end_point).normalized()
            label_name = "box"

            # Add QLabel for the label above the box
            label_edit = QLineEdit(self)
            label_edit.setText(label_name)
            label_edit.setGeometry(
                box_coords.topLeft().x() + self.left_image_label.geometry().x(),
                box_coords.topLeft().y() + self.left_image_label.geometry().y() - 20,
                50,
                20,
            )
            label_edit.show()
            label_edit.editingFinished.connect(
                lambda: self.update_label(label_edit, box_coords)
            )

            # Add bounding box to the dictionary
            self.bounding_boxes[label_name] = box_coords
            self.start_point = None
            self.end_point = None
            self.update()

    def paintEvent(self, event):
        """Draw the bounding boxes."""
        left_image_path = self.images[self.current_index]
        left_pixmap = QPixmap(left_image_path)
        right_image_path = self.depths[self.current_index]
        right_pixmap = QPixmap(right_image_path)

        painter = QPainter(left_pixmap)
        pen = QPen(Qt.GlobalColor.green, 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        # Draw current bounding box
        if self.start_point and self.end_point:
            box = QRect(self.start_point, self.end_point).normalized()
            if self.left_image_label.geometry().contains(
                self.mapFromGlobal(QPoint(box.x(), box.y()))
            ):
                painter.drawRect(
                    box.translated(self.left_image_label.geometry().topLeft())
                )
            elif self.right_image_label.geometry().contains(
                self.mapFromGlobal(QPoint(box.x(), box.y()))
            ):
                painter.drawRect(
                    box.translated(self.right_image_label.geometry().topLeft())
                )

        # Draw saved bounding boxes
        for label, box in self.bounding_boxes.items():
            if self.left_image_label.geometry().contains(
                self.mapFromGlobal(QPoint(box.x(), box.y()))
            ):
                painter.drawRect(
                    box.translated(self.left_image_label.geometry().topLeft())
                )
            elif self.right_image_label.geometry().contains(
                self.mapFromGlobal(QPoint(box.x(), box.y()))
            ):
                painter.drawRect(
                    box.translated(self.right_image_label.geometry().topLeft())
                )

        painter.end()
        if 0 <= self.current_index < len(self.images):
            # Load left image
            self.left_image_label.setPixmap(
                left_pixmap.scaled(
                    self.image_width,
                    self.image_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

            # Load right image
            self.right_image_label.setPixmap(
                right_pixmap.scaled(
                    self.image_width,
                    self.image_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            if self.current_index < 0:
                self.current_index = len(self.images) - 1
            else:
                self.current_index = 0

    def update_label(self, label_edit, box_coords):
        """Update the label in the bounding boxes dictionary."""
        new_label = label_edit.text()
        if new_label:
            old_label = [k for k, v in self.bounding_boxes.items() if v == box_coords]
            if old_label:
                del self.bounding_boxes[old_label[0]]
            self.bounding_boxes[new_label] = box_coords
        label_edit.deleteLater()


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Display paired images and depth maps side by side."
    )
    parser.add_argument("name", type=str, help="Name of the output directory")
    args = parser.parse_args()

    # Construct the directories for images and depths
    base_dir = os.path.join("output", args.name)
    images_dir = os.path.join(base_dir, "images")
    depths_dir = os.path.join(base_dir, "depths")

    if not os.path.exists(images_dir) or not os.path.exists(depths_dir):
        print(f"One or both directories ({images_dir}, {depths_dir}) do not exist.")
        sys.exit(1)

    # Create and show the PyQt window
    app = QApplication(sys.argv)
    window = MainWindow(images_dir, depths_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
