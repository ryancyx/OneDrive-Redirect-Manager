import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

ApplicationWindow {
    id: root

    width: 1280
    height: 820
    minimumWidth: 1100
    minimumHeight: 720
    visible: true
    title: "Cloud Redirect Manager"
    color: "#f6f8fb"

    property bool controllerReady: typeof controller !== "undefined" && controller !== null
    property var projectListData: controllerReady ? controller.projectList : []
    property string currentRootText: controllerReady ? controller.currentRoot : ""
    property bool hasRootValue: controllerReady ? controller.hasRoot : false
    property string selectedProjectId: ""
    property string toastText: ""
    property bool toastVisible: false
    readonly property bool controllerBusy: controllerReady ? controller.busy : false
    readonly property string controllerBusyText: controllerReady ? controller.busyText : ""

    readonly property color pageBg: "#f6f8fb"
    readonly property color cardBg: "#ffffff"
    readonly property color borderColor: "#dde6f2"
    readonly property color textMain: "#0f172a"
    readonly property color textSecond: "#64748b"
    readonly property color brand: "#2563eb"

    readonly property var emptyProject: ({
        id: "",
        name: "",
        localPath: "",
        cloudRelativePath: "",
        cloudAbsolutePath: "",
        statusCode: "",
        statusText: "未选择项目",
        statusLevel: "muted",
        statusColor: "#64748b",
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

    function showToast(message) {
        toastText = message || "操作完成。"
        toastVisible = true
        toastTimer.restart()
    }

    function openCreateDialog() {
        if (controllerBusy)
            return
        if (!hasRootValue) {
            settingsDialog.open()
            showToast("请先设置 Cloud 工作目录。")
            return
        }
        projectDialog.editMode = false
        projectDialog.projectId = ""
        projectDialog.nameValue = ""
        projectDialog.localPathValue = ""
        projectDialog.cloudPathValue = "data/"
        projectDialog.open()
    }

    function openEditDialog() {
        if (controllerBusy)
            return
        if (!selectedProjectId)
            return
        projectDialog.editMode = true
        projectDialog.projectId = selectedProject.id || ""
        projectDialog.nameValue = selectedProject.name || ""
        projectDialog.localPathValue = selectedProject.localPath || ""
        projectDialog.cloudPathValue = selectedProject.cloudRelativePath || "data/"
        projectDialog.open()
    }

    function handleProjectContextAction(action, projectId) {
        if (controllerBusy)
            return
        selectedProjectId = projectId || selectedProjectId
        if (action === "refresh") {
            controller.refreshProjects()
        } else if (action === "edit") {
            openEditDialog()
        } else if (action === "delete") {
            deleteConfirm.open()
        } else if (action === "settings") {
            settingsDialog.open()
        }
    }

    Timer {
        id: toastTimer
        interval: 2300
        repeat: false
        onTriggered: toastVisible = false
    }

    SettingsDialog {
        id: settingsDialog
        currentRoot: currentRootText
        busy: controllerBusy
        onChooseRootClicked: controller.chooseOneDriveRoot()
        onOpenLogClicked: controller.openLogDirectory()
    }

    ProjectEditorDialog {
        id: projectDialog
        currentRoot: currentRootText
        busy: controllerBusy
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
        busy: controllerBusy
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
            showToast(message)
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

    Dialog {
        id: deleteConfirm
        enabled: !controllerBusy
        modal: true
        width: 660
        x: parent ? Math.round((parent.width - width) / 2) : 0
        y: parent ? Math.round((parent.height - implicitHeight) / 2) : 0
        padding: 0
        standardButtons: Dialog.NoButton
        title: ""
        property bool deleteCloud: false
        property bool deleteLocalLink: false

        onOpened: {
            deleteCloudCheckbox.checked = false
            deleteLocalLinkCheckbox.checked = false
        }

        background: Rectangle {
            radius: 22
            color: "#ffffff"
            border.color: "#fecaca"
            border.width: 1
        }

        contentItem: ColumnLayout {
            spacing: 0

            Rectangle {
                Layout.fillWidth: true
                height: 84
                radius: 22
                color: "#fef2f2"
                border.color: "#fecaca"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 14

                    Rectangle {
                        width: 44
                        height: 44
                        radius: 16
                        color: "#fee2e2"
                        Text { anchors.centerIn: parent; text: "×"; color: "#b91c1c"; font.pixelSize: 26; font.weight: Font.Bold }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 3
                        Text { text: "删除同步项目"; color: "#991b1b"; font.pixelSize: 22; font.weight: Font.Bold }
                        Text { text: "删除后软件将不再管理该同步关系。请确认是否同时清理云端目标或本地链接。"; color: "#b91c1c"; font.pixelSize: 13; wrapMode: Text.WordWrap }
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
                    implicitHeight: deleteInfo.implicitHeight + 28

                    Text {
                        id: deleteInfo
                        anchors.fill: parent
                        anchors.margins: 14
                        text: "即将删除项目：" + safeString(selectedProject.name, selectedProject.id) + "\n\n如果本地路径当前是链接，原软件可能无法继续正常访问该路径。"
                        color: "#334155"
                        font.pixelSize: 14
                        wrapMode: Text.WordWrap
                    }
                }

                CheckBox {
                    id: deleteCloudCheckbox
                    text: "同时删除 Cloud 中的目标文件夹"
                    checked: false
                    onCheckedChanged: deleteConfirm.deleteCloud = checked
                }

                CheckBox {
                    id: deleteLocalLinkCheckbox
                    text: "同时删除本地链接"
                    checked: false
                    onCheckedChanged: deleteConfirm.deleteLocalLink = checked
                }

                Rectangle {
                    Layout.fillWidth: true
                    radius: 14
                    color: "#fff7ed"
                    border.color: "#fed7aa"
                    implicitHeight: 54
                    Text {
                        anchors.fill: parent
                        anchors.margins: 12
                        text: "删除本地链接只删除 junction 入口，不删除 Cloud 工作目录中的真实数据，也不会删除本地父目录。"
                        color: "#9a3412"
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Item { Layout.fillWidth: true }

                    AnimatedButton { text: "取消"; subtle: true; onClicked: deleteConfirm.close() }

                    AnimatedButton {
                        text: "确认删除"
                        baseColor: "#dc2626"
                        hoverColor: "#fee2e2"
                        pressedColor: "#fecaca"
                        onClicked: {
                            if (deleteConfirm.deleteCloud) {
                                var lines = []
                                lines.push("即将删除 Cloud 中的目标文件夹：")
                                lines.push("")
                                lines.push(selectedCloudAbsolutePath())
                                if (deleteConfirm.deleteLocalLink) {
                                    lines.push("")
                                    lines.push("同时将删除本地链接入口：")
                                    lines.push("")
                                    lines.push(selectedLocalPath())
                                    lines.push("")
                                    lines.push("删除本地链接只会删除 junction 入口，不会删除 Cloud 工作目录中的真实数据。")
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
        color: root.pageBg
    }

    ColumnLayout {
        enabled: !controllerBusy
        anchors.fill: parent
        anchors.margins: 22
        spacing: 16

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 132
            radius: 26
            color: root.cardBg
            border.color: root.borderColor
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 18

                Rectangle {
                    width: 58
                    height: 58
                    radius: 18
                    color: "#eaf2ff"
                    border.color: "#dbeafe"
                    Text { anchors.centerIn: parent; text: "↗"; color: root.brand; font.pixelSize: 32; font.weight: Font.Bold }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Text {
                            text: "Cloud Redirect Manager"
                            color: root.textMain
                            font.pixelSize: 30
                            font.weight: Font.Bold
                        }

                        Rectangle {
                            radius: 999
                            color: hasRootValue ? "#e8f7ee" : "#fff7ed"
                            border.color: hasRootValue ? "#bbf7d0" : "#fed7aa"
                            implicitHeight: 28
                            implicitWidth: statusText.implicitWidth + 22
                            Text {
                                id: statusText
                                anchors.centerIn: parent
                                text: hasRootValue ? "根目录已设置" : "未设置根目录"
                                color: hasRootValue ? "#15803d" : "#b45309"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                            }
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "轻量级 Cloud 目录重定向工具"
                        color: root.textSecond
                        font.pixelSize: 14
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "在数据原路径创建 junction 链接，真实数据保存到 Cloud 工作目录"
                        color: "#94a3b8"
                        font.pixelSize: 13
                        elide: Text.ElideRight
                    }
                }

                RowLayout {
                    spacing: 10
                    Layout.alignment: Qt.AlignTop

                    AnimatedButton { text: "＋ 新建"; enabled: controllerReady; onClicked: openCreateDialog() }
                    AnimatedButton { text: "刷新"; subtle: true; enabled: controllerReady; onClicked: controller.refreshProjects() }
                    AnimatedButton { text: "设置"; subtle: true; enabled: controllerReady; onClicked: settingsDialog.open() }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 26
            color: root.cardBg
            border.color: root.borderColor
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 14

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 3
                        Text { text: "同步项目"; color: root.textMain; font.pixelSize: 18; font.weight: Font.Bold }
                        Text { text: "双击项目可编辑；右键项目可打开管理菜单。"; color: root.textSecond; font.pixelSize: 12 }
                    }

                    StatusBadge {
                        statusText: selectedProjectId ? safeString(selectedProject.statusText, "未知状态") : "未选择项目"
                        statusColor: selectedProjectId ? safeString(selectedProject.statusColor, "#64748b") : "#64748b"
                        statusIcon: selectedProjectId ? safeString(selectedProject.statusIcon, "○") : "○"
                    }
                }

                Loader {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    active: true
                    sourceComponent: projectListData.length > 0 ? tableComponent : emptyComponent
                }
            }

            Component {
                id: emptyComponent
                EmptyState {
                    title: hasRootValue ? "还没有同步项目" : "请先设置 Cloud 工作目录"
                    description: hasRootValue
                        ? "点击右上角“新建”，选择本地源文件夹和 Cloud 路径。"
                        : "打开右上角“设置”，选择一个 Cloud 工作目录后再继续。"
                }
            }

            Component {
                id: tableComponent
                ProjectTable {
                    modelData: projectListData
                    busy: controllerBusy
                    selectedId: selectedProjectId
                    onProjectSelected: function(projectId) { selectedProjectId = projectId }
                    onProjectDoubleClicked: function(projectId) {
                        selectedProjectId = projectId
                        openEditDialog()
                    }
                    onContextAction: function(action, projectId) {
                        handleProjectContextAction(action, projectId)
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 112
            radius: 22
            color: root.cardBg
            border.color: root.borderColor
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 14

                Rectangle {
                    width: 52
                    height: 52
                    radius: 18
                    color: selectedProjectId ? "#eef5ff" : "#f1f5f9"
                    Text { anchors.centerIn: parent; text: selectedProjectId ? "✓" : "·"; color: selectedProjectId ? root.brand : "#94a3b8"; font.pixelSize: 26; font.weight: Font.Bold }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 6

                    Text {
                        Layout.fillWidth: true
                        text: selectedProjectId
                            ? (safeString(selectedProject.name, "未命名项目") + "  ·  " + safeString(selectedProject.id, ""))
                            : "请选择一个同步项目"
                        color: root.textMain
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.fillWidth: true
                        text: selectedProjectId
                            ? safeString(selectedProject.message, "当前状态正常。")
                            : "选择项目后，可在这里查看路径、状态和操作提示。"
                        color: root.textSecond
                        font.pixelSize: 13
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.fillWidth: true
                        text: selectedProjectId
                            ? ("本地：" + safeString(selectedProject.localPath, "未配置") + "    云端：" + safeString(selectedProject.cloudRelativePath, ""))
                            : ""
                        color: "#94a3b8"
                        font.pixelSize: 12
                        elide: Text.ElideMiddle
                    }
                }

                ColumnLayout {
                    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                    spacing: 10

                    AnimatedButton {
                        text: "恢复到本地并取消同步"
                        baseColor: "#0f766e"
                        hoverColor: "#ccfbf1"
                        pressedColor: "#99f6e4"
                        enabled: controllerReady && !!selectedProjectId && !controllerBusy
                        onClicked: controller.restoreProjectToLocal(selectedProjectId)
                    }

                    Text {
                        text: "Developed by @ryancyx/github.com"
                        color: "#94a3b8"
                        font.pixelSize: 12
                        horizontalAlignment: Text.AlignRight
                        Layout.alignment: Qt.AlignRight
                    }
                }
            }
        }
    }

    Rectangle {
        visible: controllerBusy
        anchors.fill: parent
        z: 1000
        color: "#7a0f172a"

        MouseArea {
            anchors.fill: parent
        }

        Rectangle {
            width: Math.min(460, parent.width - 48)
            radius: 22
            color: "#ffffff"
            border.color: "#dbe4ef"
            border.width: 1
            anchors.centerIn: parent
            implicitHeight: overlayColumn.implicitHeight + 40

            ColumnLayout {
                id: overlayColumn
                anchors.fill: parent
                anchors.margins: 20
                spacing: 14

                Text {
                    text: "正在处理"
                    color: root.textMain
                    font.pixelSize: 22
                    font.weight: Font.Bold
                }

                Text {
                    Layout.fillWidth: true
                    text: controllerBusyText
                    color: root.textSecond
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                }

                BusyIndicator {
                    Layout.alignment: Qt.AlignHCenter
                    running: controllerBusy
                    visible: controllerBusy
                    width: 56
                    height: 56
                }
            }
        }
    }

    Rectangle {
        id: toast
        visible: opacity > 0
        opacity: toastVisible ? 1 : 0
        width: Math.min(parent.width - 80, toastLabel.implicitWidth + 42)
        height: 44
        radius: 14
        color: "#0f172a"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 28


        Text {
            id: toastLabel
            anchors.centerIn: parent
            text: toastText
            color: "#ffffff"
            font.pixelSize: 13
            font.weight: Font.DemiBold
            elide: Text.ElideRight
        }
    }

    Component.onCompleted: {
        if (controllerReady && !hasRootValue)
            settingsDialog.open()
    }
}
