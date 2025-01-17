# 핵심 기능 모듈

이 디렉토리는 날개 프로그램의 핵심 기능 모듈들을 포함합니다.

## 둥지 (Nest)
기본 화상 키보드 레이아웃과 키 입력을 처리하는 핵심 모듈입니다.

### 주요 기능
- 기본 키보드 레이아웃 (104 Key, 87 Key 등) 제공
- 마우스 클릭으로 키 입력 시뮬레이션
- IME 상태 감지 및 처리
- 키 입력 시각/청각 피드백

### 구현 상태
- [x] 기본 프로그램 구조 설정
- [ ] 키보드 레이아웃 UI 구현
- [ ] 키 입력 처리 로직 구현
- [ ] IME 상태 처리 구현
- [ ] 시각/청각 피드백 구현

### 사용 예시
```python
from core.nest import NestKeyboard

# 키보드 인스턴스 생성
keyboard = NestKeyboard()

# 레이아웃 설정
keyboard.set_layout("104key")

# 키보드 표시
keyboard.show()
```

## 날개 꾸미기 (Feathering)
[구현 예정]

## 길잡이 (Guide)
[구현 예정]

## 산들바람 (Breeze)
[구현 예정]

## 부리 (Beak)
[구현 예정]

## 워프 (Warp)
[구현 예정]

## 변신 (Transformation)
[구현 예정] 