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

## 시작하기

### 요구사항
- Python 3.11.9 이상
- Windows 10 이상

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

## 개발 진행사항

### v0.1.0: 프로젝트 초기 설정
1. **개발 환경 설정**
   - Python 가상환경 설정
   - 기본 의존성 설치 및 requirements.txt 생성
   - 프로젝트 문서화 시작 (PRD, 개발 가이드)

2. **프로젝트 기본 구조 설정**
   - 프로젝트 디렉토리 구조 생성
   - 기본 설정 파일 생성 (setup.py, .gitignore)
   - 로깅 시스템 구현 (src/utils/logger.py)
   - 설정 관리 시스템 구현 (src/utils/config.py)

3. **기본 GUI 프레임워크 설정**
   - PySide6 기반 메인 윈도우 구현
   - 투명 배경, 드래그 가능한 창 설정
   - 시스템 트레이 아이콘 및 메뉴 구현

4. **개발 편의성 개선**
   - 원클릭 실행 스크립트 추가 (run.bat)
   - 프로젝트 문서 구조화 및 개선

## 기여하기
현재 이 프로젝트는 개발 초기 단계입니다. 기여 가이드는 추후 업데이트될 예정입니다.

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## Credits
- Keyboard sound samples from [kbsim](https://github.com/tplai/kbsim) (MIT License) 