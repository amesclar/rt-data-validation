#!/usr/bin/env python3
#
# usage: run-validation.sh or manual CLI:
#   python3 data-validation-ai-python.py --expected exp.xml --actual act.xml --junit report.xml
#

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from collections import defaultdict
import json
import argparse
import sys
from typing import List, Dict
import pandas as pd
import xml.dom.minidom as minidom

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

EXPECTED_ACTIVATIONS = {
    "1min": {0: (1,0),30:(0,3),40:(0,2),50:(0,1),55:(0,1),56:(0,1),
             57:(0,1),58:(0,1),59:(0,1),60:(1,0)},
    "2min": {0:(2,0),30:(1,3),60:(1,0),90:(0,3),100:(0,2),110:(0,1),
             115:(0,1),116:(0,1),117:(0,1),118:(0,1),119:(0,1),120:(1,0)},
    "3min": {0:(3,0),60:(2,0),90:(1,3),120:(1,0),150:(0,3),160:(0,2),
             170:(0,1),175:(0,1),176:(0,1),177:(0,1),178:(0,1),179:(0,1),180:(1,0)},
    "5min": {0:(1,0),60:(1,0),240:(1,0),300:(1,0)}
}

SEQUENCE_MAP = {"1": "1min", "2": "2min", "3": "3min", "5": "5min"}

# ---------------------------------------------------------------------
# DATA CLASSES
# ---------------------------------------------------------------------

@dataclass
class BuzzEvent:
    second: int
    tick: int
    type: str  # long/short

@dataclass
class Sequence:
    which: str
    start_tick: int
    end_tick: int = 0
    events: List[BuzzEvent] = field(default_factory=list)

# ---------------------------------------------------------------------
# PARSERS
# ---------------------------------------------------------------------

def parse_expected_results(path: str) -> List[Dict]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        sys.exit(f"Error parsing >>> {path} <<< expected results XML: {e}")
    root = tree.getroot()
    tests = []
    for t in root.findall("Test"):
        which = t.get("which")
        if which is None:
            print(f"Warning: Test entry missing 'which': {ET.tostring(t)}")
            continue
        test_id = t.get("testId")
        if test_id is None:
            print(f"Warning: Test entry missing 'testId': {ET.tostring(t)}")
            continue
        tests.append({"which": which, "test_id": int(test_id)})
    return tests


def parse_actual_results(path: str) -> List[Sequence]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        sys.exit(f"Error parsing >>> {path} <<< actual results XML: {e}")

    root = tree.getroot()
    sequences: List[Sequence] = []
    current_seq = None

    for ev in root.findall("event"):
        tag = ev.get("tag")
        try:
            sec = int(ev.get("second"))
            tick = int(ev.get("tick"))
        except (TypeError, ValueError):
            print(f"Warning: event missing numeric attributes: {ET.tostring(ev)}")
            continue

        if tag == "sequence_start":
            if str(sec) not in SEQUENCE_MAP:
                print(f"Warning: unknown sequence second '{sec}'")
                continue
            current_seq = Sequence(which=SEQUENCE_MAP[str(sec)], start_tick=tick)
            sequences.append(current_seq)

        elif tag == "sequence_end":
            if current_seq:
                current_seq.end_tick = tick
                current_seq = None
            else:
                print(f"Warning: sequence_end without start at tick {tick}")

        elif tag.startswith("buzz_"):
            if current_seq is None:
                print(f"Warning: buzz event outside sequence at tick {tick}")
                continue
            buzz_type = "long" if tag == "buzz_long" else "short"
            current_seq.events.append(BuzzEvent(second=sec, tick=tick, type=buzz_type))

    return sequences

# ---------------------------------------------------------------------
# VALIDATORS
# ---------------------------------------------------------------------

def validate_sequence_counts(expected, actual):
    exp_count = defaultdict(int)
    act_count = defaultdict(int)
    for t in expected: exp_count[t["which"]] += 1
    for a in actual: act_count[a.which] += 1
    return {"expected": dict(exp_count), "actual": dict(act_count)}

def validate_sequence_order(expected, actual):
    exp_order = [t["which"] for t in expected]
    act_order = [a.which for a in actual]
    return {"expected": exp_order, "actual": act_order}

def validate_buzzer_counts(seq: Sequence):
    which = seq.which
    expected = EXPECTED_ACTIVATIONS[which]
    actual_counts = defaultdict(lambda: {"long": 0, "short": 0})

    for ev in seq.events:
        actual_counts[ev.second][ev.type] += 1

    errors = []
    for sec, (exp_long, exp_short) in expected.items():
        a_long = actual_counts[sec]["long"]
        a_short = actual_counts[sec]["short"]
        if a_long != exp_long or a_short != exp_short:
            errors.append({
                "second": sec,
                "expected": (exp_long, exp_short),
                "actual": (a_long, a_short)
            })
    return errors

# ---------------------------------------------------------------------
# JUNIT GENERATOR
# ---------------------------------------------------------------------

def generate_junit_xml(report: Dict) -> str:
    def add_failure(parent, message, payload_dict):
        tc = ET.SubElement(parent, "testcase", {"name": message})
        fail = ET.SubElement(tc, "failure", {"message": message})

        # Add CDATA wrapper manually — ElementTree does NOT support CDATA natively
        json_text = json.dumps(payload_dict, indent=4)

        fail.text = f"<![CDATA[\n{json_text}\n]]>"

    root = ET.Element("testsuite", {
        "name": "SailingTimerValidation",
        "tests": str(len(report["sequences"]) + 2),
        "failures": str(report["summary"]["failed_sequences"])
    })

    # --- Test 1: Sequence count validation ---
    tc1 = ET.SubElement(root, "testcase", {"name": "SequenceCountValidation"})
    if report["counts"]["expected"] != report["counts"]["actual"]:
        f = ET.SubElement(tc1, "failure", {"message": "Sequence counts mismatch"})
        json_text = json.dumps(report["counts"], indent=4)
        f.text = f"<![CDATA[\n{json_text}\n]]>"

    # --- Test 2: Sequence order validation ---
    tc2 = ET.SubElement(root, "testcase", {"name": "SequenceOrderValidation"})
    if report["sequence_order"]["expected"] != report["sequence_order"]["actual"]:
        f = ET.SubElement(tc2, "failure", {"message": "Sequence order mismatch"})
        json_text = json.dumps(report["sequence_order"], indent=4)
        f.text = f"<![CDATA[\n{json_text}\n]]>"

    # --- Per sequence buzzer validation ---
    for seq in report["sequences"]:
        tc = ET.SubElement(root, "testcase", {
            "name": f"Sequence_{seq['which']}",
            "classname": "BuzzerCounts"
        })
        if seq["buzzer_count_errors"]:
            f = ET.SubElement(tc, "failure", {"message": "Buzzer count errors"})
            json_text = json.dumps(seq["buzzer_count_errors"], indent=4)
            f.text = f"<![CDATA[\n{json_text}\n]]>"

    xml_str = ET.tostring(root, encoding="utf-8")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")

# ---------------------------------------------------------------------
# REPORT GENERATION / MAIN VALIDATION
# ---------------------------------------------------------------------

def validate(expected_path, actual_path, to_dataframe=False):
    expected = parse_expected_results(expected_path)
    actual = parse_actual_results(actual_path)

    report = {}
    report["counts"] = validate_sequence_counts(expected, actual)
    report["sequence_order"] = validate_sequence_order(expected, actual)

    seq_reports = []
    passed_sequences = 0

    for seq in actual:
        buzzer_count_errors = validate_buzzer_counts(seq)
        passed = (len(buzzer_count_errors) == 0)
        if passed:
            passed_sequences += 1

        seq_reports.append({
            "which": seq.which,
            "start_tick": seq.start_tick,
            "end_tick": seq.end_tick,
            "buzzer_count_errors": buzzer_count_errors,
            "pass": passed
        })

    report["sequences"] = seq_reports
    report["summary"] = {
        "total_sequences": len(actual),
        "passed_sequences": passed_sequences,
        "failed_sequences": len(actual) - passed_sequences
    }

    if to_dataframe:
        rows = []
        for s in seq_reports:
            for e in s["buzzer_count_errors"]:
                rows.append({**e, "which": s["which"], "type": "count_error"})
        report["df"] = pd.DataFrame(rows)

    return report

# ---------------------------------------------------------------------
# PRINT REPORT (HUMAN)
# ---------------------------------------------------------------------

def print_report(report):
    print("\n=== Validation Summary ===")
    print(f"Total sequences: {report['summary']['total_sequences']}")
    print(f"Passed: {report['summary']['passed_sequences']}")
    print(f"Failed: {report['summary']['failed_sequences']}")

    print("\nSequence counts comparison:")
    if report["counts"]["expected"] == report["counts"]["actual"]:
        print("PASS: test counts match")
    else:
        print("FAIL: test counts do not match")
        print(json.dumps(report["counts"], indent=4))

    print("\nSequence order comparison:")
    print(json.dumps(report["sequence_order"], indent=4))

    print("\nDetailed sequence reports:")
    for s in report["sequences"]:
        print(f"\nSequence {s['which']} (ticks {s['start_tick']} - {s['end_tick']})")
        print(f"PASS: {s['pass']}")
        if s["buzzer_count_errors"]:
            print("  Buzzer count errors:")
            for e in s["buzzer_count_errors"]:
                print(f"    {e}")

# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Validate sailing timer XML logs.")
    parser.add_argument("--expected", required=True, help="Expected XML file path")
    parser.add_argument("--actual", required=True, help="Actual XML file path")
    parser.add_argument("--df", action="store_true", help="Generate Pandas dataframe of errors")
    parser.add_argument("--junit", help="Output JUnit XML file")
    args = parser.parse_args()

    report = validate(args.expected, args.actual, to_dataframe=args.df)

    print_report(report)

    if args.junit:
        xml_output = generate_junit_xml(report)
        with open(args.junit, "w") as f:
            f.write(xml_output)
        print(f"\nJUnit XML written to: {args.junit}")

    if args.df:
        if "df" in report:
            print("\nDataFrame preview:")
            print(report["df"].head())
        else:
            print("\nDataFrame not generated (no errors found or --df flag not used).")

if __name__ == "__main__":
    main()
