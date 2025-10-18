# app/routes/ui.py
from flask import Blueprint, render_template_string
ui_bp = Blueprint("ui", __name__, url_prefix="")

HTML_UI = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Gateway UI</title>
<style>
  :root{ --bg:#0b1020; --card:#0f172a; --bd:#1f2a44; --txt:#e2e8f0; --muted:#94a3b8; 
         --green:#22c55e; --orange:#f59e0b; --red:#ef4444; --blue:#38bdf8; }
  *{box-sizing:border-box}
  body{margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto; background:var(--bg); color:var(--txt);}
  .phone{width:390px; height:844px; margin:16px auto; border:12px solid #111827; border-radius:36px; overflow:auto; box-shadow:0 10px 30px rgba(0,0,0,.5); background:#0a0f1f;}
  header{background:linear-gradient(90deg,#0ea5e9,#38bdf8); color:#fff; padding:14px 16px; font-weight:700;}
  .tabs{display:flex; gap:6px; padding:10px 12px; background:#0b1226; position:sticky; top:0; z-index:5; border-bottom:1px solid var(--bd)}
  .tab{flex:1; text-align:center; padding:10px 0; border:1px solid var(--bd); border-radius:10px; cursor:pointer; color:#cbd5e1; background:#0f172a}
  .tab.active{background:#0ea5e9; color:#fff; border-color:transparent; font-weight:700}
  section{display:none; padding:16px}
  section.active{display:block}
  .card{background:var(--card); border:1px solid var(--bd); padding:16px; border-radius:16px;}
  h2{margin:0 0 10px 0; font-size:16px}
  .row{display:flex; gap:8px; margin:8px 0; align-items:center; flex-wrap:wrap}
  .muted{color:var(--muted); font-size:12px}
  input{padding:10px 12px; border:1px solid var(--bd); border-radius:10px; background:#0b1226; color:var(--txt); width:100%;}
  button{padding:10px 12px; border:none; border-radius:10px; background:#0ea5e9; color:#fff; cursor:pointer;}
  button.secondary{background:#1f2937}

  /* Passcode */
  .screen{font-size:26px; letter-spacing:6px; background:#0b1226; padding:12px 14px; border-radius:12px; border:1px solid var(--bd); text-align:center;}
  .keys{display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:10px;}
  .key{padding:16px 0; background:#0b1226; border:1px solid var(--bd); border-radius:12px; text-align:center; font-size:20px; cursor:pointer; user-select:none;}
  .key:active{filter:brightness(1.2)}

  /* Toggle fan */
  .toggle{position:relative; width:60px; height:32px; background:#1f2937; border-radius:999px; cursor:pointer; border:1px solid var(--bd);}
  .knob{position:absolute; top:3px; left:3px; width:26px; height:26px; background:#fff; border-radius:50%; transition:all .2s ease;}
  .toggle.on{background:#065f46;}
  .toggle.on .knob{left:31px; background:#d1fae5;}
  .state-label{margin-left:8px; font-weight:600}

  /* Notifications */
  /* ép feed thành vùng cuộn độc lập */
  .feed{
  display:flex;
  flex-direction:column;
  gap:8px;                     /* khoảng cách giữa các item */
  margin-top:10px;
  padding:10px;
  height:320px;                /* ép chiều cao để xuất hiện scroll */
  overflow-y:auto;
  overscroll-behavior:contain;
  -webkit-overflow-scrolling:touch;
  background:#0b1226;
  border:1px solid var(--bd);
  border-radius:12px;
}

  /* nếu muốn luôn thấy scrollbar (hệ macOS/Ubuntu hay ẩn) */
  .feed::-webkit-scrollbar{ width: 8px; }
  .feed::-webkit-scrollbar-thumb{ background: #334155; border-radius: 8px; }


  .item{
  display:block;               /* mỗi thông báo là 1 block riêng */
  line-height: 0.4;
  padding: 13px 10px;
  border-radius:10px;
  border:1px solid var(--bd);
  white-space:nowrap;          /* 1 dòng */
  overflow:hidden;
  text-overflow:ellipsis;
  font-size:13px;
}

  .i-green{background:rgba(34,197,94,.1); color:#86efac;}
  .i-orange{background:rgba(245,158,11,.08); color:#fcd34d;}
  .i-red{background:rgba(239,68,68,.1); color:#fca5a5;}
  .i-gray{background:rgba(148,163,184,.08); color:#cbd5e1;}
  .i-blue{background:rgba(56,189,248,.12); color:#bae6fd;}
  .toast{
  position:fixed;
  left:50%;
  bottom:24px;
  transform:translateX(-50%);
  padding:10px 14px;
  border-radius:12px;
  border:1px solid var(--bd);
  backdrop-filter:blur(6px);
  background:rgba(15,23,42,.9);
  color:#e2e8f0;
  font-weight:600;
  box-shadow:0 10px 30px rgba(0,0,0,.4);
  opacity:0;
  pointer-events:none;
  transition:opacity .25s ease, transform .25s ease;
}
  .toast.show{opacity:1; transform:translateX(-50%) translateY(-6px);}
  .toast.ok{border-color:#14532d; color:#86efac;}
  .toast.err{border-color:#7f1d1d; color:#fca5a5;}
  /* Inline status ngay dưới nút Enter */
  .inline-status{
    min-height: 22px;             /* chừa chỗ ngay cả khi rỗng */
    margin-left: 10px;
    font-weight: 700;
    font-size: 13px;
    transition: opacity .2s ease;
    opacity: .95;
  }
  .inline-status.ok{  color: #86efac; }   /* xanh */
  .inline-status.err{ color: #fca5a5; }   /* đỏ  */
  @media (max-width: 420px){ .phone{width:100%; height:100vh; border:none; border-radius:0;} }

<!--rfid-->
  .rfid-grid{ display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
@media (max-width: 520px){ .rfid-grid{ grid-template-columns: 1fr; } }

  .listbox{
  height: 340px; overflow-y:auto; border:1px solid var(--bd);
  border-radius:12px; background:#0b1226; padding:6px;
}
  .listrow{
    display:flex; align-items:center; justify-content:space-between;
    gap:8px; padding:8px 10px; border-radius:10px; border:1px solid var(--bd);
    margin-bottom:6px;
  }
  .rowleft{ display:flex; flex-direction:column; }
  .rowright{ display:flex; gap:6px; }
  .badge{ font-size:11px; padding:3px 8px; border-radius:999px; border:1px solid var(--bd); }
  .badge.on{ background:rgba(34,197,94,.12); color:#86efac; }
  .badge.off{ background:rgba(239,68,68,.12); color:#fca5a5; }
  .btn-mini{ padding:6px 8px; font-size:12px; border:none; border-radius:8px; cursor:pointer; background:#0ea5e9; color:#fff; }
  .btn-mini.alt{ background:#1f2937; }

  /* MODALS */
  .modal-backdrop{ position:fixed; inset:0; background:rgba(0,0,0,.55); display:none; align-items:center; justify-content:center; z-index:50; }
  .modal{ width:min(92vw, 420px); background:#0f172a; border:1px solid var(--bd); border-radius:14px; padding:16px; box-shadow:0 10px 30px rgba(0,0,0,.5); }
  .modal h3{ margin:0 0 10px 0; font-size:16px }
  .modal .muted{ font-size:12px }
  .modal-actions{ display:flex; justify-content:flex-end; gap:8px; margin-top:12px }
  .show-modal{ display:flex; }
  .spinner{ width:18px;height:18px;border:3px solid #334155;border-top-color:#38bdf8;border-radius:50%; display:inline-block; animation:spin .9s linear infinite; vertical-align:middle; margin-right:8px; }
  @keyframes spin{ to { transform: rotate(360deg); } }


</style>
</head>
<body>

<!-- Modal chi tiết 1 log RFID -->
<div id="log_backdrop" class="modal-backdrop">
  <div class="modal">
    <h3>Chi tiết lượt vào/ra</h3>
    <div class="row"><div class="muted">UID</div><div id="lg_uid"></div></div>
    <div class="row"><div class="muted">Owner</div><div id="lg_owner"></div></div>
    <div class="row"><div class="muted">Device</div><div id="lg_device"></div></div>
    <div class="row"><div class="muted">Kết quả</div><div id="lg_result"></div></div>
    <div class="row"><div class="muted">Thời gian</div><div id="lg_time"></div></div>
    <div class="modal-actions">
      <button class="secondary" onclick="closeLogModal()">Đóng</button>
    </div>
  </div>
</div>


<!-- Modal thêm/sửa (form) -->
<div id="rfid_modal" class="modal-backdrop">
  <div class="modal">
    <h3 id="rfid_modal_title">Thông tin thẻ</h3>
    <div class="row"><input id="f_uid" placeholder="UID (hex)"></div>
    <div class="row"><input id="f_owner" placeholder="Chủ thẻ (Owner)"></div>
    <div class="row"><input id="f_type" placeholder="Card type" value="MIFARE Classic"></div>
    <div class="row"><input id="f_desc" placeholder="Mô tả"></div>
    <div class="row"><input id="f_expires" placeholder="Hết hạn (ISO) - tuỳ chọn"></div>
    <div class="row"><label><input type="checkbox" id="f_active" checked> Active</label></div>
    <div class="modal-actions">
      <button class="secondary" onclick="closeEditModal()">Đóng</button>
      <button onclick="saveRfid()">Lưu</button>
    </div>
    <div class="muted" id="rfid_hint"></div>
  </div>
</div>

<!-- Modal xác nhận xoá -->
<div id="confirm_backdrop" class="modal-backdrop">
  <div class="modal">
    <h3>Xoá thẻ</h3>
    <div class="muted" id="confirm_text">Bạn chắc muốn xoá?</div>
    <div class="modal-actions">
      <button class="secondary" onclick="closeConfirm()">Hủy</button>
      <button onclick="confirmDelete()">Xoá</button>
    </div>
  </div>
</div>

<!-- Popup chờ quét RFID -->
<div id="scan_backdrop" class="modal-backdrop">
  <div class="modal">
    <h3>Thêm thẻ RFID</h3>
    <div class="muted" id="scan_status">
      <span class="spinner"></span>Đang chờ bạn quét thẻ trên đầu đọc...
    </div>
    <div class="modal-actions">
      <button class="secondary" onclick="closeScanModal()">Hủy</button>
    </div>
  </div>
</div>

<!-- Toast hiển thị nổi (thông báo GRANTED / DENIED) -->
  <div id="toast" class="toast"></div>

  <div class="phone">
    <header>Gateway Control</header>

    <!-- Tabs -->
    <div class="tabs">
      <div class="tab active" data-tab="passkey">Passkey</div>
      <div class="tab" data-tab="fan">Quạt</div>
      <div class="tab" data-tab="notify">Thông báo</div>
      <div class="tab" data-tab="rfid">RFID</div>

    </div>

    <!-- PASSKEY TAB -->
    <section id="tab-passkey" class="active">
      <div class="card">
        <h2>Mở cửa bằng Passcode</h2>
        <div class="row"><input id="device_id" value="passkey_01" placeholder="device_id (ví dụ passkey_01)"></div>
        <div id="screen" class="screen">******</div>
        <div class="keys">
          <div class="key" onclick="tap('1')">1</div><div class="key" onclick="tap('2')">2</div><div class="key" onclick="tap('3')">3</div>
          <div class="key" onclick="tap('4')">4</div><div class="key" onclick="tap('5')">5</div><div class="key" onclick="tap('6')">6</div>
          <div class="key" onclick="tap('7')">7</div><div class="key" onclick="tap('8')">8</div><div class="key" onclick="tap('9')">9</div>
          <div class="key" onclick="delKey()">⌫</div><div class="key" onclick="tap('0')">0</div><div class="key" onclick="clearKey()">C</div>
        </div>
        <div class="row">
          <button onclick="submitPasscode()">Enter</button>
          <span id="pass_inline" class="inline-status"></span>
        </div>
      </div>
    </section>

    <!-- FAN TAB -->
    <section id="tab-fan">
      <div class="card">
        <h2>Quạt (Relay)</h2>
        <div class="row">
          <input id="fdev" value="fan_01" style="max-width:180px" placeholder="device_id">
          <div id="toggler" class="toggle" onclick="toggleFan()"><div class="knob"></div></div>
          <span id="fan_label" class="state-label">Off</span>
        </div>
      </div>
    </section>

    <!-- NOTIFY TAB -->
    <section id="tab-notify">
      <div class="card">
        <h2>Thông báo hôm nay</h2>
        <div class="row">
          <button onclick="loadFeed()">Làm mới</button>
          <span class="muted">Mới nhất ở trên • 1 dòng/thông báo • tự lọc theo ngày</span>
        </div>
        <div id="feed" class="feed"></div>
      </div>
    </section>
  <!-- RFID TAB -->
<section id="tab-rfid">
  <div class="card">
    <h2>Quản lý RFID</h2>

    <div class="row">
      <input id="rfid_search" placeholder="Tìm theo UID/Owner..." oninput="filterRfid()">
      <button onclick="startAddRfid()">Thêm thẻ</button>
    </div>

    <!-- Danh sách thẻ có nút Sửa/Xoá trên mỗi dòng -->
    <div id="rfid_list" class="listbox"></div>

    <div style="margin-top:12px">
      <div class="row">
        <h3 style="margin:0;font-size:14px">Lịch sử vào/ra</h3>
        <span class="muted">(mới nhất trước)</span>
      </div>
      <div id="rfid_logs" class="feed"></div>
    </div>
  </div>
</section>



  </div>


<script>

/* ==== TABS ==== */
// Khi click tab
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click', ()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
    t.classList.add('active');
    const sectionId = 'tab-'+t.dataset.tab;
    document.getElementById(sectionId).classList.add('active');

    // 👉 Tự load danh sách khi vào tab RFID
    if(t.dataset.tab === 'rfid'){
      loadRfid();
    }
  });
});

// 👉 Lần đầu mở UI, load luôn danh sách RFID
loadRfid();


/* ==== PASSKEY (mask bằng *) ==== */
/* ==== PASSKEY (placeholder đổi ký tự sau mỗi lần Enter) ==== */
let passBuf = "";
let placeholderChar = '*'; // sẽ luân phiên '*' ↔ '·'

function renderScreen(){
  const screen = document.getElementById('screen');
  if(passBuf.length){
    // Khi đang nhập, luôn hiển thị dấu chấm tròn để mask
    screen.textContent = '•'.repeat(passBuf.length);
  }else{
    // Khi rỗng, hiện placeholder 4 ký tự: ****** hoặc ···· (luân phiên)
    screen.textContent = placeholderChar.repeat(6);
  }
}
function tap(d){ if(passBuf.length<12){ passBuf += d; renderScreen(); } }
function delKey(){ passBuf = passBuf.slice(0,-1); renderScreen(); }
function clearKey(){ passBuf = ""; renderScreen(); }

function togglePlaceholder(){ placeholderChar = (placeholderChar === '*') ? '·' : '*'; }

function showToast(ok, msg){
  const el = document.getElementById('toast');
  el.className = 'toast ' + (ok ? 'ok' : 'err');
  el.textContent = msg;
  // show
  requestAnimationFrame(()=>{
    el.classList.add('show');
    setTimeout(()=> el.classList.remove('show'), 1600);
  });
}

async function submitPasscode(){
  const device_id = (document.getElementById('device_id').value || 'passkey_01').trim();
  if(!passBuf){ showToast(false, 'Chưa nhập mã'); return; }

  const body = { passcode: String(passBuf).trim(), device_id };
  try{
    const r = await fetch('/access/passcode', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(body)
    });
    const js = await r.json();

    if(js.ok){
      showToast(true, 'Mở cửa: GRANTED');
      // Reset buffer + đổi placeholder khác ký tự
      passBuf = "";
      togglePlaceholder();
      renderScreen();
    }else{
      // Không hiện reason thô kỹ thuật nữa — chỉ thông điệp đẹp
      showToast(false, 'Từ chối: DENIED');
      // Cũng reset để nhập lại nhanh
      passBuf = "";
      togglePlaceholder();
      renderScreen();
    }
  }catch(e){
    showToast(false, 'Lỗi mạng');
    console.error(e);
  }
  // làm mới feed sau thao tác
  setTimeout(loadFeed, 150);
}


/* ==== FAN TOGGLE ==== */
function setToggle(on){
  const t = document.getElementById('toggler');
  const label = document.getElementById('fan_label');
  if(on){ t.classList.add('on'); label.textContent = 'On'; }
  else { t.classList.remove('on'); label.textContent = 'Off'; }
}
async function loadFan(){
  const dev = document.getElementById('fdev').value || "fan_01";
  try{
    const r = await fetch('/fan/state?device_id='+encodeURIComponent(dev));
    if(!r.ok){
      showToast(false, `Fan ${dev}: ${r.status}`);
      return;
    }
    const js = await r.json();
    setToggle(js.desired_state === 'on');
  }catch(e){
    showToast(false, 'Fan: lỗi mạng');
    console.error(e);
  }
}

async function toggleFan(){
  const dev = document.getElementById('fdev').value || "fan_01";
  const isOn = document.getElementById('toggler').classList.contains('on');
  const next = isOn ? 'off' : 'on';
  try{
    const r = await fetch('/fan/toggle', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ device_id: dev, state: next })
    });
    if(!r.ok){
      showToast(false, `Quạt ${dev}: ${r.status}`);
      return;
    }
    const js = await r.json();
    if(js.ok){
      setToggle(js.desired_state === 'on');
      showToast(true, `Quạt ${dev}: ${js.desired_state.toUpperCase()}`);
    }else{
      showToast(false, `Quạt ${dev}: lỗi (${js.error||'unknown'})`);
    }
  }catch(e){
    showToast(false, 'Quạt: lỗi mạng');
    console.error(e);
  }
  setTimeout(loadFeed, 150);
}



/* ==== NOTIFY ==== */
async function loadFeed(){
  const r = await fetch('/notify/today');
  const arr = await r.json();
  const box = document.getElementById('feed');
  box.innerHTML = '';
  if(!Array.isArray(arr) || !arr.length){
    box.innerHTML = '<div class="item i-gray">Không có thông báo hôm nay</div>';
    return;
  }
  for(const it of arr){
    const div = document.createElement('div');
    let cls = 'i-gray';
    if(it.color==='green') cls='i-green';
    else if(it.color==='orange') cls='i-orange';
    else if(it.color==='red') cls='i-red';
    else if(it.color==='blue') cls='i-blue';
    div.className = 'item ' + cls;
    div.textContent = it.text;
    box.appendChild(div);
  }
  box.scrollTop = 0;     // <— quan trọng
}


/* ==== RFID Management ==== */
let RFID_ALL = [];
let RFID_SELECTED = null;
let RFID_IS_ADDING = false;
let SCAN_TIMER = null;
let SCAN_AFTER = null;
let DELETE_UID = null;

/* Load list ngay khi mở UI & khi vào tab RFID */
async function initRfidOnStart(){ await loadRfid(); }
document.addEventListener('DOMContentLoaded', initRfidOnStart);
/* Nếu bạn có handler chuyển tab, nhớ gọi loadRfid() khi tab=rfid */

function renderRfidList(arr){
  const box = document.getElementById('rfid_list');
  box.innerHTML = '';
  if(!arr.length){ box.innerHTML = '<div class="muted">Không có thẻ</div>'; return; }
  for(const c of arr){
    const row = document.createElement('div'); row.className = 'listrow';

    const left = document.createElement('div'); left.className='rowleft';
    const line1 = document.createElement('div');
    line1.innerHTML = `<b>${c.uid}</b> <span class="badge ${c.active?'on':'off'}">${c.active?'Active':'Inactive'}</span>`;
    const line2 = document.createElement('div'); line2.className='muted'; line2.style.fontSize='12px'; line2.textContent = c.owner||'-';
    left.appendChild(line1); left.appendChild(line2);

    const right = document.createElement('div'); right.className='rowright';
    const btnEdit = document.createElement('button'); btnEdit.className='btn-mini'; btnEdit.textContent='Sửa';
    btnEdit.onclick = (e)=>{ e.stopPropagation(); openEditForUid(c.uid); };
    const btnDelete = document.createElement('button'); btnDelete.className='btn-mini alt'; btnDelete.textContent='Xoá';
    btnDelete.onclick = (e)=>{ e.stopPropagation(); openConfirm(c.uid); };
    right.appendChild(btnEdit); right.appendChild(btnDelete);

    row.appendChild(left); row.appendChild(right);
    row.onclick = ()=> openEditForUid(c.uid);
    box.appendChild(row);
  }
}

async function loadRfid(){
  try{
    const r = await fetch('/rfid/list');
    if(!r.ok){ showToast(false, 'RFID list: '+r.status); return; }
    RFID_ALL = await r.json();
    RFID_ALL.sort((a,b)=> (b.active?1:0)-(a.active?1:0));
    renderRfidList(RFID_ALL);
    // nếu đang chọn, refresh logs
    if(RFID_SELECTED){ loadRfidLogs(RFID_SELECTED); }
  }catch(e){
    showToast(false, 'RFID: lỗi mạng');
  }
}

function filterRfid(){
  const q = (document.getElementById('rfid_search')?.value || '').toLowerCase();
  const f = RFID_ALL.filter(x=> (x.uid||'').toLowerCase().includes(q) || (x.owner||'').toLowerCase().includes(q));
  renderRfidList(f);
}

/* ===== Modals ===== */
function openScanModal(){
  document.getElementById('scan_backdrop').classList.add('show-modal');
  document.getElementById('scan_status').innerHTML = '<span class="spinner"></span>Đang chờ bạn quét thẻ…';
  SCAN_AFTER = new Date().toISOString(); // mốc để chỉ nhận quét mới
  SCAN_TIMER = setInterval(checkScanOnce, 1000);
}
function closeScanModal(){
  document.getElementById('scan_backdrop').classList.remove('show-modal');
  if(SCAN_TIMER){ clearInterval(SCAN_TIMER); SCAN_TIMER=null; }
}

function openEditModal(title='Thông tin thẻ'){
  document.getElementById('rfid_modal_title').textContent = title;
  document.getElementById('rfid_modal').classList.add('show-modal');
}
function closeEditModal(){
  document.getElementById('rfid_modal').classList.remove('show-modal');
}

function openConfirm(uid){
  DELETE_UID = uid;
  document.getElementById('confirm_text').textContent = 'Xoá thẻ '+uid+' ?';
  document.getElementById('confirm_backdrop').classList.add('show-modal');
}
function closeConfirm(){
  DELETE_UID = null;
  document.getElementById('confirm_backdrop').classList.remove('show-modal');
}

/* ===== Flow Thêm/Sửa/Xoá ===== */
let ENROLL_SESSION = null;
let ENROLL_TIMER = null;

async function startAddRfid(){
  openScanModal(); // popup “chờ quét”
  try{
    const rs = await fetch('/rfid/enroll/start', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ device_id: 'rfid_gate_01', ttl_sec: 60 })
    });
    const js = await rs.json();
    if(!js.ok){ document.getElementById('scan_status').textContent='Không tạo được phiên enroll'; return; }
    ENROLL_SESSION = js.session_id;
    // poll enroll
    ENROLL_TIMER = setInterval(pollEnrollOnce, 600);
  }catch(e){
    document.getElementById('scan_status').textContent='Lỗi mạng';
  }
}

async function pollEnrollOnce(){
  if(!ENROLL_SESSION) return;
  try{
    const r = await fetch('/rfid/enroll/poll?session_id='+encodeURIComponent(ENROLL_SESSION));
    const js = await r.json();
    if(!js.ok){
      closeScanModal();
      ENROLL_SESSION=null; clearInterval(ENROLL_TIMER); ENROLL_TIMER=null;
      alert('Enroll hết hạn hoặc lỗi'); return;
    }
    if(js.captured){
      const { uid, exists } = js.captured;
      closeScanModal();
      clearInterval(ENROLL_TIMER); ENROLL_TIMER=null;

      if(exists){ openEditForUid(uid); }
      else{
        RFID_IS_ADDING = true; RFID_SELECTED = null;
        document.getElementById('f_uid').readOnly = false;
        document.getElementById('f_uid').value = uid;
        document.getElementById('f_owner').value = '';
        document.getElementById('f_type').value  = 'MIFARE Classic';
        document.getElementById('f_desc').value  = '';
        document.getElementById('f_expires').value = '';
        document.getElementById('f_active').checked = true;
        document.getElementById('rfid_hint').textContent = 'Thẻ mới: nhập Owner/Mô tả rồi bấm Lưu.';
        openEditModal('Thêm thẻ RFID');
      }

      // kết thúc session phía server (không chờ)
      fetch('/rfid/enroll/stop', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ session_id: ENROLL_SESSION })
      });
      ENROLL_SESSION = null;
    }
  }catch(e){ /* im lặng, tiếp tục poll */ }
}

function closeScanModal(){
  document.getElementById('scan_backdrop').classList.remove('show-modal');
  if(ENROLL_TIMER){ clearInterval(ENROLL_TIMER); ENROLL_TIMER=null; }
  if(ENROLL_SESSION){
    fetch('/rfid/enroll/stop', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ session_id: ENROLL_SESSION })
    });
    ENROLL_SESSION = null;
  }
}


async function checkScanOnce(){
  try{
    const r = await fetch('/rfid/scan/latest?after='+encodeURIComponent(SCAN_AFTER));
    if(!r.ok) return;
    const js = await r.json();
    const status = document.getElementById('scan_status');
    if(js && js.event){
      const { uid, exists } = js.event;
      if(exists){
        status.innerHTML = `Thẻ <b>${uid}</b> đã tồn tại. Mở để sửa…`;
        setTimeout(()=>{ closeScanModal(); openEditForUid(uid); }, 600);
      }else{
        closeScanModal();
        RFID_IS_ADDING = true; RFID_SELECTED = null;
        // mở form modal với UID auto
        document.getElementById('f_uid').readOnly = false;
        document.getElementById('f_uid').value = uid;
        document.getElementById('f_owner').value = '';
        document.getElementById('f_type').value  = 'MIFARE Classic';
        document.getElementById('f_desc').value  = '';
        document.getElementById('f_expires').value = '';
        document.getElementById('f_active').checked = true;
        document.getElementById('rfid_hint').textContent = 'Thẻ mới: nhập Owner/Mô tả rồi bấm Lưu.';
        openEditModal('Thêm thẻ RFID');
      }
      SCAN_AFTER = js.event.timestamp; // không xử lý lại event cũ
    }
  }catch(e){ /* ignore */ }
}

async function openEditForUid(uid){
  try{
    const r = await fetch('/rfid/'+encodeURIComponent(uid));
    const js = await r.json();
    if(!js.ok){ showToast(false, 'Không tìm thấy thẻ'); return; }
    const c = js.card;
    RFID_IS_ADDING = false; RFID_SELECTED = uid;
    document.getElementById('f_uid').readOnly = true;
    document.getElementById('f_uid').value = c.uid;
    document.getElementById('f_owner').value = c.owner||'';
    document.getElementById('f_type').value  = c.card_type||'MIFARE Classic';
    document.getElementById('f_desc').value  = c.description||'';
    document.getElementById('f_expires').value = c.expires_at||'';
    document.getElementById('f_active').checked = !!c.active;
    document.getElementById('rfid_hint').textContent =
      `Đăng ký: ${c.registered_at||'-'} • Lần dùng: ${c.last_used||'-'}`;
    openEditModal('Sửa thẻ RFID');
    // lịch sử
    loadRfidLogs(uid);
  }catch(e){ showToast(false, 'RFID: lỗi mạng'); }
}

async function saveRfid(){
  const uid = (document.getElementById('f_uid').value || '').trim();
  const body = {
    owner: (document.getElementById('f_owner').value || '').trim(),
    card_type: (document.getElementById('f_type').value || '').trim() || 'MIFARE Classic',
    description: (document.getElementById('f_desc').value || '').trim(),
    expires_at: (document.getElementById('f_expires').value || '').trim() || null,
    active: document.getElementById('f_active').checked
  };
  if(!uid){ showToast(false, 'Thiếu UID'); return; }

  try{
    if(RFID_IS_ADDING){
      const r = await fetch('/rfid/add', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ uid, ...body }) });
      const js = await r.json();
      if(js.ok){
        showToast(true, 'Đã thêm thẻ');
        RFID_IS_ADDING = false; RFID_SELECTED = uid;
        closeEditModal();
        await loadRfid();         // auto refresh list
        await loadRfidLogs(uid);  // show history
      }else{
        showToast(false, 'Thêm thất bại: '+(js.error||''));
      }
    }else{
      const r = await fetch('/rfid/'+encodeURIComponent(uid), { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) });
      const js = await r.json();
      if(js.ok){
        showToast(true, 'Đã thêm thẻ. Vui lòng quét lại thẻ để vào.');
        RFID_IS_ADDING = false; RFID_SELECTED = uid;
        closeEditModal();
        await loadRfid();         // refresh list tự động
        await loadRfidLogs(uid);  // show history
        setTimeout(loadFeed, 150); // feed có dòng RFID ADD
      }
      else{
        showToast(false, 'Lưu thất bại: '+(js.error||''));
      }
    }
  }catch(e){ showToast(false, 'RFID: lỗi mạng'); }
}

function openConfirm(uid){ /* đã định nghĩa trên */ }
async function confirmDelete(){
  if(!DELETE_UID){ closeConfirm(); return; }
  try{
    const r = await fetch('/rfid/'+encodeURIComponent(DELETE_UID), { method:'DELETE' });
    const js = await r.json();
    if(js.ok){
      showToast(true, 'Đã xoá');
      closeConfirm();
      DELETE_UID = null;
      RFID_SELECTED = null;
      await loadRfid();           // refresh list
      document.getElementById('rfid_logs').innerHTML = '<div class="item i-gray">Chưa có lịch sử</div>';
    }else{
      showToast(false, 'Xoá thất bại: '+(js.error||''));
    }
  }catch(e){ showToast(false, 'RFID: lỗi mạng'); }
}
function closeConfirm(){ document.getElementById('confirm_backdrop').classList.remove('show-modal'); DELETE_UID=null; }

/* logs của thẻ */
function openLogModal(it){
  document.getElementById('lg_uid').textContent = it.uid || '-';
  document.getElementById('lg_owner').textContent = it.owner || '-';
  document.getElementById('lg_device').textContent = it.device || '-';
  document.getElementById('lg_result').textContent = (it.result||'-').toUpperCase();
  const t = new Date(it.timestamp);
  document.getElementById('lg_time').textContent = t.toLocaleString();
  document.getElementById('log_backdrop').classList.add('show-modal');
}
function closeLogModal(){
  document.getElementById('log_backdrop').classList.remove('show-modal');
}

async function loadRfidLogs(uid){
  try{
    const r = await fetch('/rfid/logs?uid='+encodeURIComponent(uid));
    if(!r.ok){ showToast(false, 'RFID logs: '+r.status); return; }
    const arr = await r.json();
    const box = document.getElementById('rfid_logs');
    box.innerHTML = '';
    if(!arr.length){
      box.innerHTML = '<div class="item i-gray">Chưa có lượt vào/ra</div>';
      return;
    }
    for(const it of arr){
      const div = document.createElement('div');
      const cls = (it.result==='granted') ? 'i-green' : 'i-orange';
      div.className = 'item '+cls;
      const t = new Date(it.timestamp);
      const hh = t.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
      div.textContent = `[${hh}] ${it.result.toUpperCase()} (${it.device}, uid=${it.uid})`;
      div.style.cursor = 'pointer';
      div.onclick = ()=> openLogModal(it);
      box.appendChild(div);
    }
    box.scrollTop = 0;
  }catch(e){
    showToast(false, 'RFID: lỗi mạng');
  }
}
async function deleteRfid(){
  const uid = (document.getElementById('f_uid').value || '').trim();
  if(!uid){ alert('Chưa chọn thẻ'); return; }

  // ✅ Popup xác nhận
  if(!confirm('Xoá thẻ ' + uid + ' ?')) return;

  try{
    const r = await fetch('/rfid/'+encodeURIComponent(uid), { method:'DELETE' });
    const js = await r.json();
    if(js.ok){
      alert('Đã xoá thẻ.');
      RFID_SELECTED = null;
      await loadRfid(); // tự refresh danh sách
      document.getElementById('rfid_logs').innerHTML = '<div class="item i-gray">Chưa có lịch sử</div>';
    }else{
      alert('Xoá thất bại: ' + (js.error || ''));
    }
  }catch(e){
    alert('RFID: lỗi mạng');
  }
}




/* Init */
renderScreen(); loadFan(); loadFeed();
</script>
</body>
</html>
"""
@ui_bp.get("/ui")
def ui(): return render_template_string(HTML_UI)

@ui_bp.get("/")
def index():
    from flask import redirect
    return redirect("/ui", code=302)
