import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control
    property color baseColor: "#1f6feb"
    property color textColor: "white"
    hoverEnabled: true

    background: Rectangle {
        radius: 12
        color: control.down ? Qt.darker(control.baseColor, 1.12)
             : control.hovered ? Qt.lighter(control.baseColor, 1.06)
             : control.baseColor
        opacity: control.enabled ? 1.0 : 0.45
        Behavior on color { ColorAnimation { duration: 120 } }
    }

    contentItem: Text {
        text: control.text
        color: control.textColor
        font.pixelSize: 14
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
