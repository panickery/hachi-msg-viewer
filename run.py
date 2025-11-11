from flask import Flask, jsonify, request, render_template, send_from_directory
from db import init_db, search, get_message, list_messages_under_folder
from msg_parser import scan_folder
from config import DB_PATH
import os

app = Flask(__name__)

with app.app_context():
    init_db()  # DB 초기화

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.json or {}
    folder = data.get('folder')
    if not folder or not os.path.isdir(folder):
        return jsonify({'ok': False, 'error': 'Invalid folder'}), 400
    count = scan_folder(folder)
    return jsonify({'ok': True, 'scanned': count})

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    rows = search(q)
    results = []
    for r in rows:
        # r is tuple (id, subject, sender, msg_date)
        results.append({'id': r[0], 'subject': r[1], 'sender': r[2], 'date': r[3]})
    return jsonify(results)

@app.route('/api/message/<int:message_id>')
def api_message(message_id):
    r = get_message(message_id)
    if not r:
        return jsonify({'ok': False, 'error': 'not found'}), 404
    (mid, file_path, subject, sender, recipients, msg_date, body) = r
    return jsonify({'id': mid, 'file_path': file_path, 'subject': subject, 'sender': sender, 'recipients': recipients, 'date': msg_date, 'body': body})

@app.route('/api/list_folder_messages')
def api_list_folder_messages():
    folder = request.args.get('folder')
    if not folder:
        return jsonify([])
    rows = list_messages_under_folder(folder)
    out = [{'id': r[0], 'file_path': r[1], 'subject': r[2], 'sender': r[3], 'date': r[4]} for r in rows]
    return jsonify(out)

@app.route('/folders')
def get_folders():
    # DB에서 모든 폴더 경로 가져오기 (file_path 기준으로 폴더만 추출)
    import sqlite3
    from config import DB_PATH
    folders = set()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('SELECT file_path FROM messages')
        rows = cur.fetchall()
        for r in rows:
            folder = os.path.dirname(r[0])
            folders.add(folder)
    # 트리 구조로 변환
    def build_tree(paths):
        root = {}
        for p in paths:
            parts = p.split(os.sep)
            node = root
            for part in parts:
                node = node.setdefault(part, {})
        return root

    tree = build_tree(folders)
    return jsonify(tree)

@app.route('/messages/by-folder')
def get_messages_by_folder():
    folder = request.args.get('folder')
    if not folder:
        return jsonify([])
    rows = list_messages_under_folder(folder)
    out = [{'id': r[0], 'file_path': r[1], 'subject': r[2], 'sender': r[3], 'date': r[4]} for r in rows]
    return jsonify(out)


def build_tree(paths):
    root = {}
    for p in paths:
        parts = p.split('\\')
        node = root
        for part in parts:
            node = node.setdefault(part, {})
    return root

if __name__ == '__main__':
    app.run(port=5000, debug=True)
