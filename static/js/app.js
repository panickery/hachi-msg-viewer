async function api(path, opts){
  const res = await fetch(path, opts);
  return res.json();
}

async function loadFolders() {
const res = await fetch('/folders');
const tree = await res.json();
renderFolderTree(tree, document.getElementById('folderTree'), '');
}


function renderFolderTree(node, container, path) {
Object.keys(node).forEach(key => {
const full = path ? `${path}\${key}` : key;
const div = document.createElement('div');
div.textContent = key;
div.classList.add('folder-item');
div.onclick = () => loadMessagesByFolder(full);
container.appendChild(div);
const child = document.createElement('div');
child.classList.add('folder-children');
container.appendChild(child);
renderFolderTree(node[key], child, full);
});
}


async function loadMessagesByFolder(folder) {
const res = await fetch(`/messages/by-folder?folder=${encodeURIComponent(folder)}`);
const list = await res.json();
const container = document.getElementById('messageList');
container.innerHTML = '';
list.forEach(msg => {
const item = document.createElement('div');
item.classList.add('message-item');
item.textContent = `${msg.subject} (${msg.sender})`;
item.onclick = () => loadMessage(msg.id);
container.appendChild(item);
});
}

document.getElementById('scan-btn').addEventListener('click', async ()=>{
  const folder = document.getElementById('folder-input').value.trim();
  if(!folder) { alert('폴더 경로 입력'); return; }
  const r = await api('/api/scan', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({folder})});
  if(r.ok) alert('스캔 완료: ' + r.scanned);
});

document.getElementById('search-btn').addEventListener('click', async ()=>{
  const q = document.getElementById('search-input').value.trim();
  if(!q) return;
  const rows = await api('/api/search?q=' + encodeURIComponent(q));
  const list = document.getElementById('message-list');
  list.innerHTML = '';
  for(const r of rows){
    const el = document.createElement('div');
    el.className = 'msg-row';
    el.textContent = `${r.subject || '(제목없음)'} — ${r.sender || ''} — ${r.date || ''}`;
    el.dataset.id = r.id;
    el.addEventListener('click', ()=> loadMessage(r.id));
    list.appendChild(el);
  }
});

async function loadMessage(id){
  const r = await api('/api/message/' + id);
  const d = document.getElementById('message-detail');
  d.innerHTML = `<h2>${escapeHtml(r.subject)}</h2><p><strong>From:</strong> ${escapeHtml(r.sender)}<br/><strong>To:</strong> ${escapeHtml(r.recipients)}<br/><strong>Date:</strong> ${escapeHtml(r.date)}</p><hr/><pre>${escapeHtml(r.body)}</pre>`;
}

function escapeHtml(s){
  if(!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

window.onload = () => {
loadFolders();
};