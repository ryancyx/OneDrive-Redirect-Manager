import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: root
    property string localPath: ""
    property string cloudPath: ""
    signal choose(string strategy)

    modal: true
    width: 620
    standardButtons: Dialog.NoButton
    title: "检测到冲突"

    contentItem: ColumnLayout {
        spacing: 12

        Text {
            Layout.fillWidth: true
            text: "检测到冲突：本地文件夹和 OneDrive 目标文件夹中都已有数据。"
            wrapMode: Text.WordWrap
            color: "#111827"
            font.pixelSize: 15
            font.bold: true
        }

        Text {
            Layout.fillWidth: true
            text: "本地路径：\n" + root.localPath + "\n\nOneDrive 路径：\n" + root.cloudPath
            wrapMode: Text.WordWrap
            color: "#475569"
        }

        AnimatedButton {
            Layout.fillWidth: true
            text: "备份本地文件夹并使用云端数据"
            baseColor: "#b45309"
            onClicked: root.choose("use_cloud")
        }

        AnimatedButton {
            Layout.fillWidth: true
            text: "备份云端文件夹并使用本地数据"
            baseColor: "#b3261e"
            onClicked: root.choose("use_local")
        }

        AnimatedButton {
            Layout.alignment: Qt.AlignRight
            text: "取消"
            baseColor: "#94a3b8"
            onClicked: root.close()
        }
    }
}
