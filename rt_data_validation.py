import re
import argparse
import sys
import os
import csv
import xml.etree.ElementTree as ET
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Use 'Agg' backend for matplotlib to support headless environments (servers)
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

EXPECTED_ACTIVATIONS = {
    "1min": {0: (1, 0), 30: (0, 3), 40: (0, 2), 50: (0, 1), 55: (0, 1), 
             56: (0, 1), 57: (0, 1), 58: (0, 1), 59: (0, 1), 60: (1, 0)},
    "2min": {0: (2, 0), 30: (1, 3), 60: (1, 0), 90: (0, 3), 100: (0, 2), 
             110: (0, 1), 115: (0, 1), 116: (0, 1), 117: (0, 1), 118: (0, 1), 
             119: (0, 1), 120: (1, 0)},
    "3min": {0: (3, 0), 60: (2, 0), 90: (1, 3), 120: (1, 0), 150: (0, 3), 
             160: (0, 2), 170: (0, 1), 175: (0, 1), 176: (0, 1), 177: (0, 1), 
             178: (0, 1), 179: (0, 1), 180: (1, 0)},
    "5min": {0: (1, 0), 60: (1, 0), 240: (1, 0), 300: (1, 0)}
}

DURATION_MAP = {"1min": 60, "2min": 120, "3min": 180, "5min": 300}

@dataclass
class SutBuzzerEvent:
    elapsed: int
    long_count: int
    short_count: int
    timestamp: datetime
    line_num: int

@dataclass
class TestIteration:
    sequence_label: str
    start_time: datetime
    start_line: int
    end_time: Optional[datetime] = None
    end_line: Optional[int] = None
    buzzer_events: List[SutBuzzerEvent] = field(default_factory=list)
    label_mismatches: List[str] = field(default_factory=list)

# ---------------------------------------------------------------------
# PARSING LOGIC
# ---------------------------------------------------------------------

def parse_log_line(line: str) -> Tuple[Optional[datetime], Optional[ET.Element]]:
    ts_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.(\d{3,6})\]', line)
    xml_match = re.search(r'(<testcase.*?>)', line)
    if ts_match and xml_match:
        # Construct timestamp with microseconds
        ts_str = f"{ts_match.group(1)}.{ts_match.group(2)}"
        ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S.%f')
        try:
            node = ET.fromstring(xml_match.group(0))
            return ts, node
        except ET.ParseError: return None, None
    return None, None

def parse_test_log(path: str):
    plan = []
    if not os.path.exists(path): return plan
    with open(path, 'r') as f:
        for i, line in enumerate(f, 1):
            _, node = parse_log_line(line)
            if node is not None and node.get("classname") == "TestStart":
                seq = node.get("testsequence")
                iteration = node.get("iteration", "?")
                plan.append({
                    "label": f"{seq}min", 
                    "line": i, 
                    "iteration": iteration,
                    "testsequence": seq
                })
    return plan

def parse_sut_log(path: str) -> List[TestIteration]:
    all_iterations = []
    current_iter = None
    if not os.path.exists(path): return all_iterations
    with open(path, 'r') as f:
        for i, line in enumerate(f, 1):
            ts, node = parse_log_line(line)
            if node is None: continue
            cls, lbl = node.get("classname"), node.get("whichtest")
            
            if cls == "StartEvent":
                current_iter = TestIteration(sequence_label=lbl, start_time=ts, start_line=i)
            elif cls == "BuzzerEvent" and current_iter:
                current_iter.buzzer_events.append(SutBuzzerEvent(
                    elapsed=int(node.get("elapsed", 0)), 
                    long_count=int(node.get("longcount", 0)),
                    short_count=int(node.get("shortcount", 0)), 
                    timestamp=ts, line_num=i
                ))
            elif cls == "EndEvent" and current_iter:
                current_iter.end_time = ts
                current_iter.end_line = i
                all_iterations.append(current_iter)
                current_iter = None
    return all_iterations

# ---------------------------------------------------------------------
# VALIDATION & ANALYSIS
# ---------------------------------------------------------------------

def run_validation(test_path, sut_path):
    plan = parse_test_log(test_path)
    sut_results = parse_sut_log(sut_path)
    report = {
        "errors": [], 
        "status": {"alignment": True, "count": True, "buzzer": True, "duration": True},
        "drift_records": []
    }

    if len(plan) != len(sut_results):
        report["status"]["count"] = False
        report["errors"].append(f"Count mismatch: TEST expected {len(plan)}, SUT has {len(sut_results)}")

    for i, p_item in enumerate(plan):
        if i >= len(sut_results): break
        sut = sut_results[i]
        
        # Duration Check
        expected_dur = DURATION_MAP.get(sut.sequence_label, 0)
        iter_label = f"Iter {p_item['iteration']} [{sut.sequence_label}]"
        
        if sut.end_time:
            actual_dur = (sut.end_time - sut.start_time).total_seconds()
            if abs(actual_dur - expected_dur) > 1.5:
                report["status"]["duration"] = False
                report["errors"].append(f"{iter_label}: Duration mismatch. Expected {expected_dur}s, got {actual_dur:.2f}s")

        # Buzzer Drift and Logic Check
        exp_table = EXPECTED_ACTIVATIONS.get(sut.sequence_label, {})
        act_map = {b.elapsed: b for b in sut.buzzer_events}

        for sec, (e_long, e_short) in exp_table.items():
            if sec not in act_map:
                report["status"]["buzzer"] = False
                report["errors"].append(f"{iter_label} [Line {sut.start_line}]: Missing buzzer @ {sec}s")
                continue
            
            b = act_map[sec]
            drift_ms = (b.timestamp.timestamp() - (sut.start_time.timestamp() + sec)) * 1000
            report["drift_records"].append({
                "iteration": p_item['iteration'],
                "label": sut.sequence_label,
                "sec": sec,
                "drift_ms": round(drift_ms, 3)
            })

            if (b.long_count != e_long) or (b.short_count != e_short):
                report["status"]["buzzer"] = False
                report["errors"].append(f"{iter_label} [Line {b.line_num}]: Logic Error. Expected L:{e_long} S:{e_short}")

    return report

# ---------------------------------------------------------------------
# OUTPUTS
# ---------------------------------------------------------------------

def print_stats(drift_records):
    if not drift_records: return
    drifts = [r['drift_ms'] for r in drift_records]
    print("\n" + "-"*40 + "\nTIMING STATISTICS (ms)\n" + "-"*40)
    print(f"Mean (Average) : {statistics.mean(drifts):>8.3f} ms")
    print(f"Std Deviation  : {statistics.stdev(drifts):>8.3f} ms")
    print(f"Max Drift      : {max(drifts):>8.3f} ms")
    print(f"Min Drift      : {min(drifts):>8.3f} ms")
    print("-"*40)

def generate_plot(drift_records):
    if not drift_records: return
    drifts = [r['drift_ms'] for r in drift_records]
    plt.figure(figsize=(10, 5))
    plt.plot(drifts, marker='o', color='tab:blue', label='Drift per event')
    plt.axhline(0, color='red', linestyle='--')
    plt.title("Buzzer Timing Drift Over Test Run")
    plt.ylabel("Drift (ms)")
    plt.xlabel("Buzzer Event Index")
    plt.grid(True, alpha=0.3)
    plt.savefig("drift_analysis.png")
    print("📈 Plot saved as 'drift_analysis.png'")

def main():
    parser = argparse.ArgumentParser(description="Data Validation Script")
    parser.add_argument("--test", required=True, help="Test plan log")
    parser.add_argument("--sut", required=True, help="SUT execution log")
    parser.add_argument("--csv", default="drift_results.csv", help="CSV output filename")
    args = parser.parse_args()

    results = run_validation(args.test, args.sut)

    # Console Summary
    print(f"\nVALIDATION REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for key, val in results["status"].items():
        print(f"{key.capitalize():<12}: {'PASS' if val else 'FAIL'}")

    if results["errors"]:
        print("\nERRORS FOUND:")
        for err in results["errors"]: print(f"  - {err}")

    # Statistics & Visualization
    print_stats(results["drift_records"])
    generate_plot(results["drift_records"])

    # CSV Export
    if results["drift_records"]:
        with open(args.csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results["drift_records"][0].keys())
            writer.writeheader()
            writer.writerows(results["drift_records"])
        print(f"📄 Data exported to {args.csv}")

if __name__ == "__main__":
    main()