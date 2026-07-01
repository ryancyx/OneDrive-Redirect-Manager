import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property var modelData: []
    property string selectedId: ""
    signal projectSelected(string projectId)
    signal projectDoubleClicked(string projectId)

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            height: 42
            radius: 14
            color: "#eef2ff"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 12

                Repeater {
                    model: [
                        { label: "项目 ID", width: 150 },
                        { label: "名称", width: 180 },
                        { label: "本地源文件夹路径", width: 320 },
                        { label: "OneDrive 中的路径", width: 240 },
                        { label: "运行状态", width: 180 }
                    ]

                    delegate: Text {
                        required property var modelData
                        Layout.preferredWidth: modelData.width
                        text: modelData.label
                        color: "#334155"
                        font.bold: true
                        font.pixelSize: 13
                    }
                }
            }
        }

        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 8
            model: root.modelData

            delegate: Rectangle {
                required property var modelData
                width: ListView.view.width
                height: 58
                radius: 16
                color: root.selectedId === modelData.id ? "#eff6ff" : "#ffffff"
                border.color: root.selectedId === modelData.id ? "#93c5fd" : "#e5e7eb"
                border.width: 1

                Behavior on color { ColorAnimation { duration: 140 } }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: root.projectSelected(modelData.id)
                    onDoubleClicked: root.projectDoubleClicked(modelData.id)
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 12

                    Text { Layout.preferredWidth: 150; text: modelData.id || ""; color: "#111827"; elide: Text.ElideRight }
                    Text { Layout.preferredWidth: 180; text: modelData.name || ""; color: "#111827"; elide: Text.ElideRight }
                    Text { Layout.preferredWidth: 320; text: modelData.localPath || ""; color: "#374151"; elide: Text.ElideMiddle }
                    Text { Layout.preferredWidth: 240; text: modelData.cloudRelativePath || ""; color: "#374151"; elide: Text.ElideMiddle }
                    StatusBadge {
                        Layout.preferredWidth: 180
                        statusText: modelData.statusText || "未知状态"
                        statusColor: modelData.statusColor || "#6b7280"
                        statusIcon: modelData.statusIcon || "○"
                    }
                }
            }

            add: Transition {
                NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 180 }
                NumberAnimation { property: "y"; from: 10; to: 0; duration: 180 }
            }

            remove: Transition {
                NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 140 }
            }
        }
    }
}
