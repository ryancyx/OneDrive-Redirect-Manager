import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property var modelData: []
    property string selectedId: ""
    property bool busy: false
    signal projectSelected(string projectId)
    signal projectDoubleClicked(string projectId)
    signal contextAction(string action, string projectId)

    readonly property int idWidth: 150
    readonly property int nameWidth: 190
    readonly property int localWidth: 350
    readonly property int cloudWidth: 260
    readonly property int statusWidth: 170

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        Rectangle {
            Layout.fillWidth: true
            height: 44
            radius: 14
            color: "#f6f8fb"
            border.color: "#e5ebf3"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 18
                anchors.rightMargin: 18
                spacing: 12

                Text { Layout.preferredWidth: root.idWidth; text: "项目 ID"; color: "#64748b"; font.pixelSize: 12; font.weight: Font.Bold }
                Text { Layout.preferredWidth: root.nameWidth; text: "名称"; color: "#64748b"; font.pixelSize: 12; font.weight: Font.Bold }
                Text { Layout.preferredWidth: root.localWidth; text: "本地源文件夹"; color: "#64748b"; font.pixelSize: 12; font.weight: Font.Bold }
                Text { Layout.preferredWidth: root.cloudWidth; text: "Cloud 路径"; color: "#64748b"; font.pixelSize: 12; font.weight: Font.Bold }
                Text { Layout.preferredWidth: root.statusWidth; text: "运行状态"; color: "#64748b"; font.pixelSize: 12; font.weight: Font.Bold }
            }
        }

        ListView {
            id: listView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 8
            model: root.modelData
            boundsBehavior: Flickable.StopAtBounds

            delegate: Rectangle {
                id: rowCard
                required property var modelData

                width: ListView.view.width
                height: 64
                radius: 16
                color: root.selectedId === modelData.id ? "#eef5ff" : rowMouse.containsMouse ? "#fbfdff" : "#ffffff"
                border.width: 1
                border.color: root.selectedId === modelData.id ? "#93c5fd" : rowMouse.containsMouse ? "#cfe0f5" : "#e7edf5"

                Rectangle {
                    visible: root.selectedId === modelData.id
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: 4
                    height: 30
                    radius: 999
                    color: "#2563eb"
                }

                MouseArea {
                    id: rowMouse
                    anchors.fill: parent
                    enabled: !root.busy
                    hoverEnabled: true
                    acceptedButtons: Qt.LeftButton | Qt.RightButton

                    onClicked: function(mouse) {
                        root.projectSelected(modelData.id || "")
                        if (mouse.button === Qt.RightButton)
                            contextMenu.popup(mouse.x, mouse.y)
                    }

                    onDoubleClicked: function(mouse) {
                        if (mouse.button === Qt.LeftButton)
                            root.projectDoubleClicked(modelData.id || "")
                    }
                }

                Menu {
                    id: contextMenu
                    enabled: !root.busy
                    width: 150

                    MenuItem {
                        text: "刷新"
                        enabled: !root.busy
                        onTriggered: root.contextAction("refresh", modelData.id || "")
                    }
                    MenuItem {
                        text: "编辑"
                        enabled: !root.busy
                        onTriggered: root.contextAction("edit", modelData.id || "")
                    }
                    MenuItem {
                        text: "删除"
                        enabled: !root.busy
                        onTriggered: root.contextAction("delete", modelData.id || "")
                    }
                    MenuItem {
                        text: "设置"
                        enabled: !root.busy
                        onTriggered: root.contextAction("settings", modelData.id || "")
                    }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 18
                    anchors.rightMargin: 18
                    spacing: 12

                    Text {
                        Layout.preferredWidth: root.idWidth
                        text: modelData.id || ""
                        color: "#0f172a"
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.preferredWidth: root.nameWidth
                        text: modelData.name || ""
                        color: "#111827"
                        font.pixelSize: 14
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.preferredWidth: root.localWidth
                        text: modelData.localPath || "未配置"
                        color: modelData.localPath ? "#475569" : "#94a3b8"
                        font.pixelSize: 13
                        elide: Text.ElideMiddle
                    }

                    Text {
                        Layout.preferredWidth: root.cloudWidth
                        text: modelData.cloudRelativePath || ""
                        color: "#475569"
                        font.pixelSize: 13
                        elide: Text.ElideMiddle
                    }

                    StatusBadge {
                        Layout.preferredWidth: root.statusWidth
                        statusText: modelData.statusText || "未知状态"
                        statusColor: modelData.statusColor || "#64748b"
                        statusIcon: modelData.statusIcon || "○"
                    }
                }
            }
        }
    }
}