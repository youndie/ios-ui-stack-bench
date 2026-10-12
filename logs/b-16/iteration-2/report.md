## The ruler: A against A, by the study's own rules

| Question | Metric | Estimator | A' - A | 95 % interval | Runs | Verdict | Green if |
|---|---|---|---|---|---|---|---|
| RQ2 (A vs A as C) | trace_process_to_list_ms | median difference | -10.07 | (-25.18, 17.18) | 9/10 | green | <= +100 ms |
| RQ4 (A vs A as C) | peak_footprint_bytes | median ratio | 0.98 | (0.95, 1.05) | 4/5 | green | <= 2x |
| RQ5 (A vs A as B1) | trace_hitch_time_ratio_ms_per_s | median difference | 1.57 | (-1.22, 6.15) | 4/5 | inconclusive | <= +1 ms/s |
| RQ5 (A vs A as B1) | trace_process_to_list_ms | median difference | -10.07 | (-25.18, 17.18) | 9/10 | green | <= +50 ms |
| RQ5 (A vs A as B1) | peak_footprint_bytes | median difference | -1376256.00 | (-2850816.00, 3014656.00) | 4/5 | green | <= +20 MB |
| RQ3 (A's own level) | trace_hitch_time_ratio_ms_per_s | median | 8.05 | (6.61, 9.42) | 9 | reference | < 5 ms/s for C |

## Kill criterion 5: the app's own figures, idle, with the runner and without

| Metric | With | Without | Shift | 10 % line | Runs | Verdict |
|---|---|---|---|---|---|---|
| cpu_total_ms |  |  |  |  | 0/0 | not measured |
| peak_footprint_bytes |  |  |  |  | 0/0 | not measured |

## The study's own instruments: on minus off

| Metric | On | Off | Shift | Runs | Verdict |
|---|---|---|---|---|---|
| trace_process_to_list_ms | 316.22 | 326.85 | -10.63 ms | 5/5 | inside the ruler |
| trace_hitch_time_ratio_ms_per_s | 10.05 | 7.53 | 2.52 ms/s | 3/3 | reported |

## Thermal drift

The worst thermal state of every ruler attempt, in the session's order: nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal. Attempts repeated for a thermal state above nominal: 0.
