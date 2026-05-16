# Experiment Results

## Summary â€” 30 Controlled Trials

| Configuration    | Failure Type | Mean (s) | Std Dev (s) | Min (s) | Max (s) |
|-----------------|-------------|----------|-------------|---------|---------|
| A (Aggressive)  | VM Failure  | 10.447   | 0.631       | 9.762   | 11.125  |
| A (Aggressive)  | App Failure | 10.593   | 0.426       | 10.039  | 11.212  |
| B (Balanced)    | VM Failure  | 42.328   | 0.226       | 42.016  | 42.603  |
| B (Balanced)    | App Failure | 38.725   | 0.482       | 37.986  | 39.278  |
| C (Conservative)| VM Failure  | 163.681  | 0.562       | 163.331 | 164.671 |
| C (Conservative)| App Failure | 131.914  | 1.844       | 130.359 | 134.373 |

## Key Findings
1. Detection latency scales predictably with configuration
2. App failures detected faster than VM failures â€” TCP timeout mechanics
3. Automated failover beats manual (~240s) across all conditions
4. 30/30 successful failovers â€” StdDev < 2s across all conditions
