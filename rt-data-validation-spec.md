# Regatta Timer Test Framework Data Validation

- [Regatta Timer Test Framework Data Validation](#regatta-timer-test-framework-data-validation)
  - [Summary](#summary)
  - [TEST - log examples](#test---log-examples)
    - [Attribute description](#attribute-description)
  - [SUT - log example](#sut---log-example)
    - [Attribute description](#attribute-description-1)
  - [Error references](#error-references)
  - [Validation tests](#validation-tests)
    - [Counts](#counts)
    - [Sequence](#sequence)
    - [Consistency](#consistency)
    - [Test duration](#test-duration)
    - [Buzzer durations](#buzzer-durations)
    - [Buzzer activation](#buzzer-activation)
      - [1min](#1min)
      - [2min](#2min)
      - [3min](#3min)
      - [5min](#5min)
    - [Edge case 1 sample data](#edge-case-1-sample-data)


## Summary

Python script that validates the data generated from the regattaTimer-Kicad Arduino application (SUT) driven by the rt-testFW Arduino test driver application (TEST). 

The SUT logs will be compared to the TEST logs and known timing sequences documented below.

One test cycle is defined as a test sequence (1min, 2min, 3min, 5min) repeated "iterations" times.

The log entries will be JUNIT XML formatted with each line prefixed with the timestamp of the log line (see example).

Log file names should be accepted as a command line arguments.

The validation should also include a visualization for Buzzer Drift (also known as jitter) to determine if the SUT is running at the correct speed. Jitter is the difference between the actual timestamp in the log and the expected time based on the StartEvent. 

## TEST - log examples

```
[2025-12-19 10:59:50. Regatta Timer Test Framework Ready
[2025-12-19 10:59:59. <testsuite name="RegattaTimerAutomatedTest">
[2025-12-19 10:59:59. <testcase classname="AutoCycleStart" iterations="10" type="CycleStart"/>
[2025-12-19 10:59:59. <testcase classname="TestStart" testsequence="1" iteration="1" elapsed="0" type="Start" duration="60"/>
[2025-12-19 11:00:59. <testcase classname="TestEnd" testsequence="1" iteration="1" elapsed="60" type="End"/>
...
[2025-12-19 12:42:13. <testcase classname="SequenceComplete" iteration="9"/>
[2025-12-19 12:42:13. <testcase classname="TestStart" testsequence="1" iteration="10" elapsed="0" type="Start" duration="60"/>
[2025-12-19 12:43:13. <testcase classname="TestEnd" testsequence="1" iteration="10" elapsed="60" type="End"/>
[2025-12-19 12:43:19. <testcase classname="TestStart" testsequence="2" iteration="10" elapsed="0" type="Start" duration="120"/>
[2025-12-19 12:45:19. <testcase classname="TestEnd" testsequence="2" iteration="10" elapsed="120" type="End"/>
[2025-12-19 12:45:24. <testcase classname="TestStart" testsequence="3" iteration="10" elapsed="0" type="Start" duration="180"/>
[2025-12-19 12:48:24. <testcase classname="TestEnd" testsequence="3" iteration="10" elapsed="180" type="End"/>
[2025-12-19 12:48:29. <testcase classname="TestStart" testsequence="5" iteration="10" elapsed="0" type="Start" duration="300"/>
[2025-12-19 12:53:30. <testcase classname="TestEnd" testsequence="5" iteration="10" elapsed="300" type="End"/>
[2025-12-19 12:53:35. <testcase classname="SequenceComplete" iteration="10"/>
[2025-12-19 12:53:35. <testcase classname="AutoCycleEnd" type="CycleEnd"/>
[2025-12-19 12:53:35. </testsuite>
```

### Attribute description

+ classname = TestStart, TestEnd, SequenceComplete, AutoCycleEnd
+ iteration = current test iteration
+ elapsed = elapsed time in seconds
+ type = Start, End, CycleStart, CycleEnd
+ duration = duration of test in seconds
+ testsequence = 1min, 2min, 3min, 5min

## SUT - log example

```
[2025-12-19 10:59:50. Sailing Regatta Timer Ready
[2025-12-19 10:59:59. <testcase classname="StartEvent" whichtest="1min" elapsed="0" type="Start"/>
[2025-12-19 11:00:00. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="0" type="Buzzer" longcount="1" shortcount="0"/>
[2025-12-19 11:00:29. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="30" type="Buzzer" longcount="0" shortcount="3"/>
[2025-12-19 11:00:39. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="40" type="Buzzer" longcount="0" shortcount="2"/>
[2025-12-19 11:00:49. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="50" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:00:54. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="55" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:00:55. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="56" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:00:56. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="57" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:00:57. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="58" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:00:58. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="59" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:00:59. <testcase classname="BuzzerEvent" whichtest="1min" elapsed="60" type="Buzzer" longcount="1" shortcount="0"/>
[2025-12-19 11:01:00. <testcase classname="EndEvent" whichtest="1min" elapsed="60" type="End"/>
...
[2025-12-19 12:48:30. <testcase classname="StartEvent" whichtest="5min" elapsed="0" type="Start"/>
[2025-12-19 12:48:30. <testcase classname="BuzzerEvent" whichtest="5min" elapsed="0" type="Buzzer" longcount="1" shortcount="0"/>
[2025-12-19 12:49:29. <testcase classname="BuzzerEvent" whichtest="5min" elapsed="60" type="Buzzer" longcount="1" shortcount="0"/>
[2025-12-19 12:52:29. <testcase classname="BuzzerEvent" whichtest="5min" elapsed="240" type="Buzzer" longcount="1" shortcount="0"/>
[2025-12-19 12:53:29. <testcase classname="BuzzerEvent" whichtest="5min" elapsed="300" type="Buzzer" longcount="1" shortcount="0"/>
[2025-12-19 12:53:30. <testcase classname="EndEvent" whichtest="5min" elapsed="300" type="End"/>
```

### Attribute description

+ classname = StartEvent, BuzzerEvent, EndEvent
+ whichtest = 1min, 2min, 3min, 5min
+ elapsed = elapsed time in seconds
+ type = Start, Buzzer, End
+ longcount = number of long buzzers
+ shortcount = number of short buzzers

## Error references

Test failures should reference log line entries by log line number.

Errors should be saved to a separate file.

## Validation tests

### Counts

Does the total number of 1m, 2m, 3m, 5m tests align with the "iterations" value found in TEST results file

### Sequence

Does the SUT timer sequence match the TEST results file timer sequence

### Consistency

In the SUT file do the BuzzerEvent whichtest entries align with the whichtest values with the StartEvent and EndEvent entries.

### Test duration

Verify that the duration between the StartEvent and EndEvent timestamps matches the expected test duration.

### Buzzer durations

Do the SUT buzzer durations match
| which | millisecond |
| ----- | ----------- |
| long  | 400         |
| short | 150         |

### Buzzer activation

Does the SUT buzzer activation timing, long/short and count match the expected results table for 1min, 2min, 3min and 5min sequences

#### 1min

| seconds | long buzzer count | short buzzer count |
| ------- | ----------------- | ------------------ |
| 000     | 1                 | 0                  |
| 030     | 0                 | 3                  |
| 040     | 0                 | 2                  |
| 050     | 0                 | 1                  |
| 055     | 0                 | 1                  |
| 056     | 0                 | 1                  |
| 057     | 0                 | 1                  |
| 058     | 0                 | 1                  |
| 059     | 0                 | 1                  |
| 060     | 1                 | 0                  |

#### 2min

| seconds | long buzzer count | short buzzer count |
| ------- | ----------------- | ------------------ |
| 000     | 2                 | 0                  |
| 030     | 1                 | 3                  |
| 060     | 1                 | 0                  |
| 090     | 0                 | 3                  |
| 100     | 0                 | 2                  |
| 110     | 0                 | 1                  |
| 115     | 0                 | 1                  |
| 116     | 0                 | 1                  |
| 117     | 0                 | 1                  |
| 118     | 0                 | 1                  |
| 119     | 0                 | 1                  |
| 120     | 1                 | 0                  |

#### 3min

| seconds | long buzzer count | short buzzer count |
| ------- | ----------------- | ------------------ |
| 000     | 3                 | 0                  |
| 060     | 2                 | 0                  |
| 090     | 1                 | 3                  |
| 120     | 1                 | 0                  |
| 150     | 0                 | 3                  |
| 160     | 0                 | 2                  |
| 170     | 0                 | 1                  |
| 175     | 0                 | 1                  |
| 176     | 0                 | 1                  |
| 177     | 0                 | 1                  |
| 178     | 0                 | 1                  |
| 179     | 0                 | 1                  |
| 180     | 1                 | 0                  |

#### 5min

| seconds | long buzzer count | short buzzer count |
| ------- | ----------------- | ------------------ |
| 000     | 1                 | 0                  |
| 060     | 1                 | 0                  |
| 240     | 1                 | 0                  |
| 300     | 1                 | 0                  |

### Edge case 1 sample data

The following 3min SUT includes 2min activations.

[2025-12-19 11:03:11. <testcase classname="StartEvent" whichtest="3min" elapsed="0" type="Start"/>
[2025-12-19 11:03:11. <testcase classname="BuzzerEvent" whichtest="3min" elapsed="0" type="Buzzer" longcount="3" shortcount="0"/>
[2025-12-19 11:04:11. <testcase classname="BuzzerEvent" whichtest="3min" elapsed="60" type="Buzzer" longcount="2" shortcount="0"/>
[2025-12-19 11:04:41. <testcase classname="BuzzerEvent" whichtest="3min" elapsed="90" type="Buzzer" longcount="1" shortcount="3"/>
[2025-12-19 11:05:11. <testcase classname="BuzzerEvent" whichtest="3min" elapsed="120" type="Buzzer" longcount="1" shortcount="0"/>
[2025-12-19 11:48:01. <testcase classname="BuzzerEvent" whichtest="2min" elapsed="90" type="Buzzer" longcount="0" shortcount="3"/>
[2025-12-19 11:48:11. <testcase classname="BuzzerEvent" whichtest="2min" elapsed="100" type="Buzzer" longcount="0" shortcount="2"/>
[2025-12-19 11:48:21. <testcase classname="BuzzerEvent" whichtest="2min" elapsed="110" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:48:26. <testcase classname="BuzzerEvent" whichtest="2min" elapsed="115" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:48:27. <testcase classname="BuzzerEvent" whichtest="2min" elapsed="116" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:48:28. <testcase classname="BuzzerEvent" whichtest="2min" elapsed="117" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:48:29. <testcase classname="BuzzerEvent" whichtest="2min" elapsed="118" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:48:30. <testcase classname="BuzzerEvent" whichtest="2min" elapsed="119" type="Buzzer" longcount="0" shortcount="1"/>
[2025-12-19 11:48:31. <testcase classname="BuzzerEvent" whichtest="2min" elapsed="120" type="Buzzer" longcount="1" shortcount="0"/>
[2025-12-19 11:48:32. <testcase classname="EndEvent" whichtest="2min" elapsed="120" type="End"/>
