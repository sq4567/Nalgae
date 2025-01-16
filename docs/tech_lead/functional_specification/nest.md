## 기능 명세서: 둥지 (Nest)

### 1. 기능 정의
- **목적**: 손 기능 장애인을 위한 기본 화상 키보드 레이아웃 제공
- **역할**: 다양한 키보드 레이아웃 지원 및 테마별 UI 설정으로 사용자의 접근성과 효율성 극대화
- **프로그램 내 중요성**: 사용자가 첫 번째로 접하게 되는 핵심 인터페이스로, 전체 작업 흐름의 중심을 형성하며 다른 기능들과의 연계성을 제공.

### 2. 입력/출력 정의
- **입력**:
  - 사용자 선택:
    - **키보드 레이아웃**: 104 Key, 87 Key, 사용자 정의 레이아웃
    - **테마**: 베이직, 고대비, 파스텔
  - 사용자 입력:
    - 키 클릭 (마우스)
    - 키 고정 (Shift, Ctrl, Alt 등)
- **출력**:
  - 시각적 피드백:
    - 키 상태 변경 (기본, 호버, 클릭, 고정, 비활성)
    - 테마 적용된 레이아웃 표시
  - 청각적 피드백:
    - 클릭 사운드 (짧고 부드러운 톤)
    - 특수키 고정/해제 사운드

### 3. 예외 처리 정의
1. **입력 오류**:
   - 입력 데이터(키보드 레이아웃, 테마)가 손상되었을 경우 기본 설정(104 Key, 베이직 테마)으로 복원.
2. **UI 렌더링 실패**:
   - 렌더링 실패 시, 기본 배경과 텍스트를 활용한 단순 레이아웃 표시.
3. **파일 손실**:
   - 테마 파일이나 레이아웃 파일이 없는 경우, 해당 항목에 대해 경고 메시지 표시 및 기본값 사용.

### 4. 디렉터리 구조
```plaintext
Nalgae/
├── assets/
│   ├── fonts/
│   ├── icons/
│   ├── sounds/
│   └── themes/
│       ├── default.json
│       ├── high_contrast.json
│       └── pastel.json
├── docs/
│   ├── PM/
│   ├── tech_lead/
│   ├── UXUI/
│   ├── CHANGELOG.md
│   └── README.md
├── manual_tests/
│   ├── accessibility/
│   ├── beak/
│   ├── feathering/
│   ├── guide/
│   ├── nest/
│   ├── performance/
│   └── utils/
├── src/
│   ├── accessibility/
│   │   ├── keyboard_hooks.py
│   │   ├── mouse_hooks.py
│   │   └── windows_api.py
│   ├── core/
│   │   ├── beak.py
│   │   ├── feathering.py
│   │   ├── guide.py
│   │   ├── natural_typing.py
│   │   ├── nest.py
│   │   ├── transformation.py
│   │   └── warp.py
│   ├── data/
│   │   ├── presets.json
│   │   └── user_data.json
│   ├── security/
│   │   ├── encryption.py
│   │   └── gdpr.py
│   ├── settings/
│   │   ├── layout_manager.py
│   │   ├── profile_manager.py
│   │   └── theme_manager.py
│   ├── ui/
│   │   ├── main_window.qml
│   │   ├── nest.qml
│   │   └── settings.qml
│   ├── utils/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── performance.py
│   └── main.py
├── venv/
├── .gitignore
├── LICENSE
├── requirements.txt
└── setup.py
```

### 5. 구현 가이드 (의사코드)
#### Python(PySide6) 코드 예제
```python
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "Keyboard"
QML_IMPORT_VERSION = "1.0"

@QmlElement
class KeyboardController(QObject):
    key_pressed = Signal(str)  # 키 입력 시그널
    theme_changed = Signal(str)  # 테마 변경 시그널

    def __init__(self):
        super().__init__()
        self.current_layout = "104 Key"
        self.current_theme = "basic"

    @Slot(str)
    def set_layout(self, layout):
        self.current_layout = layout
        print(f"Keyboard layout set to: {layout}")

    @Slot(str)
    def set_theme(self, theme):
        self.current_theme = theme
        print(f"Theme set to: {theme}")
        self.theme_changed.emit(theme)

    @Slot(str)
    def press_key(self, key):
        print(f"Key pressed: {key}")
        self.key_pressed.emit(key)
```

#### QML 코드 예제
```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import Keyboard 1.0

Item {
    id: root
    width: 800
    height: 400

    KeyboardController {
        id: keyboardController
        onThemeChanged: console.log("Theme changed to:", theme)
    }

    // 테마 적용
    Rectangle {
        id: keyboardBackground
        anchors.fill: parent
        color: keyboardController.current_theme === "basic" ? "#F4F4F4" :
               keyboardController.current_theme === "contrast" ? "#000000" : "#FFF6E5"
    }

    // 키보드 레이아웃
    GridLayout {
        anchors.centerIn: parent
        rows: 5
        columns: 14

        Repeater {
            model: 70  // 키 개수
            delegate: Rectangle {
                width: 50
                height: 50
                color: "#FFFFFF"
                border.color: "#333333"
                Text {
                    anchors.centerIn: parent
                    text: "Key"
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: keyboardController.press_key(text)
                }
            }
        }
    }
}
```

### 6. 수동 테스트 방향성
#### 기본 테스트 체크리스트
- **UI 테스트 체크리스트**:
  - 각 테마(basic, contrast, pastel) 적용 시 정상 렌더링 여부 육안 확인: y/n
  - 기본/호버/클릭/고정/비활성 상태의 색상 변화 육안 확인: y/n
- **기능 테스트 체크리스트**:
  - 104 Key, 87 Key, 사용자 정의 레이아웃 간 수동 전환 테스트: y/n
  - 키 클릭 시 시각적/청각적 피드백 수동 확인: y/n
  - 각 키의 입력값이 정확히 전달되는지 수동 확인: y/n

#### 예외 상황 체크리스트
- 네트워크 연결 없을 때 동작 확인: y/n
- 메모리 부족 상황에서의 동작 확인: y/n
- 잘못된 입력값 처리 확인: y/n

### 7. 와이어프레임 기반 UX 강화
- **레이아웃 동작**:
  - `RowLayout` 및 `ColumnLayout` 조합을 사용해 키보드 배치 구현.
  - 가이드 패널은 입력 이벤트 발생 시 `SlideDown` 애니메이션으로 표시.
- **가이드 패널 상태**:
  - 추천 단어는 실시간 업데이트되며, 유저 입력 종료 시 3초 동안 유지 후 사라짐.
  - 외부 프로그램 포커스 변경 시 가이드 패널 초기화.
- **특수 키 처리**:
  - Shift, Ctrl, Alt, Win 키는 단일 클릭 시 활성화, 길게 누르면 고정 상태로 변경.

### 8. 추가 구현 방향
- **QML 애니메이션**:
  - `Behavior`를 사용해 색상 변경 및 패널 이동 애니메이션 적용.
- **접근성 강화**:
  - 고대비 테마 및 키보드 크기 조정 기능 추가.
- **확장성 고려**:
  - 사용자 정의 레이아웃 및 테마 파일 추가 가능하도록 구조 설계.