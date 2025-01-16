from typing import Dict
from jamo import h2j, j2hcj

# 한글 자모와 영문 키보드 매핑
KOREAN_TO_ENGLISH_MAPPING: Dict[str, str] = {
    # 자음
    'ㄱ': 'r', 'ㄲ': 'R', 'ㄳ': 'rt', 'ㄴ': 's', 'ㄵ': 'sw',
    'ㄶ': 'sg', 'ㄷ': 'e', 'ㄸ': 'E', 'ㄹ': 'f', 'ㄺ': 'fr',
    'ㄻ': 'fa', 'ㄼ': 'fq', 'ㄽ': 'ft', 'ㄾ': 'fx', 'ㄿ': 'fv',
    'ㅀ': 'fg', 'ㅁ': 'a', 'ㅂ': 'q', 'ㅄ': 'qt', 'ㅃ': 'Q',
    'ㅅ': 't', 'ㅆ': 'T', 'ㅇ': 'd', 'ㅈ': 'w', 'ㅉ': 'W',
    'ㅊ': 'c', 'ㅋ': 'z', 'ㅌ': 'x', 'ㅍ': 'v', 'ㅎ': 'g',
    # 모음
    'ㅏ': 'k', 'ㅐ': 'o', 'ㅑ': 'i', 'ㅒ': 'O', 'ㅓ': 'j',
    'ㅔ': 'p', 'ㅕ': 'u', 'ㅖ': 'P', 'ㅗ': 'h', 'ㅘ': 'hk',
    'ㅙ': 'ho', 'ㅚ': 'hl', 'ㅛ': 'y', 'ㅜ': 'n', 'ㅝ': 'nj',
    'ㅞ': 'np', 'ㅟ': 'nl', 'ㅠ': 'b', 'ㅡ': 'm', 'ㅢ': 'ml',
    'ㅣ': 'l',
}

def k2e_conversion(input_text: str) -> str:
    """
    한글 문자열을 영문 키보드 입력으로 변환합니다.

    Args:
        input_text (str): 변환할 한글 문자열

    Returns:
        str: 영문 키보드 입력으로 변환된 문자열

    Examples:
        >>> k2e_conversion("안녕")
        "dkssud"
    """
    if not input_text:
        return ""
    
    try:
        # 한글을 자모 단위로 분리
        decomposed_text = j2hcj(h2j(input_text))
        
        # 각 자모를 영문 키보드 입력으로 변환
        output = ''
        for syllable in decomposed_text:
            output += KOREAN_TO_ENGLISH_MAPPING.get(syllable, syllable)
        
        return output
    
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return input_text