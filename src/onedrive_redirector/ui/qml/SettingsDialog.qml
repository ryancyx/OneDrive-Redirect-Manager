import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: root

    property string currentRoot: ""
    property bool busy: false
    signal chooseRootClicked()
    signal openLogClicked()

    modal: true
    width: 700
    height: 500
    x: parent ? Math.round((parent.width - width) / 2) : 0
    y: parent ? Math.round((parent.height - height) / 2) : 0
    padding: 0
    standardButtons: Dialog.NoButton
    title: ""

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
                height: 86
                radius: 22
                color: "#f8fafc"
                border.color: "#edf2f7"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 24
                    anchors.rightMargin: 24
                    anchors.topMargin: 16
                    anchors.bottomMargin: 14
                    spacing: 4

                    Text {
                        text: "设置"
                        color: "#0f172a"
                        font.pixelSize: 24
                        font.weight: Font.Bold
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "选择 Cloud 工作目录。项目配置保存在该目录，日志保存在本机 AppData。"
                        color: "#64748b"
                        font.pixelSize: 14
                        wrapMode: Text.WordWrap
                    }
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 24
                    spacing: 18

                    Rectangle {
                        Layout.fillWidth: true
                        radius: 18
                        color: root.currentRoot ? "#f0f7ff" : "#fff7ed"
                        border.color: root.currentRoot ? "#bfdbfe" : "#fed7aa"
                        implicitHeight: Math.max(130, pathText.implicitHeight + 76)

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 18
                            spacing: 10

                            Text {
                                text: root.currentRoot ? "当前 Cloud 工作目录" : "尚未设置 Cloud 工作目录"
                                color: root.currentRoot ? "#1d4ed8" : "#b45309"
                                font.pixelSize: 14
                                font.weight: Font.Bold
                            }

                            Text {
                                id: pathText
                                Layout.fillWidth: true
                                text: root.currentRoot || "请点击下方按钮，通过系统资源管理器选择一个 Cloud 工作目录。"
                                color: "#334155"
                                font.pixelSize: 15
                                wrapMode: Text.WrapAnywhere
                                lineHeight: 1.18
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        radius: 18
                        color: "#f8fafc"
                        border.color: "#e5ebf3"
                        implicitHeight: 118

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 18
                            spacing: 8

                            Text {
                                text: "路径选择说明"
                                color: "#0f172a"
                                font.pixelSize: 15
                                font.weight: Font.Bold
                            }

                            Text {
                                Layout.fillWidth: true
                                text: "点击“更改 Cloud 工作目录”会打开系统目录选择器，不需要手动复制路径。建议选择云盘目录内专门用于本工具的 Cloud 工作目录。"
                                color: "#64748b"
                                font.pixelSize: 13
                                wrapMode: Text.WordWrap
                                lineHeight: 1.2
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            Item {
                Layout.fillWidth: true
                height: 74

                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    height: 1
                    color: "#edf2f7"
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 24
                    anchors.rightMargin: 24
                    spacing: 10

                    AnimatedButton {
                        text: "更改 Cloud 工作目录"
                        enabled: !root.busy
                        onClicked: root.chooseRootClicked()
                    }

                    AnimatedButton {
                        text: "打开日志目录"
                        subtle: true
                        enabled: !root.busy
                        onClicked: root.openLogClicked()
                    }

                    Item { Layout.fillWidth: true }

                    AnimatedButton {
                        text: "关闭"
                        subtle: true
                        enabled: !root.busy
                        onClicked: root.close()
                    }
                }
            }
        }
    }
}