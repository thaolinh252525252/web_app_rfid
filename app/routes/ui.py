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
</style>
</head>
<body>
<!-- Toast hiển thị nổi (thông báo GRANTED / DENIED) -->
  <div id="toast" class="toast"></div>

  <div class="phone">
    <header>Gateway Control</header>

    <!-- Tabs -->
    <div class="tabs">
      <div class="tab active" data-tab="passkey">Passkey</div>
      <div class="tab" data-tab="fan">Quạt</div>
      <div class="tab" data-tab="notify">Thông báo</div>
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
  </div>

<script>

/* ==== TABS ==== */
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click', ()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
    t.classList.add('active');
    document.getElementById('tab-'+t.dataset.tab).classList.add('active');
  });
});

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
  const r = await fetch('/fan/state?device_id='+encodeURIComponent(dev));
  const js = await r.json();
  setToggle(js.desired_state === 'on');
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
    const js = await r.json();

    if(js.ok){
      setToggle(js.desired_state === 'on');
      // 🔔 Thông báo đẹp
      showToast(true, `Quạt ${dev}: ${js.desired_state.toUpperCase()}`);
    }else{
      showToast(false, `Quạt ${dev}: lỗi (${js.error || 'unknown'})`);
    }
  }catch(e){
    showToast(false, `Quạt ${dev}: lỗi mạng`);
    console.error(e);
  }

  // cập nhật feed để thấy dòng CONTROL mới
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
