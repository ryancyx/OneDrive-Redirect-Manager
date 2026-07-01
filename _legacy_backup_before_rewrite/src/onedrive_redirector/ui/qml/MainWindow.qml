import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    width: 1200
    height: 760
    minimumWidth: 980
    minimumHeight: 640
    visible: true
    title: "OneDrive 目录重定向管理器"
    color: "#f3f6fb"

    property bool bridgeReady: typeof bridge !== "undefined" && bridge !== null
    property var settingsSummary: bridgeReady ? bridge.settingsSummary : ({
        rootPath: "",
        isConfigured: false,
        settingsPath: "",
        logDir: "",
        projectCount: 0
    })
    property var projectListData: bridgeReady ? bridge.projectList : []
    property var selectedProject: bridgeReady ? bridge.selectedProject : ({})
    property string recentActivityText: bridgeReady ? bridge.recentActivity : "正在加载。"

    readonly property var emptyProject: ({
        id: "",
        name: "",
        localPath: "",
        cloudRelativePath: "",
        cloudAbsolutePath: "",
        statusCode: "",
        statusLabel: "",
        statusColor: "#6b7280",
        message: ""
    })

    function safeProject() {
        return selectedProject && selectedProject.id ? selectedProject : emptyProject
    }

    function hasProject() {
        return safeProject().id !== ""
    }

    Rectangle {
        anchors.fill: parent
        color: "#f3f6fb"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 14

        Rectangle {
            Layout.fillWidth: true
            radius: 18
            color: "#ffffff"
            border.color: "#dbe3f0"
            border.width: 1
            implicitHeight: 98

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8

                Label {
                    text: "OneDrive 目录重定向管理器"
                    font.pixelSize: 26
                    font.bold: true
                    color: "#111827"
                }

                Label {
                    Layout.fillWidth: true
                    text: settingsSummary.isConfigured
                        ? ("当前 OneDrive 根目录：" + settingsSummary.rootPath)
                        : "请先在设置中选择 OneDrive 根目录"
                    color: settingsSummary.isConfigured ? "#4b5563" : "#b45309"
                    elide: Text.ElideMiddle
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "新建"
                enabled: bridgeReady
                onClicked: bridge.createProject()
            }

            Button {
                text: "编辑"
                enabled: bridgeReady && root.hasProject()
                onClicked: bridge.editProject(root.safeProject().id)
            }

            Button {
                text: "删除"
                enabled: bridgeReady && root.hasProject()
                onClicked: bridge.deleteProject(root.safeProject().id)
            }

            Button {
                text: "刷新"
                enabled: bridgeReady
                onClicked: bridge.refreshStatus()
            }

            Button {
                text: "设置"
                enabled: bridgeReady
                onClicked: bridge.openSettings()
            }

            Button {
                text: "恢复到本地并取消同步"
                enabled: bridgeReady && root.hasProject()
                onClicked: bridge.restoreToLocal(root.safeProject().id)
            }

            Item { Layout.fillWidth: true }

            Button {
                text: "打开日志"
                enabled: bridgeReady
                onClicked: bridge.openLog()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 18
            color: "#ffffff"
            border.color: "#dbe3f0"
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 0

                    Repeater {
                        model: [
                            { label: "项目 ID", width: 150 },
                            { label: "名称", width: 200 },
                            { label: "本地源文件夹路径", width: 300 },
                            { label: "OneDrive 中的路径", width: 300 },
                            { label: "运行状态", width: 180 }
                        ]

                        delegate: Rectangle {
                            required property var modelData
                            width: modelData.width
                            height: 42
                            color: "#eef3fb"
                            border.color: "#dbe3f0"
                            border.width: 1

                            Label {
                                anchors.centerIn: parent
                                text: modelData.label
                                font.bold: true
                                color: "#334155"
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#ffffff"

                    Label {
                        anchors.centerIn: parent
                        visible: projectListData.length === 0
                        text: settingsSummary.isConfigured
                            ? "当前还没有同步项目。\n点击上方“新建”开始。"
                            : "请先在设置中选择 OneDrive 根目录。"
                        horizontalAlignment: Text.AlignHCenter
                        color: "#6b7280"
                    }

                    ListView {
                        anchors.fill: parent
                        clip: true
                        visible: projectListData.length > 0
                        model: projectListData

                        delegate: Rectangle {
                            required property var modelData
                            width: ListView.view.width
                            height: 54
                            color: root.safeProject().id === modelData.id ? "#eff6ff" : "#ffffff"
                            border.color: "#e5e7eb"
                            border.width: 1

                            MouseArea {
                                anchors.fill: parent
                                acceptedButtons: Qt.LeftButton
                                onClicked: bridge.selectProject(modelData.id)
                                onDoubleClicked: bridge.editProject(modelData.id)
                            }

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 0

                                Label { text: modelData.id; width: 150; elide: Text.ElideRight; color: "#111827" }
                                Label { text: modelData.name; width: 200; elide: Text.ElideRight; color: "#111827" }
                                Label { text: modelData.localPath; width: 300; elide: Text.ElideMiddle; color: "#374151" }
                                Label { text: modelData.cloudRelativePath; width: 300; elide: Text.ElideMiddle; color: "#374151" }
                                Label { text: modelData.statusLabel; width: 180; color: modelData.statusColor; font.bold: true }
                            }
                        }

                        ScrollBar.vertical: ScrollBar {}
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            radius: 16
            color: "#ffffff"
            border.color: "#dbe3f0"
            border.width: 1
            implicitHeight: 92

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 6

                Label {
                    text: root.hasProject()
                        ? ("已选项目：" + root.safeProject().name + "（" + root.safeProject().id + "）")
                        : "请选择一个同步项目"
                    font.bold: true
                    color: "#111827"
                }

                Label {
                    Layout.fillWidth: true
                    text: root.hasProject()
                        ? ("本地：" + root.safeProject().localPath + "    云端：" + root.safeProject().cloudRelativePath + "    状态：" + root.safeProject().statusLabel)
                        : "双击列表项可以编辑项目。"
                    color: root.hasProject() ? root.safeProject().statusColor : "#6b7280"
                    elide: Text.ElideMiddle
                }

                Label {
                    Layout.fillWidth: true
                    text: "最近操作：" + recentActivityText
                    color: "#4b5563"
                    elide: Text.ElideRight
                }
            }
        }
    }
}
