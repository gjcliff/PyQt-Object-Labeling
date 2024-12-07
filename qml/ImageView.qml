import QtQuick 2.15

Item {
    property alias imageSource: imageItem.source

    Image {
        id: imageItem
        anchors.fill: parent
        fillMode: Image.PreserveAspectFit
    }

    Rectangle {
        id: selectionRect
        border.color: "red"
        border.width: 2
        visible: false

        property real startX
        property real startY

        MouseArea {
            anchors.fill: parent
            onPressed: {
                selectionRect.startX = mouse.x
                selectionRect.startY = mouse.y
                selectionRect.visible = true
            }
            onPositionChanged: {
                selectionRect.width = mouse.x - selectionRect.startX
                selectionRect.height = mouse.y - selectionRect.startY
            }
            onReleased: {
                selectionRect.visible = false
                imageProcessor.saveCroppedImage(
                    Qt.rect(selectionRect.startX, selectionRect.startY, selectionRect.width, selectionRect.height),
                    "cropped.png"
                )
            }
        }
    }
}
