import win32api
import win32con
from typing import Dict

# 특수 키 매핑
SPECIAL_KEYS: Dict[str, int] = {
    'Space': win32con.VK_SPACE,
    'Enter': win32con.VK_RETURN,
    'Backspace': win32con.VK_BACK,
    'Tab': win32con.VK_TAB,
    'Shift': win32con.VK_SHIFT,
    'Ctrl': win32con.VK_CONTROL,
    'Alt': win32con.VK_MENU,
    'Win': win32con.VK_LWIN,
    'ESC': win32con.VK_ESCAPE,
    'Caps': win32con.VK_CAPITAL,
    'Left': win32con.VK_LEFT,
    'Right': win32con.VK_RIGHT,
    'Up': win32con.VK_UP,
    'Down': win32con.VK_DOWN,
    '[': 0xDB,  # 왼쪽 대괄호
    ']': 0xDD,  # 오른쪽 대괄호
    '\\': 0xDC, # 백슬래시
    'Del': win32con.VK_DELETE,
    'Insert': win32con.VK_INSERT,
    'Home': win32con.VK_HOME,
    'End': win32con.VK_END,
    'PageUp': win32con.VK_PRIOR,
    'PageDn': win32con.VK_NEXT,
}

def send_key(key: str):
    """키 입력을 시뮬레이션합니다."""
    if key in SPECIAL_KEYS:
        vk_code = SPECIAL_KEYS[key]
    else:
        # 일반 문자키는 ord() 함수로 가상 키코드 변환
        vk_code = ord(key.upper())
    
    # 키 누름
    win32api.keybd_event(vk_code, 0, 0, 0)
    # 키 뗌
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)