# 날개 (Nalgae)

손 기능 장애인을 위한 맞춤형 화상 키보드 프로그램

## 프로젝트 소개
"날개"는 손 기능이 불편한 사람들도 컴퓨터를 사용하는 동안에는 자유롭게 날아오르기를 바라는 마음을 담은 프로그램입니다. 기존의 화상 키보드와 달리, 사용자의 작업 환경과 요구사항에 맞는 다양한 커스터마이징 옵션과 고급 기능을 제공합니다.

## 주요 기능
1. **둥지(Nest)**: 기본 화상 키보드 레이아웃 및 키 입력 처리
2. **날개 꾸미기(Feathering)**: 키보드 레이아웃 및 테마 개인화
3. **길잡이(Guide)**: AI 기반 텍스트 추천 및 자동완성
4. **산들바람(Breeze)**: 자주 사용하는 구문을 단축 문자열로 자동입력
5. **부리(Beak)**: 다단계 복합 작업을 단일 클릭으로 처리하는 커스텀 키
6. **워프(Warp)**: 다중 좌표 저장 및 마우스 커서 빠른 이동
7. **변신(Transformation)**: 활성화된 프로그램에 따라 키보드 레이아웃 자동 전환

## 시스템 요구사항
- Python 3.11.9 이상
- Windows 10 이상

## 시작하기

### 설치 방법
1. 저장소 클론
```bash
git clone https://github.com/yourusername/nalgae.git
cd nalgae
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
venv\\Scripts\\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 실행 방법
- `run.bat` 파일을 더블클릭
또는
```bash
python src/main.py
```

## 업데이트 내역

### v0.1.0 (2025-01-16)
- 프로젝트 기본 구조 설정
  - Python 가상환경 및 의존성 설정
  - 프로젝트 디렉토리 구조 생성
  - 로깅 및 설정 관리 시스템 구현
  - PySide6 기반 메인 윈도우 구현
  - 개발 가이드 및 문서화 시작

### v0.2.0 (2025-01-17)
- 둥지(Nest) 모듈 핵심 기능 구현
  - 키보드 핵심 클래스 구현 (Key, NestKeyboard)
  - 키 상태 관리 시스템 구현
  - 마우스 이벤트 처리 및 키 상태별 색상 관리
  - 키 입력 시뮬레이션 로직 분리

- 한글 입력 시스템 구현
  - IME 상태 실시간 감지 및 관리
  - 한글 자음/모음 레이블 매핑
  - Caps Lock과 한/영 키 연동
  - IME 상태 자동 동기화

- 기능 키 시스템 구현
  - 다중 기능 키 조합 처리
  - 기능 키 상태 추적 및 관리
  - 기능 키 길게 누르기 지원

- 키보드 피드백 시스템 구현
  - 기계식 키보드 스위치 사운드 지원
  - 키보드 행별 사운드 매핑
  - 키 색상 애니메이션 시스템

- 안정성 강화
  - 키 입력 실패 시 자동 재시도 메커니즘 구현
  - IME 상태 동기화 실패 대응 시스템 추가
  - 키보드 상태 health check 시스템 도입
  - 성능 메트릭 수집 및 모니터링 기능 구현

- 메모리 관리 최적화
  - 메모리 사용량 실시간 모니터링
  - LRU 기반 캐시 시스템 구현
  - 주기적 리소스 정리 메커니즘 도입
  - 메모리 상태 보고서 생성 기능

### v0.2.5 (개발 중)
- 둥지(Nest) UI 구현
  - 키보드 레이아웃 디자인
  - ...

## 기여하기
현재 이 프로젝트는 개발 초기 단계입니다. 기여 가이드는 추후 업데이트될 예정입니다.

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## Credits
- Keyboard sound samples from [kbsim](https://github.com/tplai/kbsim) (MIT License) 