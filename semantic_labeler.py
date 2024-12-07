import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class MainWindow(QWidget):
    def __init__(self, image_path):
        super().__init__()

        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Layout
        layout = QVBoxLayout()

        # QLabel to display the image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Load the image
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Failed to load image at {image_path}")
        else:
            self.image_label.setPixmap(pixmap)

        layout.addWidget(self.image_label)

        # Set the layout
        self.setLayout(layout)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Display first image from the output directory"
    )
    parser.add_argument("name", type=str, help="Name of the output directory")
    args = parser.parse_args()

    # Construct the image path
    images_dir = os.path.join("output", args.name, "images")
    first_image_path = os.path.join(images_dir, "0.jpg")

    if not os.path.exists(first_image_path):
        print(f"Image {first_image_path} does not exist.")
        sys.exit(1)

    # Create and show the PyQt window
    app = QApplication(sys.argv)
    window = MainWindow(first_image_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
