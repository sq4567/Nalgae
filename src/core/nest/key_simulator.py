"""키 입력 시뮬레이션을 담당하는 모듈입니다."""

import win32api
import win32con
from typing import Dict, Set

# 알파벳 키 (A-Z)
ALPHABET_KEYS = {chr(c): ord(c.upper()) for c in range(ord('a'), ord('z') + 1)}

# 숫자 키 (0-9)
NUMBER_KEYS = {str(n): ord(str(n)) for n in range(10)}

# 수정자 키
MODIFIER_KEYS = {
    'shift': win32con.VK_SHIFT,
    'lshift': win32con.VK_LSHIFT,
    'rshift': win32con.VK_RSHIFT,
    'ctrl': win32con.VK_CONTROL,
    'lctrl': win32con.VK_LCONTROL,
    'rctrl': win32con.VK_RCONTROL,
    'alt': win32con.VK_MENU,
    'lalt': win32con.VK_LMENU,
    'ralt': win32con.VK_RMENU,
    'win': win32con.VK_LWIN,
    'rwin': win32con.VK_RWIN,
    'apps': win32con.VK_APPS,  # 메뉴 키
}

# IME 관련 키
IME_KEYS = {
    'hangul': win32con.VK_HANGUL,
    'hanja': win32con.VK_HANJA,
    'kana': win32con.VK_KANA,
    'kanji': win32con.VK_KANJI,  # 일본어 한자
    'ime_on': win32con.VK_IME_ON,
    'ime_off': win32con.VK_IME_OFF,
    'ime_junja': win32con.VK_JUNJA,  # 한자 변환
    'ime_final': win32con.VK_FINAL,  # IME 최종
    'ime_convert': win32con.VK_CONVERT,  # IME 변환
    'ime_nonconvert': win32con.VK_NONCONVERT,  # IME 무변환
    'ime_accept': win32con.VK_ACCEPT,  # IME 확정
    'ime_mode_change_request': win32con.VK_MODECHANGE,  # IME 모드 변경
}

# 잠금 키
LOCK_KEYS = {
    'caps_lock': win32con.VK_CAPITAL,
    'num_lock': win32con.VK_NUMLOCK,
    'scroll_lock': win32con.VK_SCROLL,
}

# 특수문자 키
SYMBOL_KEYS = {
    '`': win32con.VK_OEM_3,
    '-': win32con.VK_OEM_MINUS,
    '=': win32con.VK_OEM_PLUS,
    '[': win32con.VK_OEM_4,
    ']': win32con.VK_OEM_6,
    '\\': win32con.VK_OEM_5,
    ';': win32con.VK_OEM_1,
    "'": win32con.VK_OEM_7,
    ',': win32con.VK_OEM_COMMA,
    '.': win32con.VK_OEM_PERIOD,
    '/': win32con.VK_OEM_2,
}

# 추가 OEM 키
OEM_KEYS = {
    'oem_ax': win32con.VK_OEM_AX,  # AX 키 (일본어 키보드)
    'oem_102': win32con.VK_OEM_102,  # RT 102 키보드의 추가 키
}

# 기능 키 (F1-F24)
FUNCTION_KEYS = {f'f{i}': getattr(win32con, f'VK_F{i}') for i in range(1, 25)}

# 탐색 키
NAVIGATION_KEYS = {
    'insert': win32con.VK_INSERT,
    'delete': win32con.VK_DELETE,
    'home': win32con.VK_HOME,
    'end': win32con.VK_END,
    'pageup': win32con.VK_PRIOR,
    'pagedown': win32con.VK_NEXT,
}

# 화살표 키
ARROW_KEYS = {
    'left': win32con.VK_LEFT,
    'up': win32con.VK_UP,
    'right': win32con.VK_RIGHT,
    'down': win32con.VK_DOWN,
}

# 숫자 패드 키
NUMPAD_KEYS = {
    **{f'num{i}': getattr(win32con, f'VK_NUMPAD{i}') for i in range(10)},
    'num_decimal': win32con.VK_DECIMAL,
    'num_divide': win32con.VK_DIVIDE,
    'num_multiply': win32con.VK_MULTIPLY,
    'num_subtract': win32con.VK_SUBTRACT,
    'num_add': win32con.VK_ADD,
    'num_enter': win32con.VK_RETURN,
    'num_comma': win32con.VK_SEPARATOR,  # 숫자 패드 쉼표
}

# 미디어 키
MEDIA_KEYS = {
    'volume_mute': win32con.VK_VOLUME_MUTE,
    'volume_down': win32con.VK_VOLUME_DOWN,
    'volume_up': win32con.VK_VOLUME_UP,
    'media_next': win32con.VK_MEDIA_NEXT_TRACK,
    'media_prev': win32con.VK_MEDIA_PREV_TRACK,
    'media_stop': win32con.VK_MEDIA_STOP,
    'media_play_pause': win32con.VK_MEDIA_PLAY_PAUSE,
}

# 브라우저 키
BROWSER_KEYS = {
    'browser_back': win32con.VK_BROWSER_BACK,
    'browser_forward': win32con.VK_BROWSER_FORWARD,
    'browser_refresh': win32con.VK_BROWSER_REFRESH,
    'browser_stop': win32con.VK_BROWSER_STOP,
    'browser_search': win32con.VK_BROWSER_SEARCH,
    'browser_favorites': win32con.VK_BROWSER_FAVORITES,
    'browser_home': win32con.VK_BROWSER_HOME,
}

# 기타 키
MISC_KEYS = {
    'escape': win32con.VK_ESCAPE,
    'tab': win32con.VK_TAB,
    'space': win32con.VK_SPACE,
    'enter': win32con.VK_RETURN,
    'backspace': win32con.VK_BACK,
    'print_screen': win32con.VK_SNAPSHOT,
    'pause': win32con.VK_PAUSE,
    'break': win32con.VK_CANCEL,  # Ctrl+Break
    'sleep': win32con.VK_SLEEP,
    'help': win32con.VK_HELP,
    'select': win32con.VK_SELECT,
    'execute': win32con.VK_EXECUTE,
    'clear': win32con.VK_CLEAR,
}

# 앱 런처 키
LAUNCHER_KEYS = {
    'launch_mail': win32con.VK_LAUNCH_MAIL,
    'launch_media': win32con.VK_LAUNCH_MEDIA_SELECT,
    'launch_app1': win32con.VK_LAUNCH_APP1,
    'launch_app2': win32con.VK_LAUNCH_APP2,
}

# 파워 관리 키
POWER_KEYS = {
    'power': win32con.VK_POWER,
    'sleep': win32con.VK_SLEEP,
}

# 추가 특수 키
SPECIAL_KEYS = {
    'processkey': win32con.VK_PROCESSKEY,  # IME 프로세스 키
    'packet': win32con.VK_PACKET,  # 유니코드 문자용
    'attn': win32con.VK_ATTN,  # Attention 키
    'crsel': win32con.VK_CRSEL,  # Cursor Select 키
    'exsel': win32con.VK_EXSEL,  # Extend Selection 키
    'ereof': win32con.VK_EREOF,  # Erase EOF 키
    'play': win32con.VK_PLAY,  # Play 키
    'zoom': win32con.VK_ZOOM,  # Zoom 키
    'noname': win32con.VK_NONAME,  # 예약된 키
    'pa1': win32con.VK_PA1,  # PA1 키
}

def get_all_key_mappings() -> Dict[str, int]:
    """모든 키 매핑을 반환합니다."""
    return {
        **ALPHABET_KEYS,  # 알파벳 키 (A-Z)
        **NUMBER_KEYS,    # 숫자 키 (0-9)
        **MODIFIER_KEYS,  # 수정자 키
        **IME_KEYS,       # IME 관련 키
        **LOCK_KEYS,      # 잠금 키
        **SYMBOL_KEYS,    # 특수문자 키
        **OEM_KEYS,       # 추가 OEM 키
        **FUNCTION_KEYS,  # 기능 키 (F1-F24)
        **NAVIGATION_KEYS,# 탐색 키
        **ARROW_KEYS,     # 화살표 키
        **NUMPAD_KEYS,    # 숫자 패드 키
        **MEDIA_KEYS,     # 미디어 키
        **BROWSER_KEYS,   # 브라우저 키
        **MISC_KEYS,      # 기타 키
        **LAUNCHER_KEYS,  # 앱 런처 키
        **POWER_KEYS,     # 파워 관리 키
        **SPECIAL_KEYS,   # 추가 특수 키
    }

class KeySimulator:
    """키 입력을 시뮬레이션하는 클래스입니다."""
    
    # 키 코드와 Windows Virtual Key Code 매핑
    VK_MAP = get_all_key_mappings()
    
    def __init__(self):
        """KeySimulator 클래스를 초기화합니다."""
        self._active_keys: Set[str] = set()  # 현재 눌린 키들
        
    def press_key(self, key_code: str) -> None:
        """키를 누릅니다.
        
        Args:
            key_code (str): 누를 키의 코드
        """
        if key_code not in self.VK_MAP:
            return
            
        vk = self.VK_MAP[key_code]
        win32api.keybd_event(vk, 0, 0, 0)
        self._active_keys.add(key_code)
        
    def release_key(self, key_code: str) -> None:
        """키를 뗍니다.
        
        Args:
            key_code (str): 뗄 키의 코드
        """
        if key_code not in self.VK_MAP:
            return
            
        vk = self.VK_MAP[key_code]
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        self._active_keys.discard(key_code)
        
    def press_keys(self, key_codes: Set[str]) -> None:
        """여러 키를 동시에 누릅니다.
        
        Args:
            key_codes (Set[str]): 누를 키들의 코드
        """
        for key_code in key_codes:
            self.press_key(key_code)
            
    def release_keys(self, key_codes: Set[str]) -> None:
        """여러 키를 동시에 뗍니다.
        
        Args:
            key_codes (Set[str]): 뗄 키들의 코드
        """
        for key_code in key_codes:
            self.release_key(key_code)
            
    def release_all_keys(self) -> None:
        """현재 눌린 모든 키를 뗍니다."""
        keys_to_release = self._active_keys.copy()
        for key_code in keys_to_release:
            self.release_key(key_code)
            
    @property
    def active_keys(self) -> Set[str]:
        """현재 눌린 키들의 집합을 반환합니다."""
        return self._active_keys.copy()