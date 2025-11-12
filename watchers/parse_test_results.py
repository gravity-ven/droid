#!/usr/bin/env python3
"""
Test Results Parser

Parses test results in JUnit XML or text format.
Extracts pass/fail counts, errors, and test details.
"""

import sys
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET


def parse_junit_xml(file_path):
    """Parse JUnit XML test results."""

    result = {
        "status": "unknown",
        "success": False,
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "failures": [],
        "error_details": [],
        "test_time": None,
        "metadata": {}
    }

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Handle different XML formats
        if root.tag == 'testsuites':
            # Multiple test suites
            for testsuite in root.findall('.//testsuite'):
                result["total_tests"] += int(testsuite.get('tests', 0))
                result["failed"] += int(testsuite.get('failures', 0))
                result["errors"] += int(testsuite.get('errors', 0))
                result["skipped"] += int(testsuite.get('skipped', 0))

                # Parse test time
                time_str = testsuite.get('time')
                if time_str:
                    result["test_time"] = f"{float(time_str):.2f}s"

        elif root.tag == 'testsuite':
            # Single test suite
            result["total_tests"] = int(root.get('tests', 0))
            result["failed"] = int(root.get('failures', 0))
            result["errors"] = int(root.get('errors', 0))
            result["skipped"] = int(root.get('skipped', 0))

            time_str = root.get('time')
            if time_str:
                result["test_time"] = f"{float(time_str):.2f}s"

        # Calculate passed
        result["passed"] = result["total_tests"] - result["failed"] - result["errors"] - result["skipped"]

        # Extract failure details
        for failure in root.findall('.//failure'):
            test_case = failure.getparent()
            failure_info = {
                "test": test_case.get('name', 'unknown'),
                "classname": test_case.get('classname', ''),
                "message": failure.get('message', ''),
                "type": failure.get('type', ''),
                "text": failure.text.strip() if failure.text else ''
            }
            result["failures"].append(failure_info)

        # Extract error details
        for error in root.findall('.//error'):
            test_case = error.getparent()
            error_info = {
                "test": test_case.get('name', 'unknown'),
                "classname": test_case.get('classname', ''),
                "message": error.get('message', ''),
                "type": error.get('type', ''),
                "text": error.text.strip() if error.text else ''
            }
            result["error_details"].append(error_info)

        # Set success status
        result["success"] = (result["failed"] == 0 and result["errors"] == 0)
        result["status"] = "passed" if result["success"] else "failed"

    except ET.ParseError as e:
        result["status"] = "error"
        result["success"] = False
        result["error_details"].append({"error": f"XML parse error: {str(e)}"})
    except Exception as e:
        result["status"] = "error"
        result["success"] = False
        result["error_details"].append({"error": f"Failed to parse XML: {str(e)}"})

    return result


def parse_text_results(file_path):
    """Parse text-based test results."""

    result = {
        "status": "unknown",
        "success": False,
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "failures": [],
        "error_details": [],
        "test_time": None,
        "metadata": {}
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Detect test framework
        if "pytest" in content.lower():
            result["metadata"]["framework"] = "pytest"
        elif "jest" in content.lower():
            result["metadata"]["framework"] = "jest"
        elif "mocha" in content.lower():
            result["metadata"]["framework"] = "mocha"
        elif "unittest" in content.lower():
            result["metadata"]["framework"] = "unittest"

        # Extract pass/fail counts
        count_patterns = [
            r'(\d+)\s+passed',
            r'(\d+)\s+failed',
            r'(\d+)\s+skipped',
            r'(\d+)\s+error',
            r'Tests:\s*(\d+)\s+passed,\s*(\d+)\s+failed',
            r'OK\s+\((\d+)\s+test',
            r'FAILED\s+\(.*?failures=(\d+)',
        ]

        for pattern in count_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'passed' in match.group(0).lower():
                    result["passed"] = int(match.group(1))
                elif 'failed' in match.group(0).lower():
                    result["failed"] = int(match.group(1))
                elif 'skipped' in match.group(0).lower():
                    result["skipped"] = int(match.group(1))
                elif 'error' in match.group(0).lower():
                    result["errors"] = int(match.group(1))

        result["total_tests"] = result["passed"] + result["failed"] + result["skipped"] + result["errors"]

        # Extract test time
        time_patterns = [
            r'in\s+(\d+\.?\d*)\s*s(?:econds?)?',
            r'Time:\s+(\d+\.?\d*)\s*s',
            r'Ran\s+\d+\s+tests?\s+in\s+(\d+\.?\d*)\s*s',
        ]

        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result["test_time"] = f"{match.group(1)}s"
                break

        # Check for success markers
        if "All tests passed" in content or result["failed"] == 0 and result["errors"] == 0 and result["total_tests"] > 0:
            result["status"] = "passed"
            result["success"] = True
        elif "Tests failed" in content or result["failed"] > 0 or result["errors"] > 0:
            result["status"] = "failed"
            result["success"] = False

        # Extract failure details
        failure_patterns = [
            r'FAILED\s+([\w:\.]+)\s*-\s*(.+)',
            r'FAIL:\s+([\w\.]+)\s*\((.+?)\)',
            r'✗\s+([\w\s]+)',
        ]

        for pattern in failure_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                if len(match.groups()) == 2:
                    failure_info = {
                        "test": match.group(1).strip(),
                        "message": match.group(2).strip()
                    }
                else:
                    failure_info = {
                        "test": match.group(1).strip(),
                        "message": ""
                    }
                result["failures"].append(failure_info)

    except Exception as e:
        result["status"] = "error"
        result["success"] = False
        result["error_details"].append({"error": f"Failed to parse text results: {str(e)}"})

    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: parse_test_results.py <results_file>", file=sys.stderr)
        return 1

    results_file = sys.argv[1]

    if not Path(results_file).exists():
        print(f"Error: File not found: {results_file}", file=sys.stderr)
        return 1

    # Determine file type and parse
    if results_file.endswith('.xml'):
        parsed = parse_junit_xml(results_file)
    else:
        parsed = parse_text_results(results_file)

    # Save parsed data
    parsed_file = f"{results_file}.parsed.json"
    with open(parsed_file, 'w') as f:
        json.dump(parsed, f, indent=2)

    # Print summary
    print(f"Status: {parsed['status']}")
    print(f"Success: {parsed['success']}")
    print(f"Total: {parsed['total_tests']}")
    print(f"Passed: {parsed['passed']}")
    print(f"Failed: {parsed['failed']}")
    print(f"Errors: {parsed['errors']}")
    print(f"Skipped: {parsed['skipped']}")
    if parsed['test_time']:
        print(f"Test time: {parsed['test_time']}")
    print(f"Parsed data saved to: {parsed_file}")

    # Exit code based on success
    return 0 if parsed["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
