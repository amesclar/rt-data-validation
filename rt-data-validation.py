#!/usr/bin/env python3
import re
import argparse
import sys
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime

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

# ---------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------

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
# PARSING UTILS
# ---------------------------------------------------------------------

def parse_log_line(line: str) -> Tuple[Optional[datetime], Optional[ET.Element]]:
    ts_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.', line)
    xml_match = re.search(r'(<testcase.*?>)', line)
    
    if ts_match and xml_match:
        ts = datetime.strptime(ts_match.group(1), '%Y-%m-%d %H:%M:%S')
        try:
            node = ET.fromstring(xml_match.group(0))
            return ts, node
        except ET.ParseError:
            return None, None
    return None, None

def parse_test_log(path: str):
    plan = []
    with open(path, 'r') as f:
        for i, line in enumerate(f, 1):
            _, node = parse_log_line(line)
            if node is not None and node.get("classname") == "TestStart":
                plan.append({"label": f"{node.get('testsequence')}min", "line": i})
    return plan

def parse_sut_log(path: str) -> List[TestIteration]:
    all_iterations = []
    current_iter = None
    with open(path, 'r') as f:
        for i, line in enumerate(f, 1):
            ts, node = parse_log_line(line)
            if node is None: continue
            cls = node.get("classname")
            lbl = node.get("whichtest")
            
            if cls == "StartEvent":
                current_iter = TestIteration(sequence_label=lbl, start_time=ts, start_line=i)
            elif cls == "BuzzerEvent" and current_iter:
                if lbl != current_iter.sequence_label:
                    current_iter.label_mismatches.append(f"Line {i}: Buzzer label mismatch ({lbl} != {current_iter.sequence_label})")
                current_iter.buzzer_events.append(SutBuzzerEvent(
                    elapsed=int(node.get("elapsed", 0)), long_count=int(node.get("longcount", 0)),
                    short_count=int(node.get("shortcount", 0)), timestamp=ts, line_num=i
                ))
            elif cls == "EndEvent" and current_iter:
                if lbl != current_iter.sequence_label:
                    current_iter.label_mismatches.append(f"Line {i}: End label mismatch ({lbl} != {current_iter.sequence_label})")
                current_iter.end_time = ts
                current_iter.end_line = i
                all_iterations.append(current_iter)
                current_iter = None
    return all_iterations

# ---------------------------------------------------------------------
# VALIDATION ENGINE
# ---------------------------------------------------------------------

def run_validation(test_path, sut_path):
    plan = parse_test_log(test_path)
    sut_results = parse_sut_log(sut_path)
    
    report = {
        "errors": [], 
        "status": {"alignment": True, "count": True, "buzzer": True, "duration": True},
        "test_log": test_path,
        "sut_log": sut_path
    }

    # 1. Alignment & Duration
    for i, sut in enumerate(sut_results):
        if sut.label_mismatches:
            report["status"]["alignment"] = False
            report["errors"].extend([f"Iter {i+1} [SUT Line {sut.start_line}]: {m}" for m in sut.label_mismatches])

        expected_dur = DURATION_MAP.get(sut.sequence_label, 0)
        if sut.end_time:
            actual_dur = (sut.end_time - sut.start_time).total_seconds()
            if abs(actual_dur - expected_dur) > 1.0:
                report["status"]["duration"] = False
                report["errors"].append(f"Iter {i+1} [SUT Line {sut.start_line}-{sut.end_line}]: Duration mismatch. Expected {expected_dur}s, got {actual_dur}s")

    # 2. Sequence & Buzzer
    if len(plan) != len(sut_results):
        report["status"]["count"] = False
        report["errors"].append(f"Count mismatch: TEST log expected {len(plan)} tests, SUT has {len(sut_results)}")

    for i, p_item in enumerate(plan):
        if i >= len(sut_results): break
        sut = sut_results[i]
        
        if sut.sequence_label != p_item["label"]:
            report["errors"].append(f"Iter {i+1} [SUT Line {sut.start_line}]: Sequence mismatch. TEST (Line {p_item['line']}) expected {p_item['label']}, SUT got {sut.sequence_label}")

        exp_table = EXPECTED_ACTIVATIONS.get(sut.sequence_label, {})
        act_map = {b.elapsed: b for b in sut.buzzer_events}

        for sec, (e_long, e_short) in exp_table.items():
            if sec not in act_map:
                report["status"]["buzzer"] = False
                report["errors"].append(f"Iter {i+1} [SUT Line {sut.start_line}]: Missing expected buzzer at {sec}s")
                continue
            
            b = act_map[sec]
            if (b.long_count != e_long) or (b.short_count != e_short):
                report["status"]["buzzer"] = False
                report["errors"].append(f"Iter {i+1} [SUT Line {b.line_num}] @ {sec}s: Expected L:{e_long} S:{e_short}, got L:{b.long_count} S:{b.short_count}")

    return report

# ---------------------------------------------------------------------
# MAIN & REPORTING
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-log", required=True)
    parser.add_argument("--sut-log", required=True)
    args = parser.parse_args()

    res = run_validation(args.test_log, args.sut_log)

    print("\n--- Validation Summary ---")
    for key, val in res["status"].items():
        print(f"{key.capitalize():<15}: {'PASS' if val else 'FAIL'}")

    if res["errors"]:
        # Generate error file
        report_filename = args.sut_log + ".failures.txt"
        with open(report_filename, "w") as f:
            f.write(f"Validation Report - {datetime.now()}\n")
            f.write(f"TEST Log: {args.test_log}\n")
            f.write(f"SUT Log:  {args.sut_log}\n")
            f.write("-" * 40 + "\n")
            for e in res["errors"]:
                f.write(f"FAIL: {e}\n")
        
        print(f"\nErrors Found! Detailed report written to: {report_filename}")
        for e in res["errors"]:
            print(f" - {e}")
        sys.exit(1)
    
    print("\nAll validation passed.")

if __name__ == "__main__":
    main()