# Experiment Results

## Overview

30 controlled failover trials across 6 experimental conditions.
Each condition tested 5 repetitions to enable statistical analysis.

## Experimental Design

**Failure types tested:**
- VM Failure — Azure instance stopped via CLI (infrastructure-level)
- App Failure — Docker container stopped while VM continues running (application-level)

**Health check configurations:**
- Config A (Aggressive): 5s interval, 3s timeout, 2 failures to trigger
- Config B (Balanced): 15s interval, 5s timeout, 3 failures to trigger
- Config C (Conservative): 30s interval, 10s timeout, 5 failures to trigger

## Results Summary

| Configuration | Failure Type | Mean Detection (s) | Std Dev (s) | Min (s) | Max (s) |
|--------------|-------------|-------------------|-------------|---------|---------|
| A (Aggressive) | VM Failure  | 10.447 | 0.631 | 9.762  | 11.125  |
| A (Aggressive) | App Failure | 10.593 | 0.426 | 10.039 | 11.212  |
| B (Balanced)   | VM Failure  | 42.328 | 0.226 | 42.016 | 42.603  |
| B (Balanced)   | App Failure | 38.725 | 0.482 | 37.986 | 39.278  |
| C (Conservative)| VM Failure | 163.681| 0.562 | 163.331| 164.671 |
| C (Conservative)| App Failure| 131.914| 1.844 | 130.359| 134.373 |

## Key Findings

1. **Health check configuration is the primary determinant of RTO.** Config A (10s) 
   is 4x faster than Config B (42s), which is 4x faster than Config C (163s).

2. **App failures are detected faster than VM failures** under conservative configs.
   Config C shows a 31.8s gap — explained by TCP timeout behaviour under VM failure.

3. **Automated failover outperforms manual across all conditions.** Config C (slowest)
   still beats manual baseline (~240s) by 31.8%.

4. **Results are highly consistent.** Standard deviation below 2s across all conditions.

## Raw Data

See `results/all_results.csv` for all 30 trial records with timestamps.
