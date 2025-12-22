import pytest
from datetime import datetime
from rt_data_validation import parse_log_line, run_validation

def test_parse_log_line_valid():
    line = '[2025-12-22 10:00:00. <testcase classname="StartEvent" whichtest="1min"/>'
    ts, node = parse_log_line(line)
    assert ts == datetime(2025, 12, 22, 10, 0, 0)
    assert node.get("classname") == "StartEvent"

def test_parse_log_line_invalid():
    ts, node = parse_log_line("junk data")
    assert ts is None

def test_duration_validation_failure(tmp_path):
    test_log, sut_log = tmp_path / "test.log", tmp_path / "sut.log"
    test_log.write_text('[2025-12-22 09:00:00. <testcase classname="TestStart" testsequence="1" duration="60"/>')
    sut_log.write_text('[2025-12-22 09:00:00. <testcase classname="StartEvent" whichtest="1min"/>\n'
                       '[2025-12-22 09:00:10. <testcase classname="EndEvent" whichtest="1min"/>')
    report = run_validation(str(test_log), str(sut_log))
    assert report["status"]["duration"] is False

def test_buzzer_count_mismatch(tmp_path):
    test_log, sut_log = tmp_path / "test.log", tmp_path / "sut.log"
    test_log.write_text('[2025-12-22 09:00:00. <testcase classname="TestStart" testsequence="1"/>')
    sut_log.write_text('[2025-12-22 09:00:00. <testcase classname="StartEvent" whichtest="1min"/>\n'
                       '[2025-12-22 09:00:00. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="0" longcount="0" shortcount="5"/>\n'
                       '[2025-12-22 09:01:00. <testcase classname="EndEvent" whichtest="1min"/>')
    report = run_validation(str(test_log), str(sut_log))
    assert report["status"]["buzzer"] is False

def test_label_alignment_mismatch(tmp_path):
    test_log, sut_log = tmp_path / "test.log", tmp_path / "sut.log"
    test_log.write_text('[2025-12-22 09:00:00. <testcase classname="TestStart" testsequence="1"/>')
    sut_log.write_text('[2025-12-22 09:00:00. <testcase classname="StartEvent" whichtest="1min"/>\n'
                       '[2025-12-22 09:00:01. <testcase classname="BuzzerEvent" whichtest="5min" elapsed="0"/>\n'
                       '[2025-12-22 09:01:00. <testcase classname="EndEvent" whichtest="1min"/>')
    report = run_validation(str(test_log), str(sut_log))
    assert report["status"]["alignment"] is False

def test_line_number_accuracy(tmp_path):
    test_log, sut_log = tmp_path / "test_line.log", tmp_path / "sut_line.log"
    test_log.write_text('[2025-12-22 09:00:00. <testcase classname="TestStart" testsequence="1"/>')
    
    # We MUST include an EndEvent, otherwise the parser ignores the whole block
    sut_content = ["[Noise]\n"] * 5
    sut_content.append('[2025-12-22 09:00:00. <testcase classname="StartEvent" whichtest="1min"/>\n')
    sut_content.append('[2025-12-22 09:00:01. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="0" longcount="5" shortcount="5"/>\n')
    sut_content.append('[2025-12-22 09:01:00. <testcase classname="EndEvent" whichtest="1min"/>\n')
    
    sut_log.write_text("".join(sut_content))
    report = run_validation(str(test_log), str(sut_log))
    
    # Now that the block is finished, Line 7 (Buzzer) will be evaluated
    assert any("[SUT Line 7]" in err for err in report["errors"])

def test_drift_calculation_accuracy(tmp_path):
    test_log, sut_log = tmp_path / "test_drift.log", tmp_path / "sut_drift.log"
    test_log.write_text('[2025-12-22 09:00:00. <testcase classname="TestStart" testsequence="1"/>')
    
    # We must provide the 0s buzzer that the 1min sequence expects, 
    # then we test the drift on the second buzzer.
    sut_log.write_text(
        '[2025-12-22 09:00:00. <testcase classname="StartEvent" whichtest="1min" elapsed="0"/>\n'
        '[2025-12-22 09:00:00. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="0" longcount="1" shortcount="0"/>\n'
        '[2025-12-22 09:00:31.500 <testcase classname="BuzzerEvent" whichtest="1min" elapsed="30" longcount="0" shortcount="3"/>\n'
        '[2025-12-22 09:01:00. <testcase classname="EndEvent" whichtest="1min"/>'
    )
    
    report = run_validation(str(test_log), str(sut_log))
    drifts = report.get("drift_data", [])
    
    # Drift for the 30s buzzer:
    # Expected: 09:00:00 + 30s = 09:00:30
    # Actual: 09:00:31
    # Result: ~1000ms drift
    assert len(drifts) > 0
    assert any(900 < d < 1100 for d in drifts)
