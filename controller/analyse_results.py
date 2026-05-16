import csv, os, statistics

def analyse():
    f = "logs/all_results.csv"
    if not os.path.exists(f):
        print("No results file found. Run trials first.")
        return
    trials = []
    with open(f) as fp:
        for row in csv.DictReader(fp):
            if row.get("detection_latency_s") and row["detection_latency_s"] != "N/A":
                row["detection_latency_s"] = float(row["detection_latency_s"])
                trials.append(row)
    if not trials:
        print("No completed trials found.")
        return
    conditions = {}
    for t in trials:
        k = (t["config"], t["failure_type"])
        conditions.setdefault(k, []).append(t["detection_latency_s"])
    print("\n" + "="*80)
    print("DETECTION LATENCY SUMMARY (seconds)")
    print("="*80)
    print(f"{'Config':<8} {'Failure Type':<16} {'N':<5} {'Mean':<10} {'StdDev':<10} {'Min':<10} {'Max':<10}")
    print("-"*80)
    for (cfg, ft), lats in sorted(conditions.items()):
        n = len(lats)
        mean  = statistics.mean(lats)
        stdev = statistics.stdev(lats) if n > 1 else 0.0
        print(f"{cfg:<8} {ft:<16} {n:<5} {mean:<10.3f} {stdev:<10.3f} {min(lats):<10.3f} {max(lats):<10.3f}")
    print("\nIndividual trials:")
    for t in sorted(trials, key=lambda x:(x["config"],x["failure_type"],x["trial_id"])):
        print(f"  {t['trial_id']:<20} {t['config']:<6} {t['failure_type']:<16} {t['detection_latency_s']:.3f}s")
    with open("logs/graph_data.csv","w",newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["config","failure_type","trial_id","detection_latency_s"])
        for t in trials:
            w.writerow([t["config"],t["failure_type"],t["trial_id"],t["detection_latency_s"]])
    print("\nGraph data exported to logs/graph_data.csv")

if __name__ == "__main__":
    analyse()
