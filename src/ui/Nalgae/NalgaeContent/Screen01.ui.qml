/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick
import QtQuick.Controls
import Nalgae

Rectangle {
    id: bg
    width: Constants.width
    height: Constants.height
    color: "#484848"
    border.width: 0


    Rectangle {
        id: esc
        x: 30
        y: 30
        width: 70
        height: 70
        visible: true
        color: "#ffffff"
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
    }
    states: [
        State {
            name: "clicked"
        }
    ]
}
