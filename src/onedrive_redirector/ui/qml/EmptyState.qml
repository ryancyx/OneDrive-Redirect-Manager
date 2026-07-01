import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    property string title: "暂无项目"
    property string description: "请先创建一个同步项目。"

    Column {
        anchors.centerIn: parent
        width: Math.min(parent.width - 40, 420)
        spacing: 10

        Text {
            width: parent.width
            text: root.title
            color: "#111827"
            font.pixelSize: 24
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            width: parent.width
            text: root.description
            color: "#6b7280"
            font.pixelSize: 14
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
    }
}
