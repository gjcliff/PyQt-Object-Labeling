import sys
import os
import argparse
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QRect


class MainWindow(QWidget):
    def __init__(self, images_dir):
        super().__init__()

        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Layout for the window
        self.layout = QVBoxLayout()

        # QLabel to display the image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons to navigate images
        self.left_button = QPushButton("<", self)
        self.right_button = QPushButton(">", self)

        # Set buttons to be transparent (optional)
        self.left_button.setStyleSheet(
            "background-color: black; border: none; font-size: 24px; color: white;"
        )
        self.right_button.setStyleSheet(
            "background-color: black; border: none; font-size: 24px; color: white;"
        )

        # Connect buttons to methods
        self.left_button.clicked.connect(self.show_previous_image)
        self.right_button.clicked.connect(self.show_next_image)

        # Add buttons and image label to the layout
        self.layout.addWidget(self.image_label)

        # Set up the buttons' positions using absolute positioning
        self.left_button.setGeometry(
            QRect(10, 480, 50, 50)
        )  # Left button at the left center of the image
        self.right_button.setGeometry(
            QRect(682, 480, 50, 50)
        )  # Right button at the right center of the image

        # Add image_label to the layout
        self.setLayout(self.layout)

        # Load images from directory
        self.images = self.load_images(images_dir)
        self.current_index = 0  # Start with the first image

        # Show the first image
        self.display_image(self.current_index)

    def load_images(self, images_dir):
        """Load all image file paths from the directory."""
        images = []
        for filename in os.listdir(images_dir):
            if filename.endswith(".jpg"):  # Add more file types if needed
                images.append(os.path.join(images_dir, filename))
        images.sort()  # Sort files (optional, but ensures correct order)
        return images

    def display_image(self, index):
        """Display the image at the given index."""
        image_path = self.images[index]
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Failed to load image at {image_path}")
        else:
            self.image_label.setPixmap(pixmap)
            self.image_label.setFixedSize(
                pixmap.size()
            )  # Ensure the image size is fixed

    def show_previous_image(self):
        """Show the previous image."""
        self.current_index = (self.current_index - 1) % len(self.images)
        self.display_image(self.current_index)

    def show_next_image(self):
        """Show the next image."""
        self.current_index = (self.current_index + 1) % len(self.images)
        self.display_image(self.current_index)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Display images from the output directory"
    )
    parser.add_argument("name", type=str, help="Name of the output directory")
    args = parser.parse_args()

    # Construct the image directory path
    images_dir = os.path.join("output", args.name, "images")

    if not os.path.exists(images_dir):
        print(f"Directory {images_dir} does not exist.")
        sys.exit(1)

    # Create and show the PyQt window
    app = QApplication(sys.argv)
    window = MainWindow(images_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
