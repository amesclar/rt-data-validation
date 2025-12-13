# python script to validate regatta timer test run
#
# *** note ***
# 135 files are missing 2min execution
# TODO - update test files to include 2min execution
#
# test_data_samples
# 135-fw - test framework - expected results
# 135-rt - regatta timer -- actual results
#
# Validation rules
# does test cycle count match
#   expected - count 1min, 2min, 3min, 5min
#       <Test which=1min id=13900/>
#   actual --- count second=1, 2, 3, 5
#       <event tag="sequence_start" type="start" second="1" tick="9080" />
#
# does test cycle order match
# is the long/short buzzer count correct
# did the long/short buzzer sound at the correct time
#
# ---
# usage: ./run-validation.sh test_data_samples/135-fw.xml test_data_samples/135-rt.xml
#

import pandas as pd
import sys

def xml2df(xml_file):
    df = pd.read_xml(xml_file)
    return df

def count_fw_which(df):

    exp_1m = (df['which'] == '1min').sum()
    exp_2m = (df['which'] == '2min').sum()
    exp_3m = (df['which'] == '3min').sum()
    exp_5m = (df['which'] == '5min').sum()

    return [exp_1m, exp_2m, exp_3m, exp_5m]

def count_rt_sequence_start(df):

    act_1m = ((df['type'] == 'start') & (df['second'] == 1)).sum()
    act_2m = ((df['type'] == 'start') & (df['second'] == 2)).sum()
    act_3m = ((df['type'] == 'start') & (df['second'] == 3)).sum()
    act_5m = ((df['type'] == 'start') & (df['second'] == 5)).sum()

    return [act_1m, act_2m, act_3m, act_5m]

def validate_test_counts(fw_df,rt_df):
    exp_count = count_fw_which(fw_df)
    act_count = count_rt_sequence_start(rt_df)
    print(exp_count)
    print(act_count)

    if exp_count == act_count:
        print("SUCCESS - expected test count MATCHES actual test count")
    else:
        print("FAIL - expected test count NOT equal actual test count")

# *** main starts here ***
def main():
    print(f"Script name: {sys.argv[0]}")

    if len(sys.argv) > 1:

        fw_xml = sys.argv[1]
        rt_xml = sys.argv[2]

        fw_df = xml2df(fw_xml)
        rt_df = xml2df(rt_xml)
        print(fw_df)
        print(rt_df)

        validate_test_counts(fw_df,rt_df)

if __name__ == "__main__":
    main()
