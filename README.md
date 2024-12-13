# 날개(Nalgae) - 기능성 화상키보드

> Windows 환경에서 장애인을 포함한 다양한 사용자를 위한 기능성 화상키보드 애플리케이션

<!-- 
프로젝트의 핵심 가치와 목적을 한 줄로 표현하여 방문자가 즉시 이해할 수 있도록 합니다.
-->

## 주요 기능

- Windows 기본 화상키보드와 동등한 수준의 텍스트 입력
- 한/영 상태를 "한/영" 키 레이블로 명확히 표시
- 특수키(Shift, Ctrl, Alt, Win 등) 지원
- 윈도우 포커스를 뺏지 않는 항상 위 표시 기능

<!--
GitHub 문서에 따르면 "What the project does"를 명시해야 합니다.
현재 구현된 v0.1.0 기능을 중심으로 나열했습니다.
-->

## 시작하기

### 요구사항

- Windows 10 이상
- Python 3.11.9
- PySide6
- pywin32

### 설치

1. 저장소 클론

```bash
git clone https://github.com/yourusername/nalgae.git
cd nalgae
```

2. 가상환경 생성 및 활성화

```bash
python -m venv venv_nalgae
source venv_nalgae/bin/activate  # Windows: venv_nalgae\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

<!--
"How users can get started with the project"를 제공합니다.
사용자가 프로젝트를 실행하는데 필요한 모든 단계를 명확히 설명합니다.
-->

## 사용 방법

1. 프로그램 실행
```bash
python src/main.py
```

2. 키보드 사용
- 마우스로 키를 클릭하여 텍스트 입력
- "한/영" 키로 한글/영문 전환
- 특수키(Shift, Ctrl 등)는 토글 방식으로 동작

<!--
실제 사용자가 프로그램을 어떻게 사용하는지 설명합니다.
현재 구현된 기능을 중심으로 설명했습니다.
-->

## 프로젝트 구조

```
src/
├── core/
│   └── input.py          # 키보드 입력 처리
├── ui/
│   ├── keyboard/
│   │   └── keyboard_layout.py  # 키보드 레이아웃
│   └── main_window.py    # 메인 윈도우
└── utils/
    └── win32_utils.py    # Windows API 유틸리티
```

<!--
프로젝트의 구조를 보여줌으로써 코드 탐색과 이해를 돕습니다.
-->

## 기여하기

현재 v0.1.0 버전으로, 기본적인 키보드 기능을 구현한 상태입니다. 
추가 기능 개발 및 버그 수정에 참여하실 수 있습니다.

<!--
"Who maintains and contributes to the project"를 설명합니다.
현재는 초기 버전이므로 간단히 작성했습니다.
-->

## 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

<!--
GitHub 문서에서 권장하는 대로 라이선스 정보를 포함했습니다.
-->

## 도움말

문제가 발생하거나 도움이 필요한 경우:
- GitHub Issues를 통해 버그를 보고해주세요
- 새로운 기능 제안도 환영합니다

<!--
"Where users can get help with your project"를 제공합니다.
사용자가 도움을 받을 수 있는 채널을 명시합니다.
-->

