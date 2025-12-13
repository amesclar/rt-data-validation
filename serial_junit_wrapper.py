#!/usr/bin/env python3
#
# example usage:
# python3 serial_junit_wrapper.py --port /dev/cu.usbmodem14301
# python3 serial_junit_wrapper.py --port /dev/cu.usbmodem14301 --baud 9600 --outfile regatta.xml
# 
import serial
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(description="Convert Arduino regatta timer logs into JUnit XML.")
    p.add_argument("--port", required=True, help="Serial port (e.g. /dev/cu.usbmodem14301)")
    p.add_argument("--baud", default=9600, type=int, help="Baud rate (default 9600)")
    p.add_argument("--outfile", default="junit_output.xml", help="JUnit XML output file")
    return p.parse_args()

def create_suite(name):
    suite = ET.Element("testsuite")
    suite.set("name", name)
    return suite

def add_testcase(suite, classname, eventat, longcount, shortcount):
    tc = ET.SubElement(suite, "testcase")
    tc.set("classname", classname)
    tc.set("eventat", str(eventat))
    tc.set("type", "Buzzer")
    tc.set("longcount", str(longcount))
    tc.set("shortcount", str(shortcount))

def write_xml(root, filename):
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

def main():
    args = parse_args()

    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
    except Exception as e:
        print("ERROR: Could not open serial port:", e)
        return

    root = ET.Element("testsuites")
    current_suite = None

    print("Listening on", args.port, "... Press Ctrl+C to stop.")

    try:
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                continue

            # <sequenceStart name="1min" duration="60"/>
            if line.startswith("<sequenceStart"):
                parts = dict(x.split("=") for x in line.replace("<sequenceStart", "")
                                                      .replace("/>", "")
                                                      .replace("\"", "")
                                                      .split() if "=" in x)
                name = parts.get("name", "Unknown")
                current_suite = create_suite(f"TimerSequence_{name}")
                root.append(current_suite)
                continue

            # <sequenceEnd/>
            if line.startswith("<sequenceEnd"):
                current_suite = None
                continue

            # <buzzerEvent time="30" long="0" short="3"/>
            if line.startswith("<buzzerEvent") and current_suite is not None:
                parts = dict(x.split("=") for x in line.replace("<buzzerEvent", "")
                                                      .replace("/>", "")
                                                      .replace("\"", "")
                                                      .split() if "=" in x)
                eventat = parts.get("time", "0")
                longc   = parts.get("long", "0")
                shortc  = parts.get("short", "0")
                add_testcase(current_suite, "BuzzerLogic", eventat, longc, shortc)
                continue

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        ser.close()

    write_xml(root, args.outfile)
    print("JUnit XML written to", args.outfile)

if __name__ == "__main__":
    main()
