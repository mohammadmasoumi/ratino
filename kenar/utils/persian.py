EN_FA_NUMBER_MAPPING = {
    '0': '۰',
    '1': '۱',
    '2': '۲',
    '3': '۳',
    '4': '۴',
    '5': '۵',
    '6': '۶',
    '7': '۷',
    '8': '۸',
    '9': '۹',
    '.': '.',
}
AR_FA_NUMBER_MAPPING = {
    '٠': '۰',
    '١': '۱',
    '٢': '۲',
    '٣': '۳',
    '٤': '۴',
    '٥': '۵',
    '٦': '۶',
    '٧': '۷',
    '٨': '۸',
    '٩': '۹',
}
FA_EN_NUMBER_MAPPING = {
    '۰': '0',
    '۱': '1',
    '۲': '2',
    '۳': '3',
    '۴': '4',
    '۵': '5',
    '۶': '6',
    '۷': '7',
    '۸': '8',
    '۹': '9',
    '.': '.',
}
AR_EN_NUMBER_MAPPING = {
    '٠': '0',
    '١': '1',
    '٢': '2',
    '٣': '3',
    '٤': '4',
    '٥': '5',
    '٦': '6',
    '٧': '7',
    '٨': '8',
    '٩': '9',
    '.': '.',
}
AR_FA_CHAR_MAPPING = {
    'ك': 'ک',
    'دِ': 'د',
    'بِ': 'ب',
    'زِ': 'ز',
    'ذِ': 'ذ',
    'شِ': 'ش',
    'سِ': 'س',
    'ى': 'ی',
    'ي': 'ی'
}


def translate_fa_ar_numbers_to_en(s: str):
    res = []
    for ch in s:
        res_ch = ch
        res_ch = FA_EN_NUMBER_MAPPING.get(res_ch, res_ch)
        res_ch = AR_EN_NUMBER_MAPPING.get(res_ch, res_ch)
        res.append(res_ch)
    return ''.join(res)


def translate_en_to_fa_numbers(s: str):
    res = []
    for ch in s:
        res_ch = ch
        res_ch = EN_FA_NUMBER_MAPPING.get(res_ch, res_ch)
        res.append(res_ch)
    return ''.join(res)
