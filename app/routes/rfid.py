# app/routes/rfid.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import os

from ..utils.storage import load_json, save_json, CONFIG_PATH, LOGS_PATH
from ..utils.helpers import now_iso, parse_iso, is_today

rfid_bp = Blueprint("rfid", __name__, url_prefix="/rfid")

ENROLL_PATH = "app/data/enroll.json"


# ====== Helpers ======
def _ensure_parent(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _get_cfg():
    return load_json(CONFIG_PATH, default={
        "passwords": {},
        "rfid_cards": {},
        "devices": {},
        "access_rules": {},
        "system_info": {}
    })


def _save_cfg(cfg):
    save_json(CONFIG_PATH, cfg)


def _load_enroll():
    _ensure_parent(ENROLL_PATH)
    return load_json(ENROLL_PATH, default={"sessions": {}})


def _save_enroll(d):
    _ensure_parent(ENROLL_PATH)
    save_json(ENROLL_PATH, d)


# ====== RFID CRUD ======
@rfid_bp.get("/list")
def rfid_list():
    cfg = _get_cfg()
    cards = cfg.get("rfid_cards", {})
    items = []
    for uid, c in cards.items():
        it = dict(c)
        it["uid"] = uid
        items.append(it)
    items.sort(key=lambda x: (not x.get("active", False), (x.get("owner") or "").lower()))
    return jsonify(items), 200


@rfid_bp.get("/<uid>")
def rfid_get(uid):
    cfg = _get_cfg()
    card = cfg.get("rfid_cards", {}).get(uid)
    if not card:
        return jsonify({"ok": False, "error": "not_found"}), 404
    out = dict(card)
    out["uid"] = uid
    return jsonify({"ok": True, "card": out}), 200


@rfid_bp.post("/add")
def rfid_add():
    data = request.get_json(silent=True) or {}
    uid = (data.get("uid") or "").strip()
    if not uid:
        return jsonify({"ok": False, "error": "missing_uid"}), 400

    cfg = _get_cfg()
    cards = cfg.setdefault("rfid_cards", {})
    if uid in cards:
        return jsonify({"ok": False, "error": "uid_exists"}), 409

    cards[uid] = {
        "active": bool(data.get("active", True)),
        "owner": data.get("owner") or "",
        "card_type": data.get("card_type") or "MIFARE Classic",
        "description": data.get("description") or "",
        "registered_at": now_iso(),
        "last_used": None,
        "expires_at": data.get("expires_at")
    }
    _save_cfg(cfg)
    return jsonify({"ok": True, "uid": uid}), 201


@rfid_bp.put("/<uid>")
def rfid_update(uid):
    data = request.get_json(silent=True) or {}
    cfg = _get_cfg()
    cards = cfg.setdefault("rfid_cards", {})
    card = cards.get(uid)
    if not card:
        return jsonify({"ok": False, "error": "not_found"}), 404

    for k in ("owner", "description", "card_type", "expires_at"):
        if k in data:
            card[k] = data[k]
    if "active" in data:
        card["active"] = bool(data["active"])

    _save_cfg(cfg)
    return jsonify({"ok": True}), 200


@rfid_bp.delete("/<uid>")
def rfid_delete(uid):
    cfg = _get_cfg()
    cards = cfg.setdefault("rfid_cards", {})
    if uid not in cards:
        return jsonify({"ok": False, "error": "not_found"}), 404
    del cards[uid]
    _save_cfg(cfg)
    return jsonify({"ok": True}), 200


# ====== RFID Logs ======
@rfid_bp.get("/logs")
def rfid_logs():
    uid = (request.args.get("uid") or "").strip()
    only_today = request.args.get("today") in ("1", "true", "yes")

    cfg_cards = _get_cfg().get("rfid_cards", {})
    logs = load_json(LOGS_PATH, default=[])
    items = []
    for e in logs:
        if e.get("type") != "access_attempt" or e.get("method") != "rfid":
            continue
        if uid and e.get("uid") != uid:
            continue
        ts = parse_iso(e.get("timestamp", ""))
        if only_today and not is_today(ts):
            continue
        this_uid = e.get("uid")
        items.append({
            "timestamp": ts.isoformat(),
            "uid": this_uid,
            "owner": (cfg_cards.get(this_uid) or {}).get("owner"),
            "device": e.get("device") or e.get("device_id"),
            "result": e.get("result"),
            "deny_reason": e.get("deny_reason")
        })
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify(items), 200


# ====== Disable old /scan/latest ======
@rfid_bp.get("/scan/latest")
def legacy_scan_latest():
    return jsonify({"ok": False, "error": "legacy_endpoint_disabled"}), 410


# ====== Enroll Mode (robust) ======
@rfid_bp.post("/enroll/start")
def rfid_enroll_start():
    data = request.get_json(silent=True) or {}
    device_id = (data.get("device_id") or "rfid_gate_01").strip()
    ttl = int(data.get("ttl_sec") or 60)
    now = datetime.now(timezone.utc)

    sid = uuid4().hex
    d = _load_enroll()
    d.setdefault("sessions", {})[sid] = {
        "device_id": device_id,
        "started_at": now_iso(),
        "expires_at": (now + timedelta(seconds=ttl)).isoformat(),
        "captured": None
    }
    _save_enroll(d)
    return jsonify({
        "ok": True,
        "session_id": sid,
        "device_id": device_id,
        "started_at": d["sessions"][sid]["started_at"],
        "expires_at": d["sessions"][sid]["expires_at"]
    }), 200


@rfid_bp.get("/enroll/poll")
def rfid_enroll_poll():
    sid = (request.args.get("session_id") or "").strip()
    if not sid:
        return jsonify({"ok": False, "error": "missing_session"}), 400

    d = _load_enroll()
    s = d.get("sessions", {}).get(sid)
    if not s:
        return jsonify({"ok": False, "error": "unknown_session"}), 404

    now = datetime.now(timezone.utc)
    try:
        exp = parse_iso(s["expires_at"])
    except Exception:
        exp = now
    if now > exp:
        return jsonify({"ok": False, "error": "expired"}), 410

    if s.get("captured"):
        return jsonify({"ok": True, "captured": s["captured"]}), 200

    # Lọc logs mới hơn started_at
    try:
        since = parse_iso(s["started_at"])
    except Exception:
        since = now
    device_id = s.get("device_id")
    logs = load_json(LOGS_PATH, default=[])

    found = None
    for e in reversed(logs):
        if e.get("type") != "access_attempt" or e.get("method") != "rfid":
            continue
        dev = e.get("device") or e.get("device_id")
        if device_id and dev != device_id:
            continue
        try:
            ts = parse_iso(e.get("timestamp", ""))
        except Exception:
            continue
        if ts <= since:
            continue
        found = {
            "uid": e.get("uid"),
            "device": dev,
            "result": e.get("result"),
            "timestamp": ts.isoformat()
        }
        break

    if not found:
        return jsonify({"ok": True, "captured": None}), 200

    # Kiểm tra tồn tại trong config
    cfg = load_json(CONFIG_PATH, default={})
    exists = (cfg.get("rfid_cards", {}) or {}).get(found["uid"]) is not None
    found["exists"] = exists

    s["captured"] = found
    _save_enroll(d)
    return jsonify({"ok": True, "captured": found}), 200


@rfid_bp.post("/enroll/stop")
def rfid_enroll_stop():
    data = request.get_json(silent=True) or {}
    sid = (data.get("session_id") or "").strip()
    if not sid:
        return jsonify({"ok": False, "error": "missing_session"}), 400
    d = _load_enroll()
    d.get("sessions", {}).pop(sid, None)
    _save_enroll(d)
    return jsonify({"ok": True}), 200
