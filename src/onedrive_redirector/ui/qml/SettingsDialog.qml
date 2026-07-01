import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: root
    property string currentRoot: ""
    signal chooseRootClicked()
    signal openLogClicked()

    modal: true
    width: 560
    standardButtons: Dialog.NoButton
    title: "设置"

    contentItem: ColumnLayout {
        spacing: 14

        Text {
            Layout.fillWidth: true
            text: root.currentRoot ? ("当前 OneDrive 根目录：\n" + root.currentRoot) : "当前尚未设置 OneDrive 根目录。"
            wrapMode: Text.WordWrap
            color: "#334155"
            font.pixelSize: 14
        }

        RowLayout {
            spacing: 10

            AnimatedButton {
                text: "更改 OneDrive 根目录"
                onClicked: root.chooseRootClicked()
            }

            AnimatedButton {
                text: "打开日志目录"
                baseColor: "#475569"
                onClicked: root.openLogClicked()
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignRight

            AnimatedButton {
                text: "关闭"
                baseColor: "#94a3b8"
                onClicked: root.close()
            }
        }
    }
}
