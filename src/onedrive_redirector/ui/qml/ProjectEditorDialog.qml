import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: root
    property bool editMode: false
    property string projectId: ""
    property string nameValue: ""
    property string localPathValue: ""
    property string cloudPathValue: "data/"
    signal submit(var payload)

    modal: true
    width: 560
    standardButtons: Dialog.NoButton
    title: editMode ? "编辑项目" : "新建项目"

    contentItem: ColumnLayout {
        spacing: 12

        TextField {
            id: idField
            Layout.fillWidth: true
            placeholderText: "项目 ID"
            text: root.projectId
        }

        TextField {
            id: nameField
            Layout.fillWidth: true
            placeholderText: "项目名称"
            text: root.nameValue
        }

        TextField {
            id: localField
            Layout.fillWidth: true
            placeholderText: "本地源文件夹路径"
            text: root.localPathValue
        }

        TextField {
            id: cloudField
            Layout.fillWidth: true
            placeholderText: "OneDrive 中的路径"
            text: root.cloudPathValue
        }

        RowLayout {
            Layout.alignment: Qt.AlignRight
            spacing: 10

            AnimatedButton {
                text: "取消"
                baseColor: "#94a3b8"
                onClicked: root.close()
            }

            AnimatedButton {
                text: root.editMode ? "保存修改" : "创建项目"
                onClicked: {
                    root.submit({
                        "id": idField.text,
                        "name": nameField.text,
                        "local_path": localField.text,
                        "cloud_relative_path": cloudField.text
                    })
                }
            }
        }
    }
}
