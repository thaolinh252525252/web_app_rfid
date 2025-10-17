from flask import Blueprint, request, jsonify
from ..utils.storage import load_json, CONFIG_PATH
from ..utils.helpers import now_iso, append_log, sha256_hex

access_bp = Blueprint("access", __name__, url_prefix="/access")

@access_bp.post("/passcode")
def access_by_passcode():
    data = request.get_json(silent=True) or {}
    passcode   = (data.get("passcode") or "").strip()
    device_id  = (data.get("device_id") or "").strip()
    explicit_pid = data.get("password_id")

    if not passcode:
        return jsonify({"ok": False, "error": "empty_passcode"}), 400
    if not device_id:
        return jsonify({"ok": False, "error": "missing_device_id"}), 400

    # ĐỌC FILE MỖI LẦN
    cfg     = load_json(CONFIG_PATH, default={"passwords": {}, "rfid_cards": {}, "devices": {}, "access_rules": {}, "system_info": {}})
    devices = cfg.get("devices", {})
    users   = cfg.get("passwords", {})

    result="denied"; reason=None; auth_mode=None; matched_pid=None

    # 1) ƯU TIÊN PIN THIẾT BỊ
    dev = devices.get(device_id)
    if dev and "password" in dev:
        dev_pin = str(dev.get("password"))
        if passcode == dev_pin:
            result="granted"; auth_mode="device_pin"; reason=None
        else:
            reason="device_pin_mismatch"  # sẽ thử fallback

    # 2) FALLBACK HASH NGƯỜI DÙNG (nếu chưa granted)
    if result != "granted":
        phash = sha256_hex(passcode)
        if explicit_pid:
            p = users.get(explicit_pid)
            if p and p.get("active", False) and p.get("hash") == phash:
                matched_pid = explicit_pid; result="granted"; auth_mode="user_hash"; reason=None
        else:
            for pid, p in users.items():
                if p.get("active", False) and p.get("hash") == phash:
                    matched_pid = pid; result="granted"; auth_mode="user_hash"; reason=None
                    break
        if result != "granted" and reason is None:
            reason = "invalid_hash"

    append_log({
        "type":"access_attempt","method":"passkey","device_id":device_id,
        "password_id":matched_pid,"result":result,"deny_reason":reason,
        "auth_mode":auth_mode,"timestamp":now_iso()
    })

    return jsonify({
        "ok": result=="granted","result":result,"auth_mode":auth_mode,
        "password_id":matched_pid,"deny_reason":reason,"device_id":device_id,
        "executed_at":now_iso()
    }), 200
