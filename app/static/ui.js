/* ===== Utils ===== */
function showToast(ok, msg){
  const t = document.getElementById('toast');
  t.className = 'toast ' + (ok ? 'ok' : 'err') + ' show';
  t.textContent = msg;
  setTimeout(()=>{ t.classList.remove('show'); }, 2200);
}
function setToggle(on){
  const tg = document.getElementById('toggler');
  tg.classList.toggle('on', !!on);
}
function nowISO(){ return new Date().toISOString(); }

/* ===== Clock ===== */
function tick(){
  document.getElementById('clock').textContent = new Date().toLocaleString();
}
setInterval(tick, 1000); tick();

/* ===== Tabs ===== */
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click', ()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
    t.classList.add('active');
    document.getElementById('tab-'+t.dataset.tab).classList.add('active');
    if(t.dataset.tab==='fan') loadFan();
    if(t.dataset.tab==='notify') loadFeed();
    if(t.dataset.tab==='rfid') loadRfid();
  });
});

/* ===== PASSKEY ===== */
let passBuf = '';
let masked = true;
function renderPass(){
  const v = masked ? '•'.repeat(passBuf.length) : '·'.repeat(passBuf.length);
  document.getElementById('pass_input').value = v || '';
}
function pressNum(d){
  if(passBuf.length >= 12) return;
  passBuf += d; masked = true; renderPass();
}
function backspace(){ passBuf = passBuf.slice(0,-1); masked = true; renderPass(); }
function clearPass(){
  passBuf = ''; masked = true; renderPass();
  const st = document.getElementById('pass_status');
  st.textContent=''; st.className='status muted';
}
async function submitPasscode(){
  const pin = passBuf;
  if(!pin){ showToast(false,'Nhập passkey'); return; }
  try{
    const r = await fetch('/access/passcode', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ passcode: pin, device_id: 'passkey_01' })
    });
    const js = await r.json();
    masked = false; renderPass();
    const st = document.getElementById('pass_status');
    if(js.ok){ st.textContent='GRANTED • mở cửa'; st.className='status i-green'; showToast(true,'PASSKEY GRANTED'); }
    else { st.textContent='DENIED'; st.className='status i-red'; showToast(false,'PASSKEY DENIED'); }
  }catch(e){ showToast(false,'Lỗi mạng'); }
  setTimeout(()=>{ clearPass(); }, 1200);
}

/* ===== FAN ===== */
async function loadFan(){
  const dev = document.getElementById('fdev').value || 'fan_01';
  try{
    const r = await fetch('/fan/state?device_id='+encodeURIComponent(dev));
    if(!r.ok){ showToast(false, 'Fan '+dev+': '+r.status); return; }
    const js = await r.json();
    setToggle(js.desired_state === 'on');
  }catch(e){ showToast(false,'Fan: lỗi mạng'); }
}
async function toggleFan(){
  const dev = document.getElementById('fdev').value || 'fan_01';
  const isOn = document.getElementById('toggler').classList.contains('on');
  const next = isOn ? 'off' : 'on';
  try{
    const r = await fetch('/fan/toggle', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ device_id: dev, state: next })
    });
    const js = await r.json();
    if(!r.ok || !js.ok){ showToast(false,'Quạt lỗi'); return; }
    setToggle(js.desired_state === 'on');
    showToast(true, `Quạt ${dev}: ${js.desired_state.toUpperCase()}`);
  }catch(e){ showToast(false,'Fan: lỗi mạng'); }
  setTimeout(loadFeed, 150);
}

/* ===== NOTIFY ===== */
async function loadFeed(){
  try{
    const r = await fetch('/notify/today');
    if(!r.ok){ return; }
    const arr = await r.json();
    const box = document.getElementById('feed');
    box.innerHTML = '';
    if(!arr.length){ box.innerHTML = '<div class="item i-gray">Chưa có thông báo</div>'; return; }
    for(const it of arr){
      const div = document.createElement('div');
      div.className = 'item ' + (it.color==='green'?'i-green':it.color==='red'?'i-red':it.color==='orange'?'i-orange':'i-blue');
      div.textContent = it.text;
      box.appendChild(div);
    }
    box.scrollTop = 0;
  }catch(e){}
}

/* ===== RFID ===== */
let RFID_ALL = [];
let RFID_SELECTED = null;
let RFID_IS_ADDING = false;

function renderRfidList(arr){
  const box = document.getElementById('rfid_list');
  box.innerHTML = '';
  if(!arr.length){ box.innerHTML = '<div class="muted">Không có thẻ</div>'; return; }
  for(const c of arr){
    const row = document.createElement('div'); row.className='listrow';
    const left = document.createElement('div'); left.className='rowleft';
    const line1 = document.createElement('div');
    line1.innerHTML = `<b>${c.uid}</b> <span class="badge ${c.active?'on':'off'}">${c.active?'Active':'Inactive'}</span>`;
    const line2 = document.createElement('div'); line2.className='muted'; line2.style.fontSize='12px'; line2.textContent=c.owner||'-';
    left.appendChild(line1); left.appendChild(line2);

    const right = document.createElement('div'); right.className='rowright';
    const btnEdit = document.createElement('button'); btnEdit.className='btn-mini'; btnEdit.textContent='Sửa';
    btnEdit.onclick=(e)=>{ e.stopPropagation(); openEditForUid(c.uid); };
    const btnDel = document.createElement('button'); btnDel.className='btn-mini alt'; btnDel.textContent='Xoá';
    btnDel.onclick=async (e)=>{ e.stopPropagation(); deleteByUid(c.uid); };

    right.appendChild(btnEdit); right.appendChild(btnDel);
    row.appendChild(left); row.appendChild(right);
    row.onclick=()=>openEditForUid(c.uid);
    box.appendChild(row);
  }
}
async function loadRfid(){
  try{
    const r = await fetch('/rfid/list');
    if(!r.ok){ showToast(false,'RFID list lỗi'); return; }
    RFID_ALL = await r.json();
    RFID_ALL.sort((a,b)=> (b.active?1:0) - (a.active?1:0));
    renderRfidList(RFID_ALL);
    if(RFID_SELECTED) loadRfidLogs(RFID_SELECTED);
  }catch(e){}
}
function filterRfid(){
  const q = (document.getElementById('rfid_search')?.value||'').toLowerCase();
  const f = RFID_ALL.filter(x => (x.uid||'').toLowerCase().includes(q) || (x.owner||'').toLowerCase().includes(q));
  renderRfidList(f);
}

/* --- Modal helpers --- */
function openEditModal(title='Thông tin thẻ'){
  document.getElementById('rfid_modal_title').textContent = title;
  document.getElementById('rfid_modal').classList.add('show-modal');
}
function closeEditModal(){ document.getElementById('rfid_modal').classList.remove('show-modal'); }
function openScanModal(){ document.getElementById('scan_backdrop').classList.add('show-modal'); }
function closeScanModal(){
  document.getElementById('scan_backdrop').classList.remove('show-modal');
  if(window.ENROLL_TIMER){ clearInterval(window.ENROLL_TIMER); window.ENROLL_TIMER=null; }
  if(window.ENROLL_SESSION){
    fetch('/rfid/enroll/stop', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({session_id: window.ENROLL_SESSION})});
    window.ENROLL_SESSION=null;
  }
}
function openLogModal(it){
  document.getElementById('lg_uid').textContent = it.uid || '-';
  document.getElementById('lg_owner').textContent = it.owner || '-';
  document.getElementById('lg_device').textContent = it.device || '-';
  document.getElementById('lg_result').textContent = (it.result||'-').toUpperCase();
  const t=new Date(it.timestamp);
  document.getElementById('lg_time').textContent = t.toLocaleString();
  document.getElementById('log_backdrop').classList.add('show-modal');
}
function closeLogModal(){ document.getElementById('log_backdrop').classList.remove('show-modal'); }

/* --- Enroll Mode --- */
window.ENROLL_SESSION = null;
window.ENROLL_TIMER = null;
let COUNT_TIMER = null;

async function startAddRfid(){
  openScanModal();
  let expiresAt = null;
  try{
    const rs = await fetch('/rfid/enroll/start', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ device_id:'rfid_gate_01', ttl_sec:60 })
    });
    const js = await rs.json();
    if(!js.ok){ document.getElementById('scan_status').textContent='Không tạo được phiên enroll'; return; }
    window.ENROLL_SESSION = js.session_id;
    expiresAt = new Date(js.expires_at).getTime();
  }catch(e){
    document.getElementById('scan_status').textContent='Lỗi mạng';
    return;
  }
  const st = document.getElementById('scan_status');
  if(COUNT_TIMER) clearInterval(COUNT_TIMER);
  COUNT_TIMER = setInterval(()=>{
    const left = Math.max(0, Math.floor((expiresAt - Date.now())/1000));
    st.innerHTML = `<span class="spinner"></span>Đang chờ bạn quét thẻ… (còn ${left}s)`;
    if(left<=0){ clearInterval(COUNT_TIMER); }
  }, 1000);

  if(window.ENROLL_TIMER) clearInterval(window.ENROLL_TIMER);
  window.ENROLL_TIMER = setInterval(pollEnrollOnce, 600);
}

async function pollEnrollOnce(){
  if(!window.ENROLL_SESSION) return;
  try{
    const r = await fetch('/rfid/enroll/poll?session_id='+encodeURIComponent(window.ENROLL_SESSION));
    const js = await r.json();
    if(!js.ok){
      closeScanModal();
      alert('Phiên enroll hết hạn hoặc lỗi, thử lại.');
      return;
    }
    if(js.captured){
      const { uid, exists } = js.captured;
      closeScanModal();
      if(COUNT_TIMER) clearInterval(COUNT_TIMER);
      if(window.ENROLL_TIMER){ clearInterval(window.ENROLL_TIMER); window.ENROLL_TIMER=null; }

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
      fetch('/rfid/enroll/stop', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({session_id: window.ENROLL_SESSION})});
      window.ENROLL_SESSION = null;
    }
  }catch(e){ /* ignore */ }
}

/* --- CRUD --- */
async function openEditForUid(uid){
  try{
    const r = await fetch('/rfid/'+encodeURIComponent(uid));
    const js = await r.json();
    if(!js.ok){ alert('Không tìm thấy thẻ'); return; }
    const c = js.card;
    RFID_IS_ADDING = false; RFID_SELECTED = uid;
    document.getElementById('f_uid').readOnly = true;
    document.getElementById('f_uid').value = c.uid;
    document.getElementById('f_owner').value = c.owner || '';
    document.getElementById('f_type').value  = c.card_type || 'MIFARE Classic';
    document.getElementById('f_desc').value  = c.description || '';
    document.getElementById('f_expires').value = c.expires_at || '';
    document.getElementById('f_active').checked = !!c.active;
    document.getElementById('rfid_hint').textContent = `Đăng ký: ${c.registered_at||'-'} • Lần dùng: ${c.last_used||'-'}`;
    openEditModal('Sửa thẻ RFID');
    loadRfidLogs(uid);
  }catch(e){ alert('RFID: lỗi mạng'); }
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
  if(!uid){ alert('Thiếu UID'); return; }

  try{
    if(RFID_IS_ADDING){
      const r = await fetch('/rfid/add', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ uid, ...body }) });
      const js = await r.json();
      if(js.ok){
        alert('Đã thêm thẻ thành công. Vui lòng quét lại thẻ để vào.');
        RFID_IS_ADDING = false; RFID_SELECTED = uid;
        closeEditModal();
        await loadRfid();
        await loadRfidLogs(uid);
      }else{
        alert('Thêm thẻ thất bại: ' + (js.error || ''));
      }
    }else{
      const r = await fetch('/rfid/'+encodeURIComponent(uid), { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) });
      const js = await r.json();
      if(js.ok){
        alert('Đã lưu thay đổi thẻ.');
        closeEditModal();
        await loadRfid();
        await loadRfidLogs(uid);
      }else{
        alert('Lưu thất bại: ' + (js.error || ''));
      }
    }
  }catch(e){ alert('RFID: lỗi mạng'); }
}

async function deleteByUid(uid){
  if(!confirm('Xoá thẻ '+uid+' ?')) return;
  try{
    const r = await fetch('/rfid/'+encodeURIComponent(uid), { method:'DELETE' });
    const js = await r.json();
    if(js.ok){
      alert('Đã xoá thẻ.');
      RFID_SELECTED = null;
      await loadRfid();
      document.getElementById('rfid_logs').innerHTML = '<div class="item i-gray">Chưa có lịch sử</div>';
    }else{
      alert('Xoá thất bại: '+(js.error||''));
    }
  }catch(e){ alert('RFID: lỗi mạng'); }
}
async function deleteRfid(){
  const uid = (document.getElementById('f_uid').value || '').trim();
  if(!uid){ alert('Chưa chọn thẻ'); return; }
  await deleteByUid(uid);
  closeEditModal();
}

/* --- Logs --- */
async function loadRfidLogs(uid){
  try{
    const r = await fetch('/rfid/logs?uid='+encodeURIComponent(uid));
    if(!r.ok){ return; }
    const arr = await r.json();
    const box = document.getElementById('rfid_logs');
    box.innerHTML = '';
    if(!arr.length){ box.innerHTML = '<div class="item i-gray">Chưa có lượt vào/ra</div>'; return; }
    for(const it of arr){
      const div = document.createElement('div');
      const cls = (it.result==='granted') ? 'i-green' : 'i-orange';
      div.className = 'item '+cls;
      const t = new Date(it.timestamp);
      const hh = t.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
      div.textContent = `[${hh}] ${it.result.toUpperCase()} (${it.device}, uid=${it.uid})`;
      div.style.cursor='pointer';
      div.onclick = ()=> openLogModal(it);
      box.appendChild(div);
    }
    box.scrollTop = 0;
  }catch(e){}
}

/* ===== Init ===== */
document.addEventListener('DOMContentLoaded', ()=>{
  loadFan(); loadFeed(); loadRfid();
});
