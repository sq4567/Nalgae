@echo off
:: 가상환경 활성화
call venv\Scripts\activate.bat

:: 프로그램 실행
python src/main.py

:: 실행 완료 후 창이 바로 닫히지 않도록 대기
pause 