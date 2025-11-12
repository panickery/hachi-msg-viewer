import extract_msg
import tempfile
import webbrowser
import sys
import os


def decode_body(data):
    """본문이 bytes일 경우 한글 인코딩 자동 감지 및 디코딩"""
    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return data.decode("cp949")
            except UnicodeDecodeError:
                return data.decode("latin1", errors="ignore")
    return data or ""


def view_msg_html(msg_path):
    msg = extract_msg.Message(msg_path)
    msg_sender = msg.sender
    msg_subject = msg.subject
    msg_date = msg.date

    # 본문 디코딩
    html_body = decode_body(msg.htmlBody)
    text_body = decode_body(msg.body)

    # htmlBody가 없으면 text_body 사용
    body = html_body if html_body.strip() else f"<pre>{text_body}</pre>"

    # 임시 HTML 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>{msg_subject}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h2 {{ color: #333; }}
                .meta {{ color: #555; font-size: 0.9em; margin-bottom: 20px; }}
                pre {{ white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <h2>{msg_subject}</h2>
            <div class="meta">
                From: {msg_sender}<br>
                Date: {msg_date}
            </div>
            <hr>
            {body}
        </body>
        </html>
        """
        f.write(html_content)
        temp_path = f.name

    webbrowser.open(f"file://{os.path.abspath(temp_path)}")
    print(f"✅ 열기 완료: {temp_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python msg_viewer.py <msg파일 경로>")
        sys.exit(1)

    msg_path = sys.argv[1]
    if not os.path.exists(msg_path):
        print("❌ 파일을 찾을 수 없습니다:", msg_path)
        sys.exit(1)

    view_msg_html(msg_path)
