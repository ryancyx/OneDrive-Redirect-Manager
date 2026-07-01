import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    property string statusText: ""
    property string statusIcon: ""
    property color statusColor: "#6b7280"
    radius: 999
    color: Qt.rgba(statusColor.r, statusColor.g, statusColor.b, 0.12)
    implicitHeight: 28
    implicitWidth: row.implicitWidth + 18

    Row {
        id: row
        anchors.centerIn: parent
        spacing: 6

        Text {
            text: root.statusIcon || "○"
            color: root.statusColor
            font.pixelSize: 13
            font.bold: true
        }

        Text {
            text: root.statusText || "未知状态"
            color: root.statusColor
            font.pixelSize: 13
            font.bold: true
        }
    }
}
