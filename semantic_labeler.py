import os
import sys
import argparse
import yaml
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QGuiApplication
from PyQt6.QtCore import Qt, QRect, QPoint


class MainWindow(QWidget):
    def __init__(self, base_dir):
        super().__init__()

        self.base_dir = base_dir
        self.images_dir = os.path.join(base_dir, "images")
        self.depths_dir = os.path.join(base_dir, "depths")
        self.landmarks_dir = os.path.join(base_dir, "landmarks")

        # figure out screen size
        screen = QGuiApplication.primaryScreen()
        screen_size = screen.availableGeometry()

        self.image_width = 720  # default for iphone
        self.image_height = 960  # default for iphone
        self.button_width = 50
        self.button_height = 50
        self.spacing = 10
        self.window_width = int(screen_size.width())
        self.window_height = int(screen_size.height())

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
            self.image_width + self.spacing * 2,
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
        self.labels = {}

        # Load images from directories
        self.images = self.load_images(self.images_dir)
        self.depths = self.load_images(self.depths_dir)
        self.current_index = 0  # Start with the first pair

        # Connect buttons to methods
        self.left_button.clicked.connect(self.show_previous_images)
        self.right_button.clicked.connect(self.show_next_images)

        # yaml stuff
        self.landmark_labels = []
        self.display_landmarks(self.load_yaml(self.landmarks_dir))

    def load_yaml(self, yaml_path):
        files = os.listdir(yaml_path)
        yaml_file = next((f for f in files if f.endswith(".yaml")), None)

        if not yaml_file:
            raise FileNotFoundError(f"No YAML file found in directory: {yaml_path}")

        yaml_file_path = os.path.join(yaml_path, yaml_file)
        with open(yaml_file_path, "r") as file:
            return yaml.safe_load(file)

    def display_landmarks(self, landmarks):
        start_x = self.image_width * 2 + self.spacing * 3
        start_y = 0

        for i, (name, coords) in enumerate(landmarks.items()):
            frame = QFrame(self)
            frame.setGeometry(start_x, start_y + (i * (self.spacing * 2)), 300, 100)
            frame.setStyleSheet("border: 1px solid black;")

            label = QLabel(f"{name}: ({coords['x']:.2f}, {coords['y']:.2f})", frame)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setGeometry(0, 0, 300, 100)

            self.landmark_labels.append(label)
            frame.show()
            label.show()

    def load_images(self, dir_path):
        """Load all image file paths from the directory."""
        images = []
        for filename in os.listdir(dir_path):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                images.append(os.path.join(dir_path, filename))
        images.sort()
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
        self.bounding_boxes = {}
        self.display_images()

    def show_next_images(self):
        """Show the next pair of images."""
        self.current_index = (self.current_index + 1) % len(self.images)
        self.bounding_boxes = {}
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
            self.labels[label_name] = label_edit

            label_edit = QLineEdit(self)
            label_edit.setText(label_name)
            label_edit.setGeometry(
                box_coords.topLeft().x() + self.right_image_label.geometry().x(),
                box_coords.topLeft().y() + self.right_image_label.geometry().y() - 20,
                50,
                20,
            )
            label_edit.show()
            label_edit.editingFinished.connect(
                lambda: self.update_label(label_edit, box_coords)
            )
            self.labels[label_name] = label_edit

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

        left_painter = QPainter(left_pixmap)
        right_painter = QPainter(right_pixmap)
        pen = QPen(Qt.GlobalColor.green, 2, Qt.PenStyle.SolidLine)
        left_painter.setPen(pen)
        right_painter.setPen(pen)

        # Draw current bounding box
        if self.start_point and self.end_point:
            box = QRect(self.start_point, self.end_point).normalized()
            if self.left_image_label.geometry().contains(
                self.mapFromGlobal(QPoint(box.x(), box.y()))
            ):
                left_painter.drawRect(
                    box.translated(self.left_image_label.geometry().topLeft())
                )
                right_painter.drawRect(
                    box.translated(self.left_image_label.geometry().topLeft())
                )
            elif self.right_image_label.geometry().contains(
                self.mapFromGlobal(QPoint(box.x(), box.y()))
            ):
                left_painter.drawRect(
                    box.translated(self.right_image_label.geometry().topLeft())
                )
                right_painter.drawRect(
                    box.translated(self.right_image_label.geometry().topLeft())
                )

        # Draw saved bounding boxes
        for label, box in self.bounding_boxes.items():
            if self.left_image_label.geometry().contains(
                self.mapFromGlobal(QPoint(box.x(), box.y()))
            ):
                left_painter.drawRect(
                    box.translated(self.left_image_label.geometry().topLeft())
                )
                right_painter.drawRect(
                    box.translated(self.left_image_label.geometry().topLeft())
                )

        for label, line_edit in self.labels.items():
            if self.left_image_label.geometry().contains(
                self.mapFromGlobal(QPoint(box.x(), box.y()))
            ):
                line_edit.setGeometry(
                    box.topLeft().x() + self.left_image_label.geometry().x(),
                    box.topLeft().y() + self.left_image_label.geometry().y() - 20,
                    50,
                    20,
                )
                line_edit.show()
            elif self.right_image_label.geometry().contains(
                self.mapFromGlobal(QPoint(box.x(), box.y()))
            ):
                line_edit.setGeometry(
                    box.topLeft().x() + self.right_image_label.geometry().x(),
                    box.topLeft().y() + self.right_image_label.geometry().y() - 20,
                    50,
                    20,
                )
                line_edit.show()

        left_painter.end()
        right_painter.end()
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
            self.labels[new_label] = label_edit
            if old_label:
                del self.labels[label_edit.text()]
                del self.bounding_boxes[old_label[0]]
            self.bounding_boxes[new_label] = box_coords
        # label_edit.clearFocus()
        # label_edit.setDisabled(True)
        # label_edit.hide()
        label_edit.deselect()
        label_edit.deleteLater()
        self.update()


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Display paired images and depth maps side by side."
    )
    parser.add_argument("name", type=str, help="Name of the output directory")
    args = parser.parse_args()

    # Construct the directories for images and depths
    base_dir = os.path.join("output", args.name)

    if not os.path.exists(base_dir):
        print(f"Path {base_dir} does not exist")
        sys.exit(1)

    # Create and show the PyQt window
    app = QApplication(sys.argv)
    window = MainWindow(base_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
