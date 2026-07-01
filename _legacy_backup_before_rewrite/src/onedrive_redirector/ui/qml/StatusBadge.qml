import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    property string statusText: ""
    property color statusColor: "#1f2937"

    radius: 999
    color: Qt.rgba(statusColor.r, statusColor.g, statusColor.b, 0.10)
    border.color: statusColor
    border.width: 1
    implicitHeight: 36
    implicitWidth: Math.max(110, textItem.implicitWidth + 28)

    Label {
        id: textItem
        anchors.centerIn: parent
        text: root.statusText
        color: root.statusColor
        font.bold: true
        font.pixelSize: 13
    }
}
