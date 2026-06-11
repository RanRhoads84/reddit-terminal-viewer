"""Unicode-aware text utilities replacing kitchen.text.display."""
from wcwidth import wcwidth as _char_width, wcswidth as _str_width


def textual_width(text):
    w = _str_width(text)
    return len(text) if w < 0 else w


def textual_width_chop(text, chop):
    total = 0
    for i, char in enumerate(text):
        w = _char_width(char)
        if w < 0:
            w = 1
        if total + w > chop:
            return text[:i]
        total += w
    return text


def wrap(text, width=70, **_kwargs):
    result = []
    for paragraph in (text or '').split('\n'):
        words = paragraph.split()
        if not words:
            result.append('')
            continue
        lines = []
        current = []
        current_width = 0
        for word in words:
            word_w = textual_width(word)
            if current and current_width + 1 + word_w > width:
                lines.append(' '.join(current))
                current = [word]
                current_width = word_w
            else:
                current_width = current_width + 1 + word_w if current else word_w
                current.append(word)
        if current:
            lines.append(' '.join(current))
        result.extend(lines)
    return result
