import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    property var project
    property bool selected: false
    signal cardClicked()

    radius: 14
    color: selected ? "#eaf2ff" : "#ffffff"
    border.color: selected ? "#2563eb" : "#e5e7eb"
    border.width: selected ? 2 : 1
    implicitHeight: 92

    Rectangle {
        width: 5
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        radius: 5
        color: project.statusColor
    }

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: root.cardClicked()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 12
        anchors.topMargin: 10
        anchors.bottomMargin: 10
        spacing: 5

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Label {
                text: project.statusIcon
                font.pixelSize: 18
            }

            Label {
                Layout.fillWidth: true
                text: project.name
                color: "#111827"
                font.bold: true
                font.pixelSize: 15
                elide: Text.ElideRight
            }
        }

        Label {
            Layout.fillWidth: true
            text: project.statusLabel
            color: project.statusColor
            font.bold: true
            elide: Text.ElideRight
        }

        Label {
            Layout.fillWidth: true
            text: project.isConfigured ? project.localPathDisplay : "点击后在右侧配置本机目录"
            color: "#6b7280"
            font.pixelSize: 12
            elide: Text.ElideMiddle
        }
    }
}
