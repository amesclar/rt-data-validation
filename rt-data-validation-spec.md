# Summary
Python script that validates the data generated from the regattaTimer-Kicad Arduino application driven by the rt-testFW Arduino test driver application. The regattaTimer-Kicad logs will be compared rt-testFW logs and known timing sequences that can be hardcoded. The output will be JUNIT XML formatted.

# Expected results file attributes
+ testId = current test iteration
+ which = 1min, 2min, 3min, 5min
+ ticks = timer ticks

# Actual results file
+ timer sequence bracketed by "sequence start" and "sequence_end"
+ second value (1,2,3,5) aligns with expected results 1min, 2min, 3min, 5min
+ buzz_long and buzz_short counts and timing should match buzzer activation tables listed below for 1min, 2min, 3min, 5min

# Validation tests
## Counts
Does the actual count of 1min, 2min, 3min, 5min tests align with with the count found in expected results file

## Sequence
Does the actual timer sequence in the actual results match the expected results

## Buzzer activation
Does the buzzer activation timing, long/short and count match the expected results table for 1min, 2min, 3min and 5min sequences

# Expected buzzer durations
| which | millisecond |
| -- | -- |
| long  | 400 |
| short | 150 |

# Expected buzzer activations
## 1min
| seconds | long buzzer count | short buzzer count |
| -- | -- | -- |
| 000 | 1 | 0 |
| 030 | 0 | 3 |
| 040 | 0 | 2 |
| 050 | 0 | 1 |
| 055 | 0 | 1 |
| 056 | 0 | 1 |
| 057 | 0 | 1 |
| 058 | 0 | 1 |
| 059 | 0 | 1 |
| 060 | 1 | 0 |

## 2min
| seconds | long buzzer count | short buzzer count |
| -- | -- | -- |
| 000 | 2 | 0 |
| 030 | 1 | 3 |
| 060 | 1 | 0 |
| 090 | 0 | 3 |
| 100 | 0 | 2 |
| 110 | 0 | 1 |
| 115 | 0 | 1 |
| 116 | 0 | 1 |
| 117 | 0 | 1 |
| 118 | 0 | 1 |
| 119 | 0 | 1 |
| 120 | 1 | 0 |

## 3min
| seconds | long buzzer count | short buzzer count |
| -- | -- | -- |
| 000 | 3 | 0 |
| 060 | 2 | 0 |
| 090 | 1 | 3 |
| 120 | 1 | 0 |
| 150 | 0 | 3 |
| 160 | 0 | 2 |
| 170 | 0 | 1 |
| 175 | 0 | 1 |
| 176 | 0 | 1 |
| 177 | 0 | 1 |
| 178 | 0 | 1 |
| 179 | 0 | 1 |
| 180 | 1 | 0 |

## 5min
| seconds | long buzzer count | short buzzer count |
| -- | -- | -- |
| 000 | 1 | 0 |
| 060 | 1 | 0 |
| 240 | 1 | 0 |
| 300 | 1 | 0 |
