import time, logging, csv, os, sys
from datetime import datetime
from enum import Enum
from config import CONFIGS, AZURE_IP, AWS_IP, AZURE_HEALTH_URL, AWS_HEALTH_URL, CF_API_TOKEN, CF_ZONE_ID, CF_RECORD_ID
from cloudflare import update_dns
from health_checker import check_health

class State(Enum):
    PRIMARY_HEALTHY = "PRIMARY_HEALTHY"
    FAILOVER_ACTIVE = "FAILOVER_ACTIVE"
    RECOVERING      = "RECOVERING"

class FailoverController:
    def __init__(self, config_name, trial_id, failure_type):
        self.config       = CONFIGS[config_name]
        self.config_name  = config_name
        self.trial_id     = trial_id
        self.failure_type = failure_type
        self.state        = State.PRIMARY_HEALTHY
        self.consecutive_failures = 0
        self.t_failure = self.t_dns_updated = self.t_recovery_detected = None
        os.makedirs("logs", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/ctrl_{trial_id}_{config_name}_{failure_type}_{ts}.log"
        logging.basicConfig(level=logging.INFO,
            format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler(self.log_file), logging.StreamHandler(sys.stdout)])
        logging.info(f"Trial:{trial_id} Config:{self.config['name']} Type:{failure_type}")

    def run(self):
        logging.info(f"STATE: {self.state.value} - Monitoring started. Ctrl+C to stop.")
        try:
            while True:
                self._tick()
                time.sleep(self.config["check_interval"])
        except KeyboardInterrupt:
            logging.info("Stopped by user")
            self._write_results()

    def _tick(self):
        azure_ok = check_health(AZURE_HEALTH_URL, self.config["timeout"])
        aws_ok   = check_health(AWS_HEALTH_URL,   self.config["timeout"])
        logging.info(f"Azure:{'OK  ' if azure_ok else 'FAIL'} | AWS:{'OK  ' if aws_ok else 'FAIL'} | Failures:{self.consecutive_failures} | {self.state.value}")
        if self.state == State.PRIMARY_HEALTHY:
            if not azure_ok:
                self.consecutive_failures += 1
                if self.consecutive_failures == 1:
                    self.t_failure = datetime.now()
                    logging.warning(f"T_FAILURE recorded: {self.t_failure.isoformat()}")
                logging.warning(f"Azure FAILED ({self.consecutive_failures}/{self.config['failure_threshold']})")
                if self.consecutive_failures >= self.config["failure_threshold"]:
                    logging.critical("Threshold reached - INITIATING FAILOVER")
                    self._execute_failover()
            else:
                self.consecutive_failures = 0
        elif self.state == State.FAILOVER_ACTIVE:
            if azure_ok:
                self.t_recovery_detected = datetime.now()
                self.state = State.RECOVERING
                logging.info(f"Azure recovered. STATE: RECOVERING")
        elif self.state == State.RECOVERING:
            logging.info("RECOVERING - awaiting manual switchback")

    def _execute_failover(self):
        logging.critical(f"Switching DNS: {AZURE_IP} to {AWS_IP}")
        if update_dns(CF_ZONE_ID, CF_RECORD_ID, CF_API_TOKEN, AWS_IP):
            self.t_dns_updated = datetime.now()
            self.state = State.FAILOVER_ACTIVE
            self.consecutive_failures = 0
            latency = round((self.t_dns_updated - self.t_failure).total_seconds(), 3)
            logging.critical(f"T_DNS_UPDATED: {self.t_dns_updated.isoformat()}")
            logging.critical(f"Detection latency: {latency}s")
            logging.critical("STATE: FAILOVER_ACTIVE - Traffic routed to AWS")
        else:
            logging.error("DNS update FAILED - will retry next interval")

    def _write_results(self):
        f = "logs/all_results.csv"
        exists = os.path.exists(f)
        latency = round((self.t_dns_updated - self.t_failure).total_seconds(), 3) if self.t_failure and self.t_dns_updated else None
        with open(f, "a", newline="") as fp:
            w = csv.writer(fp)
            if not exists:
                w.writerow(["trial_id","config","failure_type","t_failure","t_dns_updated","detection_latency_s","t_recovery_detected","log_file"])
            w.writerow([self.trial_id, self.config_name, self.failure_type,
                self.t_failure.isoformat() if self.t_failure else "N/A",
                self.t_dns_updated.isoformat() if self.t_dns_updated else "N/A",
                latency if latency else "N/A",
                self.t_recovery_detected.isoformat() if self.t_recovery_detected else "N/A",
                self.log_file])
        logging.info(f"Results saved to {f}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python controller.py <A|B|C> <trial_id> <vm_failure|app_failure>")
        sys.exit(1)
    c = FailoverController(sys.argv[1].upper(), sys.argv[2], sys.argv[3])
    c.run()
