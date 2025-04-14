import json
import re
from curl_cffi import requests


def extract_data_array(js_code: str, keyword: str="data") -> str:
    start_pattern = fr"const\s+{keyword}\s*=\s*\["
    match = re.search(start_pattern, js_code)
    if not match:
        raise ValueError(f"No `const {keyword} = [` found.")

    i = match.end() - 1  # index at the opening bracket [
    open_brackets = 1
    in_string = False
    escape = False

    while i < len(js_code) - 1:
        i += 1
        char = js_code[i]

        if char == '\\' and not escape:
            escape = True
            continue

        if char == '"' and not escape:
            in_string = not in_string

        if not in_string:
            if char == '[':
                open_brackets += 1
            elif char == ']':
                open_brackets -= 1
                if open_brackets == 0:
                    # Move forward to skip spaces and optional semicolon
                    j = i + 1
                    while j < len(js_code) and js_code[j].isspace():
                        j += 1
                    if j < len(js_code) and js_code[j] == ';':
                        j += 1
                    return js_code[match.end() - 1: j - 1]  # include the full [ ... ];
        escape = False

    raise ValueError("Unclosed array in data.")


def get_script_data(body: str, keyword: str="data") -> list:
    data_str = extract_data_array(body, keyword=keyword)
    data_str = data_str.replace('void 0', 'null')
    pattern = r'([{,]\s*)([A-Za-z0-9_\-]+)(\s*:)'
    data_str = re.sub(pattern, r'\1"\2"\3', data_str)
    pattern_decimal = r'([:\[,]\s*)\.(\d+)'
    def fix_decimal(match):
        return match.group(1) + "0." + match.group(2)
    data_str = re.sub(pattern_decimal, fix_decimal, data_str)
    data_str = re.sub(r',\s*([}\]])', r'\1', data_str)
    try:
        data = json.loads(data_str)
        return data
    except json.JSONDecodeError as e:
        print(data_str)
        #print(body)
        raise e
    
def get_error(url: str) -> str:
    if "error" not in url:
        return None
    code = url.split("?error=")[1]
    code = code.split(".")[2]
    res = requests.get("https://blockcoin.vercel.app/_app/immutable/chunks/errors.Bm5X5eEC.js", impersonate="chrome")
    data = get_script_data(res.text, keyword="d")
    for error in data:
        if error["code"] == code:
            return error["description"]
    return "Unknown Error"

def login(username: str, password: str) -> "Session":
    from .session import Session
    return Session(username, password)

def _register(*args, **kwargs) -> "Session":
    from .session import Session
    return Session._register(*args, **kwargs)

def deep_merge(a: dict, b: dict) -> dict:
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            deep_merge(a[k], v)
        else:
            a[k] = v
    return a