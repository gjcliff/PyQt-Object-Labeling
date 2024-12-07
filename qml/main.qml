import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 800
    height: 600
    title: "Image Annotator"

    ImageView {
        id: imageView
        anchors.fill: parent
        imageSource: imageProcessor.currentImage()
    }
}
