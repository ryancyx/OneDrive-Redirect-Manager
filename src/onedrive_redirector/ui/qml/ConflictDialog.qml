import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: root

    property string localPath: ""
    property string cloudPath: ""
    property bool busy: false
    signal choose(string strategy)

    modal: true
    width: 680
    x: parent ? Math.round((parent.width - width) / 2) : 0
    y: parent ? Math.round((parent.height - implicitHeight) / 2) : 0
    padding: 0
    standardButtons: Dialog.NoButton
    title: ""

    background: Rectangle {
        radius: 22
        color: "#ffffff"
        border.color: "#f4c7a1"
        border.width: 1
    }

    contentItem: ColumnLayout {
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            height: 84
            radius: 22
            color: "#fff7ed"
            border.color: "#fed7aa"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 14

                Rectangle {
                    width: 44
                    height: 44
                    radius: 16
                    color: "#fed7aa"
                    Text { anchors.centerIn: parent; text: "!"; color: "#b45309"; font.pixelSize: 24; font.weight: Font.Bold }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 3
                    Text { text: "检测到冲突"; color: "#92400e"; font.pixelSize: 22; font.weight: Font.Bold }
                    Text { text: "本地文件夹和 Cloud 目标文件夹中都已有数据，需要选择保留哪一侧。"; color: "#9a3412"; font.pixelSize: 13; wrapMode: Text.WordWrap }
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.margins: 22
            spacing: 14

            Rectangle {
                Layout.fillWidth: true
                radius: 16
                color: "#f8fafc"
                border.color: "#e5ebf3"
                implicitHeight: pathColumn.implicitHeight + 28

                ColumnLayout {
                    id: pathColumn
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 8

                    Text { text: "本地路径"; color: "#64748b"; font.pixelSize: 12; font.weight: Font.Bold }
                    Text { Layout.fillWidth: true; text: root.localPath; color: "#334155"; font.pixelSize: 13; wrapMode: Text.WrapAnywhere }
                    Text { text: "Cloud 路径"; color: "#64748b"; font.pixelSize: 12; font.weight: Font.Bold }
                    Text { Layout.fillWidth: true; text: root.cloudPath; color: "#334155"; font.pixelSize: 13; wrapMode: Text.WrapAnywhere }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                radius: 16
                color: "#fffbeb"
                border.color: "#fde68a"
                implicitHeight: 48
                Text {
                    anchors.fill: parent
                    anchors.margins: 12
                    text: "所有冲突处理都会先生成 _backup 备份，不会覆盖已有备份。"
                    color: "#92400e"
                    font.pixelSize: 13
                    verticalAlignment: Text.AlignVCenter
                    wrapMode: Text.WordWrap
                }
            }

            AnimatedButton {
                Layout.fillWidth: true
                text: "备份本地文件夹，并使用云端数据"
                baseColor: "#b45309"
                enabled: !root.busy
                onClicked: root.choose("use_cloud")
            }

            AnimatedButton {
                Layout.fillWidth: true
                text: "备份云端文件夹，并使用本地数据"
                baseColor: "#dc2626"
                enabled: !root.busy
                onClicked: root.choose("use_local")
            }

            RowLayout {
                Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                AnimatedButton { text: "取消"; subtle: true; enabled: !root.busy; onClicked: root.close() }
            }
        }
    }
}