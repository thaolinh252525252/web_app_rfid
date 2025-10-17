# app/routes/notify.py
from flask import Blueprint, jsonify
from ..utils.helpers import parse_iso, is_today
from ..utils.storage import load_json, LOGS_PATH   # <- đọc file tươi mỗi lần

notify_bp = Blueprint("notify", __name__, url_prefix="/notify")

@notify_bp.get("/today")
def notify_today():
    logs = load_json(LOGS_PATH, default=[])   # <- luôn lấy bản mới
    items = []

    for e in logs:
        ts = parse_iso(e.get("timestamp", ""))
        if not is_today(ts):
            continue

        typ = (e.get("type") or "").lower()
        color = "gray"
        text = ""

        if typ == "alert":
            dev = e.get("device_id") or e.get("device") or "?"
            evt = e.get("event", "")
            temp = e.get("temperature")
            temp_str = f" ({temp}°C)" if temp is not None else ""
            text = f"[{ts.strftime('%H:%M:%S')}] ALERT {dev}: {evt}{temp_str}"
            color = "red"

        elif typ == "access_attempt":
            method = e.get("method", "-")
            result = e.get("result", "-")
            dev = e.get("device") or e.get("device_id") or "?"
            who = e.get("uid") or e.get("password_id") or "-"
            mode = e.get("auth_mode") or "-"
            text = f"[{ts.strftime('%H:%M:%S')}] ACCESS {method} {result} ({dev}, id={who}, mode={mode})"
            color = "green" if result == "granted" else "orange"

        elif typ == "control":
            dev = e.get("device_id") or "?"
            cmd = e.get("command") or e.get("state") or "-"
            text = f"[{ts.strftime('%H:%M:%S')}] CONTROL {dev} \u2192 {cmd}"
            color = "blue"

        elif typ == "door_status":
            dev = e.get("device") or e.get("device_id") or "?"
            stat = e.get("status", "-")
            seq = e.get("sequence")
            seq_str = f" (seq={seq})" if seq is not None else ""
            text = f"[{ts.strftime('%H:%M:%S')}] DOOR {dev} {stat}{seq_str}"
            color = "gray"

        elif typ == "system_event":
            evt = e.get("event", "-")
            text = f"[{ts.strftime('%H:%M:%S')}] SYSTEM {evt}"
            color = "gray"

        else:
            text = f"[{ts.strftime('%H:%M:%S')}] {typ or 'event'}"
            color = "gray"

        items.append({"ts": ts.isoformat(), "text": text, "color": color})

    items.sort(key=lambda x: x["ts"], reverse=True)
    return jsonify(items), 200
