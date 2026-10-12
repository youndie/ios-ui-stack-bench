## The ruler: A against A, by the study's own rules

| Question | Metric | Estimator | A' - A | 95 % interval | Runs | Verdict | Green if |
|---|---|---|---|---|---|---|---|
| RQ2 (A vs A as C) | trace_process_to_list_ms | median difference | -0.81 | (-7.13, 28.86) | 9/10 | green | <= +100 ms |
| RQ4 (A vs A as C) | peak_footprint_bytes | median ratio | 1.00 | (0.99, 1.10) | 4/5 | green | <= 2x |
| RQ5 (A vs A as B1) | hitch_time_ratio_ms_per_s | median difference | 0.00 | (0.00, 0.00) | 4/5 | green | <= +1 ms/s |
| RQ5 (A vs A as B1) | trace_process_to_list_ms | median difference | -0.81 | (-7.13, 28.86) | 9/10 | green | <= +50 ms |
| RQ5 (A vs A as B1) | peak_footprint_bytes | median difference | 65556.00 | (-442368.00, 6225940.00) | 4/5 | green | <= +20 MB |
| RQ3 (A's own level) | hitch_time_ratio_ms_per_s | median | 0.00 | (0.00, 0.00) | 9 | reference | < 5 ms/s for C |

## Kill criterion 5: the app's own figures, idle, with the runner and without

| Metric | With | Without | Shift | 10 % line | Runs | Verdict |
|---|---|---|---|---|---|---|
| cpu_total_ms | 1999.43 ms | 1202.82 ms | 796.61 ms | 120.28 ms | 5/5 | fail - kill criterion 5 |
| peak_footprint_bytes | 27.48 MB | 21.51 MB | 5.96 MB | 2.15 MB | 5/5 | fail - kill criterion 5 |

## The study's own instruments: on minus off

| Metric | On | Off | Shift | Runs | Verdict |
|---|---|---|---|---|---|
| trace_process_to_list_ms | 318.34 | 320.12 | -1.78 ms | 5/5 | inside the ruler |
| trace_hitch_time_ratio_ms_per_s | 17.23 | 22.42 | -5.20 ms/s | 3/3 | reported |

## Thermal drift

The worst thermal state of every ruler attempt, in the session's order: nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal, nominal. Attempts repeated for a thermal state above nominal: 0.
