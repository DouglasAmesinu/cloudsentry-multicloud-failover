import threading, time, logging, csv, os, json
from datetime import datetime
from collections import deque
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import CONFIGS, AZURE_IP, AWS_IP, AZURE_HEALTH_URL, AWS_HEALTH_URL, CF_API_TOKEN, CF_ZONE_ID, CF_RECORD_ID, DOMAIN
from health_checker import check_health
from cloudflare import update_dns

app = Flask(__name__)
CORS(app)

state = {
    "system_state": "PRIMARY_HEALTHY",
    "azure_healthy": True, "aws_healthy": True,
    "consecutive_failures": 0,
    "t_failure": None, "t_dns_updated": None, "t_recovery": None,
    "detection_latency": None, "failover_count": 0,
    "active_config": "B", "dns_current_ip": AZURE_IP,
    "uptime_start": datetime.now().isoformat(),
    "last_check": None, "total_checks": 0, "auto_failover": True,
}
log_buffer = deque(maxlen=200)
state_lock = threading.Lock()

class BufferHandler(logging.Handler):
    def emit(self, record):
        log_buffer.appendleft({"time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "level": record.levelname, "message": record.getMessage(), "ts": time.time()})

logger = logging.getLogger("failover")
logger.setLevel(logging.DEBUG)
logger.addHandler(BufferHandler())
logger.addHandler(logging.StreamHandler())

def controller_loop():
    logger.info("=" * 55)
    logger.info(f"CloudSentry controller started")
    logger.info(f"Azure: {AZURE_HEALTH_URL}")
    logger.info(f"AWS:   {AWS_HEALTH_URL}")
    logger.info("=" * 55)
    while True:
        with state_lock:
            cfg = CONFIGS[state["active_config"]]
            cur = state["system_state"]
            auto = state["auto_failover"]
        azure_ok = check_health(AZURE_HEALTH_URL, cfg["timeout"])
        aws_ok   = check_health(AWS_HEALTH_URL,   cfg["timeout"])
        with state_lock:
            state["azure_healthy"] = azure_ok
            state["aws_healthy"]   = aws_ok
            state["last_check"]    = datetime.now().isoformat()
            state["total_checks"] += 1
        logger.info(f"Azure:{'OK  ' if azure_ok else 'FAIL'} | AWS:{'OK  ' if aws_ok else 'FAIL'} | Failures:{state['consecutive_failures']} | {cur}")
        if cur == "PRIMARY_HEALTHY":
            if not azure_ok:
                with state_lock:
                    state["consecutive_failures"] += 1
                    if state["consecutive_failures"] == 1:
                        state["t_failure"] = datetime.now().isoformat()
                        logger.warning(f"T_FAILURE: {state['t_failure']}")
                logger.warning(f"Azure FAILED ({state['consecutive_failures']}/{cfg['failure_threshold']})")
                if state["consecutive_failures"] >= cfg["failure_threshold"]:
                    logger.critical("Threshold reached - INITIATING FAILOVER")
                    if auto: _execute_failover()
            else:
                with state_lock: state["consecutive_failures"] = 0
        elif cur == "FAILOVER_ACTIVE":
            if azure_ok:
                with state_lock:
                    state["system_state"] = "RECOVERING"
                    state["t_recovery"]   = datetime.now().isoformat()
                logger.info("Azure recovered. STATE: RECOVERING")
        elif cur == "RECOVERING":
            logger.info("RECOVERING - awaiting manual switchback")
        time.sleep(cfg["check_interval"])

def _execute_failover():
    logger.critical(f"Switching DNS: {AZURE_IP} to {AWS_IP}")
    if update_dns(CF_ZONE_ID, CF_RECORD_ID, CF_API_TOKEN, AWS_IP):
        with state_lock:
            state["system_state"] = "FAILOVER_ACTIVE"
            state["consecutive_failures"] = 0
            state["t_dns_updated"]  = datetime.now().isoformat()
            state["dns_current_ip"] = AWS_IP
            state["failover_count"] += 1
            t_f = datetime.fromisoformat(state["t_failure"])
            t_d = datetime.fromisoformat(state["t_dns_updated"])
            state["detection_latency"] = round((t_d - t_f).total_seconds(), 3)
        logger.critical(f"DNS updated to {AWS_IP}")
        logger.critical(f"Detection latency: {state['detection_latency']}s")
    else:
        logger.error("DNS update FAILED - retrying next interval")

@app.route("/api/status")
def api_status():
    with state_lock:
        return jsonify({**state, "azure_ip": AZURE_IP, "aws_ip": AWS_IP,
            "domain": DOMAIN, "config": CONFIGS[state["active_config"]],
            "timestamp": datetime.now().isoformat()})

@app.route("/api/logs")
def api_logs():
    since = float(request.args.get("since", 0))
    entries = [e for e in log_buffer if e["ts"] > since]
    return jsonify({"logs": list(reversed(entries))})

@app.route("/api/results")
def api_results():
    f = "logs/all_results.csv"
    if not os.path.exists(f): return jsonify({"results": []})
    results = []
    with open(f) as fp:
        for row in csv.DictReader(fp):
            if row.get("detection_latency_s") and row["detection_latency_s"] != "N/A":
                results.append({"trial_id": row["trial_id"], "config": row["config"],
                    "failure_type": row["failure_type"],
                    "detection_latency": float(row["detection_latency_s"])})
    return jsonify({"results": results, "count": len(results)})

@app.route("/api/failover", methods=["POST"])
def api_failover():
    with state_lock:
        if state["system_state"] != "PRIMARY_HEALTHY":
            return jsonify({"success": False, "error": "Not in PRIMARY_HEALTHY state"}), 400
    logger.critical("MANUAL FAILOVER triggered via dashboard")
    _execute_failover()
    return jsonify({"success": True})

@app.route("/api/reset", methods=["POST"])
def api_reset():
    if update_dns(CF_ZONE_ID, CF_RECORD_ID, CF_API_TOKEN, AZURE_IP):
        with state_lock:
            state.update({"system_state": "PRIMARY_HEALTHY", "consecutive_failures": 0,
                "t_failure": None, "t_dns_updated": None, "t_recovery": None,
                "detection_latency": None, "dns_current_ip": AZURE_IP})
        logger.info("Reset complete - DNS restored to Azure")
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "DNS update failed"}), 500

@app.route("/api/config", methods=["POST"])
def api_config():
    c = request.get_json().get("config", "B").upper()
    if c not in ("A","B","C"): return jsonify({"success": False}), 400
    with state_lock: state["active_config"] = c
    logger.info(f"Config changed to {c}")
    return jsonify({"success": True, "config": c})

@app.route("/api/auto_failover", methods=["POST"])
def api_auto():
    enabled = request.get_json().get("enabled", True)
    with state_lock: state["auto_failover"] = enabled
    logger.info(f"Auto-failover {'ENABLED' if enabled else 'DISABLED'}")
    return jsonify({"success": True})

if __name__ == "__main__":
    t = threading.Thread(target=controller_loop, daemon=True)
    t.start()
    logger.info("API running at http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False, use_reloader=False)
