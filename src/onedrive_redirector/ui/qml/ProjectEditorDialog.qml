import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

Dialog {
    id: root

    property bool editMode: false
    property string projectId: ""
    property string nameValue: ""
    property string localPathValue: ""
    property string cloudPathValue: "data/"
    property string currentRoot: ""
    property bool busy: false
    signal submit(var payload)

    modal: true
    width: 860
    height: 590
    x: parent ? Math.round((parent.width - width) / 2) : 0
    y: parent ? Math.round((parent.height - height) / 2) : 0
    padding: 0
    standardButtons: Dialog.NoButton
    title: ""

    function pathFromUrl(urlValue) {
        var s = decodeURIComponent(String(urlValue))
        if (s.indexOf("file:///") === 0)
            s = s.substring(8)
        else if (s.indexOf("file://") === 0)
            s = s.substring(7)
        if (Qt.platform.os === "windows") {
            if (s.length >= 3 && s.charAt(0) === "/" && s.charAt(2) === ":")
                s = s.substring(1)
            s = s.replace(/\//g, "\\")
        }
        return s
    }

    function normalizeSlash(pathValue) {
        return String(pathValue || "").replace(/\\/g, "/").replace(/\/+$/g, "")
    }

    function relativeToRoot(pathValue) {
        var rootPath = normalizeSlash(root.currentRoot)
        var selectedPath = normalizeSlash(pathValue)
        if (!rootPath || !selectedPath)
            return ""
        if (selectedPath.toLowerCase() === rootPath.toLowerCase())
            return "data/"
        var prefix = rootPath + "/"
        if (selectedPath.toLowerCase().indexOf(prefix.toLowerCase()) === 0)
            return selectedPath.substring(prefix.length)
        return ""
    }

    onOpened: {
        idField.text = root.projectId
        nameField.text = root.nameValue
        localField.text = root.localPathValue
        cloudField.text = root.cloudPathValue || "data/"
        cloudHint.text = "相对 Cloud 工作目录，建议放在 data/ 下"
    }

    FolderDialog {
        id: localFolderDialog
        title: "选择本地源文件夹"
        onAccepted: {
            localField.text = root.pathFromUrl(selectedFolder)
        }
    }

    FolderDialog {
        id: cloudFolderDialog
        title: "选择 Cloud 中的目标文件夹"
        onAccepted: {
            var absPath = root.pathFromUrl(selectedFolder)
            var relPath = root.relativeToRoot(absPath)
            if (relPath) {
                cloudField.text = relPath
                cloudHint.text = "已转换为相对路径：" + relPath
            } else {
                cloudHint.text = "请选择 Cloud 工作目录内部文件夹，或手动填写 data/xxx"
            }
        }
    }

    background: Rectangle {
        radius: 22
        color: "#ffffff"
        border.color: "#dbe4ef"
        border.width: 1
    }

    contentItem: Item {
        implicitWidth: root.width
        implicitHeight: root.height

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            Rectangle {
                Layout.fillWidth: true
                height: 74
                radius: 22
                color: "#f8fafc"
                border.color: "#edf2f7"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 26
                    anchors.rightMargin: 26
                    anchors.topMargin: 12
                    anchors.bottomMargin: 10
                    spacing: 3

                    Text {
                        text: root.editMode ? "编辑同步项目" : "新建同步项目"
                        color: "#0f172a"
                        font.pixelSize: 23
                        font.weight: Font.Bold
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "本地路径会成为 junction 链接入口，真实文件保存在 Cloud 目标路径中。"
                        color: "#64748b"
                        font.pixelSize: 13
                        wrapMode: Text.NoWrap
                    }
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 26
                    anchors.rightMargin: 26
                    anchors.topMargin: 18
                    anchors.bottomMargin: 10
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 18

                        ColumnLayout {
                            Layout.preferredWidth: 470
                            Layout.maximumWidth: 500
                            spacing: 7
                            Text { text: "项目 ID"; color: "#1f2937"; font.pixelSize: 14; font.weight: Font.Bold }
                            TextField {
                                id: idField
                                Layout.fillWidth: true
                                Layout.preferredHeight: 44
                                placeholderText: "例如 game-save"
                                selectByMouse: true
                                font.pixelSize: 15
                                leftPadding: 14
                                rightPadding: 14
                                topPadding: 8
                                bottomPadding: 8
                                background: Rectangle { radius: 12; color: idField.activeFocus ? "#ffffff" : "#fbfdff"; border.width: 1; border.color: idField.activeFocus ? "#93c5fd" : "#dbe4ef" }
                            }
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "英文、数字和短横线，创建后不建议修改"
                            color: "#64748b"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 18

                        ColumnLayout {
                            Layout.preferredWidth: 470
                            Layout.maximumWidth: 500
                            spacing: 7
                            Text { text: "项目名称"; color: "#1f2937"; font.pixelSize: 14; font.weight: Font.Bold }
                            TextField {
                                id: nameField
                                Layout.fillWidth: true
                                Layout.preferredHeight: 44
                                placeholderText: "例如 游戏存档"
                                selectByMouse: true
                                font.pixelSize: 15
                                leftPadding: 14
                                rightPadding: 14
                                topPadding: 8
                                bottomPadding: 8
                                background: Rectangle { radius: 12; color: nameField.activeFocus ? "#ffffff" : "#fbfdff"; border.width: 1; border.color: nameField.activeFocus ? "#93c5fd" : "#dbe4ef" }
                            }
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "列表显示名称，可以使用中文"
                            color: "#64748b"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 18

                        ColumnLayout {
                            Layout.preferredWidth: 470
                            Layout.maximumWidth: 500
                            spacing: 7
                            Text { text: "本地源文件夹路径"; color: "#1f2937"; font.pixelSize: 14; font.weight: Font.Bold }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10
                                TextField {
                                    id: localField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 44
                                    placeholderText: "选择本地源文件夹"
                                    selectByMouse: true
                                    font.pixelSize: 15
                                    leftPadding: 14
                                    rightPadding: 14
                                    topPadding: 8
                                    bottomPadding: 8
                                    background: Rectangle { radius: 12; color: localField.activeFocus ? "#ffffff" : "#fbfdff"; border.width: 1; border.color: localField.activeFocus ? "#93c5fd" : "#dbe4ef" }
                                }
                                AnimatedButton {
                                    text: "选择"
                                    subtle: true
                                    enabled: !root.busy
                                    onClicked: localFolderDialog.open()
                                }
                            }
                        }

                        Text {
                            Layout.fillWidth: true
                            text: "原软件使用的本地路径，确认后会成为 junction 入口"
                            color: "#64748b"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 18

                        ColumnLayout {
                            Layout.preferredWidth: 470
                            Layout.maximumWidth: 500
                            spacing: 7
                            Text { text: "Cloud 中的路径"; color: "#1f2937"; font.pixelSize: 14; font.weight: Font.Bold }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10
                                TextField {
                                    id: cloudField
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 44
                                    placeholderText: "例如 data/game-save"
                                    selectByMouse: true
                                    font.pixelSize: 15
                                    leftPadding: 14
                                    rightPadding: 14
                                    topPadding: 8
                                    bottomPadding: 8
                                    background: Rectangle { radius: 12; color: cloudField.activeFocus ? "#ffffff" : "#fbfdff"; border.width: 1; border.color: cloudField.activeFocus ? "#93c5fd" : "#dbe4ef" }
                                }
                                AnimatedButton {
                                    text: "选择"
                                    subtle: true
                                    enabled: root.currentRoot.length > 0 && !root.busy
                                    onClicked: cloudFolderDialog.open()
                                }
                            }
                        }

                        Text {
                            id: cloudHint
                            Layout.fillWidth: true
                            text: "相对 Cloud 工作目录，建议放在 data/ 下"
                            color: "#64748b"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "确认后会根据当前文件状态自动迁移、创建链接或弹出冲突处理。"
                        color: "#64748b"
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            Item {
                Layout.fillWidth: true
                height: 64

                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    height: 1
                    color: "#edf2f7"
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 26
                    anchors.rightMargin: 26
                    spacing: 10

                    Item { Layout.fillWidth: true }

                    AnimatedButton {
                        text: "取消"
                        subtle: true
                        enabled: !root.busy
                        onClicked: root.close()
                    }

                    AnimatedButton {
                        text: root.editMode ? "保存修改" : "创建项目"
                        enabled: !root.busy
                        onClicked: {
                            root.submit({
                                "id": idField.text.trim(),
                                "name": nameField.text.trim(),
                                "local_path": localField.text.trim(),
                                "cloud_relative_path": cloudField.text.trim()
                            })
                        }
                    }
                }
            }
        }
    }
}
