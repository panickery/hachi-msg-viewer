import os
import extract_msg
from dateutil import parser as dtparser
from db import insert_message

SUPPORTED_EXT = ('.msg',)

def safe_text(x):
    if x is None:
        return ''
    if isinstance(x, (list, tuple)):
        return '; '.join(str(i) for i in x)
    return str(x)

def parse_msg_file(path):
    try:
        msg = extract_msg.Message(path)
        # extract_msg에서는 .subject, .sender, .date, .body, .to 등을 제공
        subj = safe_text(msg.subject)
        sender = safe_text(msg.sender)
        try:
            recipients = safe_text(msg.to)
        except Exception:
            recipients = ''
        try:
            # extract_msg.date는 str / datetime 혼합 가능
            raw_date = msg.date
            if raw_date:
                try:
                    date_text = str(raw_date)
                except Exception:
                    date_text = ''
            else:
                date_text = ''
        except Exception:
            date_text = ''
        body = safe_text(msg.body)
        return subj, sender, recipients, date_text, body
    except Exception as e:
        print('Failed parse', path, e)
        return None


def scan_folder(base_folder):
    """base_folder 하위 .msg 파일 전부 스캔하여 DB에 저장"""
    count = 0
    for root, dirs, files in os.walk(base_folder):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXT):
                full = os.path.join(root, f)
                parsed = parse_msg_file(full)
                if parsed:
                    subj, sender, recipients, date_text, body = parsed
                    insert_message(full, subj, sender, recipients, date_text, body)
                    count += 1
    return count

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python msg_parser.py <folder>')
        sys.exit(1)
    folder = sys.argv[1]
    print('Scanning', folder)
    n = scan_folder(folder)
    print('Done. Parsed', n)
