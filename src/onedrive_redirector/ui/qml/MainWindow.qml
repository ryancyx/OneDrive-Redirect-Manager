import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

ApplicationWindow {
    id: root
    width: 1240
    height: 780
    visible: true
    title: "OneDrive 目录重定向管理器"
    color: "#f3f6fb"

    property bool controllerReady: typeof controller !== "undefined" && controller !== null
    property var projectListData: controllerReady ? controller.projectList : []
    property string currentRootText: controllerReady ? controller.currentRoot : ""
    property bool hasRootValue: controllerReady ? controller.hasRoot : false
    property string selectedProjectId: ""

    readonly property var emptyProject: ({
        id: "",
        name: "",
        localPath: "",
        cloudRelativePath: "",
        cloudAbsolutePath: "",
        statusCode: "",
        statusText: "未选择项目",
        statusLevel: "muted",
        statusColor: "#6b7280",
        statusIcon: "○",
        message: "请选择一个同步项目。"
    })

    property var selectedProject: {
        for (var i = 0; i < projectListData.length; ++i) {
            if (projectListData[i].id === selectedProjectId) {
                return projectListData[i]
            }
        }
        return emptyProject
    }

    function openCreateDialog() {
        projectDialog.editMode = false
        projectDialog.projectId = ""
        projectDialog.nameValue = ""
        projectDialog.localPathValue = ""
        projectDialog.cloudPathValue = "data/"
        projectDialog.open()
    }

    function openEditDialog() {
        if (!selectedProjectId)
            return
        projectDialog.editMode = true
        projectDialog.projectId = selectedProject.id || ""
        projectDialog.nameValue = selectedProject.name || ""
        projectDialog.localPathValue = selectedProject.localPath || ""
        projectDialog.cloudPathValue = selectedProject.cloudRelativePath || "data/"
        projectDialog.open()
    }

    function safeString(value, fallback) {
        if (value === undefined || value === null || value === "")
            return fallback === undefined ? "" : fallback
        return String(value)
    }

    function selectedCloudAbsolutePath() {
        if (selectedProject && selectedProject.cloudAbsolutePath)
            return String(selectedProject.cloudAbsolutePath)
        if (selectedProject && selectedProject.cloudRelativePath && currentRootText)
            return currentRootText + "/" + selectedProject.cloudRelativePath
        return ""
    }

    function selectedLocalPath() {
        if (selectedProject && selectedProject.localPath)
            return String(selectedProject.localPath)
        return ""
    }

    SettingsDialog {
        id: settingsDialog
        currentRoot: currentRootText
        onChooseRootClicked: controller.chooseOneDriveRoot()
        onOpenLogClicked: controller.openLogDirectory()
    }

    ProjectEditorDialog {
        id: projectDialog
        onSubmit: function(payload) {
            if (editMode) {
                controller.updateProject(selectedProjectId, payload)
            } else {
                controller.createProject(payload)
            }
            close()
        }
    }

    ConflictDialog {
        id: conflictDialog
        onChoose: function(strategy) {
            controller.resolveConflict(strategy)
            close()
        }
    }

    Connections {
        target: controllerReady ? controller : null

        function onProjectsChanged() {
            if (selectedProjectId && !root.selectedProject.id)
                selectedProjectId = ""
        }

        function onRootChanged() {
            if (!controller.hasRoot)
                selectedProjectId = ""
        }

        function onErrorOccurred(message) {
            errorDialog.text = message
            errorDialog.open()
        }

        function onMessageOccurred(message) {
            infoDialog.text = message
            infoDialog.open()
        }

        function onConflictRequired(action, payload) {
            conflictDialog.localPath = safeString(payload.local_path, "")
            if (hasRootValue)
                conflictDialog.cloudPath = safeString(currentRootText, "") + "/" + safeString(payload.cloud_relative_path, "")
            else
                conflictDialog.cloudPath = safeString(payload.cloud_relative_path, "")
            conflictDialog.open()
        }
    }

    MessageDialog {
        id: errorDialog
        title: "操作失败"
        buttons: MessageDialog.Ok
    }

    MessageDialog {
        id: infoDialog
        title: "提示"
        buttons: MessageDialog.Ok
    }

    Dialog {
        id: deleteConfirm
        modal: true
        title: "删除同步项目"
        standardButtons: Dialog.NoButton
        width: 560
        property bool deleteCloud: false
        property bool deleteLocalLink: false

        onOpened: {
            deleteCloud = false
            deleteLocalLink = false
        }

        contentItem: ColumnLayout {
            spacing: 14

            Text {
                Layout.fillWidth: true
                text: "即将删除同步项目。\n\n删除后，软件将不再管理该同步关系。\n如果本地路径当前是链接，原软件可能无法继续正常访问该路径。"
                wrapMode: Text.WordWrap
                color: "#111827"
                font.pixelSize: 14
            }

            CheckBox {
                id: deleteCloudCheckbox
                text: "同时删除 OneDrive 中的目标文件夹"
                checked: false
                onCheckedChanged: deleteConfirm.deleteCloud = checked
            }

            CheckBox {
                id: deleteLocalLinkCheckbox
                text: "同时删除本地链接"
                checked: false
                onCheckedChanged: deleteConfirm.deleteLocalLink = checked
            }

            RowLayout {
                Layout.alignment: Qt.AlignRight
                spacing: 10

                AnimatedButton {
                    text: "取消"
                    baseColor: "#94a3b8"
                    onClicked: deleteConfirm.close()
                }

                AnimatedButton {
                    text: "确认删除"
                    baseColor: "#b3261e"
                    onClicked: {
                        if (deleteConfirm.deleteCloud) {
                            var lines = []
                            lines.push("即将删除 OneDrive 中的目标文件夹：")
                            lines.push("")
                            lines.push(selectedCloudAbsolutePath())
                            if (deleteConfirm.deleteLocalLink) {
                                lines.push("")
                                lines.push("同时将删除本地链接入口：")
                                lines.push("")
                                lines.push(selectedLocalPath())
                                lines.push("")
                                lines.push("删除本地链接只会删除 junction 入口，不会删除 OneDrive 中的真实数据。")
                            }
                            lines.push("")
                            lines.push("此操作不可自动恢复。")
                            cloudDeleteConfirm.text = lines.join("\n")
                            cloudDeleteConfirm.open()
                        } else if (selectedProjectId) {
                            controller.deleteProject(selectedProjectId, false, deleteConfirm.deleteLocalLink)
                        }
                        deleteConfirm.close()
                    }
                }
            }
        }
    }

    MessageDialog {
        id: cloudDeleteConfirm
        title: "确认删除云端目录"
        text: ""
        buttons: MessageDialog.Ok | MessageDialog.Cancel
        onAccepted: {
            if (selectedProjectId)
                controller.deleteProject(selectedProjectId, true, deleteConfirm.deleteLocalLink)
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#f3f6fb"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16

        Rectangle {
            Layout.fillWidth: true
            radius: 24
            color: "#ffffff"
            border.color: "#dbe3f0"
            border.width: 1
            implicitHeight: 110

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 8

                Text {
                    text: "OneDrive 目录重定向管理器"
                    color: "#111827"
                    font.pixelSize: 28
                    font.bold: true
                }

                Text {
                    Layout.fillWidth: true
                    text: hasRootValue
                        ? ("当前 OneDrive 根目录： " + currentRootText)
                        : "当前尚未设置 OneDrive 根目录，请先在设置中选择。"
                    color: hasRootValue ? "#475569" : "#b45309"
                    font.pixelSize: 14
                    elide: Text.ElideMiddle
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            AnimatedButton { text: "新建"; enabled: controllerReady; onClicked: openCreateDialog() }
            AnimatedButton { text: "编辑"; enabled: controllerReady && !!selectedProjectId; onClicked: openEditDialog() }
            AnimatedButton {
                text: "删除"
                enabled: controllerReady && !!selectedProjectId
                baseColor: "#b3261e"
                onClicked: deleteConfirm.open()
            }
            AnimatedButton { text: "刷新"; baseColor: "#475569"; enabled: controllerReady; onClicked: controller.refreshProjects() }
            AnimatedButton { text: "设置"; baseColor: "#475569"; enabled: controllerReady; onClicked: settingsDialog.open() }
            AnimatedButton {
                text: "恢复到本地并取消同步"
                baseColor: "#0f766e"
                enabled: controllerReady && !!selectedProjectId
                onClicked: controller.restoreProjectToLocal(selectedProjectId)
            }

            Item { Layout.fillWidth: true }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 24
            color: "#ffffff"
            border.color: "#dbe3f0"
            border.width: 1

            Loader {
                anchors.fill: parent
                anchors.margins: 14
                active: true
                sourceComponent: projectListData.length > 0 ? tableComponent : emptyComponent
            }

            Component {
                id: emptyComponent
                EmptyState {
                    title: hasRootValue ? "还没有同步项目" : "请先设置 OneDrive 根目录"
                    description: hasRootValue
                        ? "点击上方“新建”按钮，创建第一个同步项目。"
                        : "打开“设置”，选择一个 OneDrive 工作目录后再继续。"
                }
            }

            Component {
                id: tableComponent
                ProjectTable {
                    modelData: projectListData
                    selectedId: selectedProjectId
                    onProjectSelected: function(projectId) { selectedProjectId = projectId }
                    onProjectDoubleClicked: function(projectId) {
                        selectedProjectId = projectId
                        openEditDialog()
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            radius: 20
            color: "#ffffff"
            border.color: "#dbe3f0"
            border.width: 1
            implicitHeight: 108

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8

                Text {
                    text: selectedProjectId
                        ? ("已选项目： " + safeString(selectedProject.name, "") + "（" + safeString(selectedProject.id, "") + "）")
                        : "请选择一个同步项目"
                    color: "#111827"
                    font.pixelSize: 16
                    font.bold: true
                }

                RowLayout {
                    spacing: 10

                    StatusBadge {
                        statusText: safeString(selectedProject.statusText, "未选择项目")
                        statusColor: safeString(selectedProject.statusColor, "#6b7280")
                        statusIcon: safeString(selectedProject.statusIcon, "○")
                    }

                    Text {
                        Layout.fillWidth: true
                        text: safeString(selectedProject.message, "请选择一个同步项目，查看当前状态。")
                        color: "#475569"
                        elide: Text.ElideRight
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: selectedProjectId
                        ? ("本地：" + safeString(selectedProject.localPath, "") + "    云端：" + safeString(selectedProject.cloudRelativePath, ""))
                        : "双击列表项可直接编辑项目。"
                    color: "#64748b"
                    elide: Text.ElideMiddle
                }
            }
        }
    }

    Component.onCompleted: {
        if (controllerReady && !hasRootValue)
            settingsDialog.open()
    }
}
