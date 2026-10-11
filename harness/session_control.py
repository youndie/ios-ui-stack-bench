#!/usr/bin/env python3
"""The session runner's decisions on summaries whose answer is known (B-25). `make check` runs it.

    python3 harness/session_control.py [-v]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import session  # noqa: E402

ok = {"valid": 1, "reason": "", "low_power": 0, "battery": 0.9, "thermal_worst": "nominal"}
CASES = [
    ("a clean run on a device counts", session.decide(ok, "device")[0] == "count"),
    ("Low Power Mode stops the session", session.decide({**ok, "low_power": 1}, "device")[0] == "stop"),
    ("a battery under 50 % on a device stops the session", session.decide({**ok, "battery": 0.42}, "device")[0] == "stop"),
    ("an unknown battery stops a device session", session.decide({**ok, "battery": ""}, "device")[0] == "stop"),
    ("a simulator's unknown battery (-1) does not stop", session.decide({**ok, "battery": -1}, "simulator")[0] == "count"),
    ("an invalid run is repeated", session.decide({**ok, "valid": 0, "reason": "39 begin"}, "device")[0] == "repeat"),
    ("a run that reached 'fair' is repeated", session.decide({**ok, "thermal_worst": "fair"}, "device")[0] == "repeat"),
    ("rotation: run 0 A,B,C; run 1 B,C,A; run 2 C,A,B; run 3 A,B,C",
     [session.rotation(["A", "B", "C"], r) for r in range(4)] == [["A", "B", "C"], ["B", "C", "A"], ["C", "A", "B"], ["A", "B", "C"]]),
]


def main():
    failed = 0
    for name, result in CASES:
        failed += not result
        if "-v" in sys.argv[1:] or not result:
            print(f"  {'ok  ' if result else 'FAIL'} {name}")
    print(f"control for session.py: {len(CASES) - failed}/{len(CASES)} cases behave")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
