import tkinter as tk
from tkinter import filedialog, messagebox
import extract_msg
import tempfile
import webbrowser
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

def open_msg_file():
    file_path = filedialog.askopenfilename(
        title="MSG 파일 선택",
        filetypes=[("Outlook 메시지", "*.msg"), ("모든 파일", "*.*")]
    )
    if not file_path:
        return

    try:
        msg = extract_msg.Message(file_path)
        sender = msg.sender or "(알 수 없음)"
        subject = msg.subject or "(제목 없음)"
        date = msg.date or "(날짜 없음)"
        html_body = decode_body(msg.htmlBody)
        text_body = decode_body(msg.body)
        body = html_body if html_body.strip() else f"<pre>{text_body}</pre>"

        # 임시 HTML 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
            html_content = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <title>{subject}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h2 {{ color: #333; }}
                    .meta {{ color: #555; font-size: 0.9em; margin-bottom: 20px; }}
                    pre {{ white-space: pre-wrap; }}
                </style>
            </head>
            <body>
                <h2>{subject}</h2>
                <div class="meta">
                    From: {sender}<br>
                    Date: {date}
                </div>
                <hr>
                {body}
            </body>
            </html>
            """
            f.write(html_content)
            temp_path = f.name

        # 브라우저로 열기
        webbrowser.open(f"file://{os.path.abspath(temp_path)}")

        # GUI에 요약 표시
        lbl_subject.config(text=f"제목: {subject}")
        lbl_sender.config(text=f"발신자: {sender}")
        lbl_date.config(text=f"날짜: {date}")
        lbl_status.config(text="✅ 열기 완료! (본문은 브라우저에서 확인하세요)")

    except Exception as e:
        messagebox.showerror("오류", f"파일을 여는 중 오류 발생:\n{e}")

# === Tkinter GUI 구성 ===
root = tk.Tk()
root.title("MSG Viewer (extract_msg 기반)")
root.geometry("480x250")
root.resizable(False, False)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill="both", expand=True)

tk.Label(frame, text="Outlook MSG 파일 뷰어", font=("맑은 고딕", 16, "bold")).pack(pady=(0, 15))

btn_open = tk.Button(frame, text="📂 MSG 파일 열기", font=("맑은 고딕", 12), command=open_msg_file)
btn_open.pack(pady=10)

lbl_subject = tk.Label(frame, text="제목: -", font=("맑은 고딕", 10))
lbl_subject.pack(anchor="w", pady=2)

lbl_sender = tk.Label(frame, text="발신자: -", font=("맑은 고딕", 10))
lbl_sender.pack(anchor="w", pady=2)

lbl_date = tk.Label(frame, text="날짜: -", font=("맑은 고딕", 10))
lbl_date.pack(anchor="w", pady=2)

lbl_status = tk.Label(frame, text="", font=("맑은 고딕", 10), fg="green")
lbl_status.pack(pady=(10, 0))

root.mainloop()
