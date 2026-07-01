from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem

from ..models import MappingStatus


def status_badge(status: MappingStatus) -> str:
    mapping = {
        MappingStatus.NORMAL: "✅ 正常",
        MappingStatus.LOCAL_NOT_CONFIGURED: "⚪ 本机未配置",
        MappingStatus.CONFLICT_BOTH_HAVE_DATA: "❗ 冲突",
        MappingStatus.LOCAL_HAS_DATA_CLOUD_EMPTY: "⚠️ 本机有数据",
        MappingStatus.LOCAL_EMPTY_CLOUD_HAS_DATA: "⚠️ 云端有数据",
        MappingStatus.CLOUD_MISSING: "❌ 云端缺失",
        MappingStatus.LOCAL_MISSING: "❌ 本机缺失",
        MappingStatus.WRONG_LINK_TARGET: "❌ 链接错误",
        MappingStatus.BOTH_EMPTY: "⚠️ 双方为空",
    }
    return mapping.get(status, f"⚠️ {status.display_text}")


def status_item(status: MappingStatus) -> QTableWidgetItem:
    item = QTableWidgetItem(status_badge(status))
    if status == MappingStatus.NORMAL:
        item.setForeground(QColor("#137333"))
    elif status in {MappingStatus.CONFLICT_BOTH_HAVE_DATA, MappingStatus.WRONG_LINK_TARGET}:
        item.setForeground(QColor("#b3261e"))
    else:
        item.setForeground(QColor("#8a4f00"))
    return item
