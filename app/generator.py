import random
import string

def random_text(length):
    # 英数字の文字列を作成
    characters = string.ascii_letters + string.digits
    # 指定された長さのランダムな文字列を生成
    return ''.join(random.choice(characters) for _ in range(length))