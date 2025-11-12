#!/usr/bin/env python3
"""
Process Output Parser

Generic parser for external process output.
Validates output and extracts basic metrics.
"""

import sys
import json
import re
from pathlib import Path


def parse_process_output(file_path):
    """Parse generic process output file."""

    result = {
        "status": "unknown",
        "success": False,
        "exit_code": None,
        "errors": [],
        "warnings": [],
        "output_lines": 0,
        "metadata": {}
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        result["output_lines"] = content.count('\n')
        result["metadata"]["file_size"] = len(content)

        # Look for exit code
        exit_patterns = [
            r'Exit code:\s*(\d+)',
            r'exit status:\s*(\d+)',
            r'returned\s+(\d+)',
            r'Process exited with code\s+(\d+)',
        ]

        for pattern in exit_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result["exit_code"] = int(match.group(1))
                break

        # Detect success based on exit code or markers
        if result["exit_code"] is not None:
            result["success"] = (result["exit_code"] == 0)
            result["status"] = "success" if result["success"] else "failed"
        else:
            # Look for success/failure markers
            success_markers = [
                "completed successfully",
                "finished successfully",
                "success",
                "done",
                "OK"
            ]

            failure_markers = [
                "failed",
                "error",
                "exception",
                "abort",
                "crash"
            ]

            content_lower = content.lower()

            has_success = any(marker in content_lower for marker in success_markers)
            has_failure = any(marker in content_lower for marker in failure_markers)

            if has_success and not has_failure:
                result["status"] = "success"
                result["success"] = True
            elif has_failure:
                result["status"] = "failed"
                result["success"] = False
            else:
                result["status"] = "unknown"
                result["success"] = False

        # Extract errors
        error_patterns = [
            r'(?:^|\n)Error:\s*(.+)',
            r'(?:^|\n)ERROR:\s*(.+)',
            r'(?:^|\n)Fatal:\s*(.+)',
            r'(?:^|\n)Exception:\s*(.+)',
            r'(?:^|\n)Traceback',
        ]

        for pattern in error_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 0:
                    error_msg = match.group(1).strip()
                else:
                    error_msg = match.group(0).strip()

                if error_msg and error_msg not in result["errors"]:
                    result["errors"].append(error_msg)

        # Extract warnings
        warning_patterns = [
            r'(?:^|\n)Warning:\s*(.+)',
            r'(?:^|\n)WARN:\s*(.+)',
            r'(?:^|\n)Caution:\s*(.+)',
        ]

        for pattern in warning_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                warn_msg = match.group(1).strip()
                if warn_msg and warn_msg not in result["warnings"]:
                    result["warnings"].append(warn_msg)

        # Extract execution time if available
        time_patterns = [
            r'(?:Execution|Runtime|Duration|Elapsed):\s*(\d+\.?\d*)\s*(\w+)',
            r'Took\s+(\d+\.?\d*)\s*(\w+)',
            r'Completed in\s+(\d+\.?\d*)\s*(\w+)',
        ]

        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result["metadata"]["execution_time"] = f"{match.group(1)} {match.group(2)}"
                break

        # Detect process type if possible
        if "python" in content.lower():
            result["metadata"]["process_type"] = "python"
        elif "node" in content.lower() or "npm" in content.lower():
            result["metadata"]["process_type"] = "nodejs"
        elif "java" in content.lower():
            result["metadata"]["process_type"] = "java"
        elif "mojo" in content.lower():
            result["metadata"]["process_type"] = "mojo"
        elif "bash" in content.lower() or "sh" in content.lower():
            result["metadata"]["process_type"] = "shell"

    except Exception as e:
        result["status"] = "error"
        result["success"] = False
        result["errors"].append(f"Failed to parse process output: {str(e)}")

    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: parse_process_output.py <output_file>", file=sys.stderr)
        return 1

    output_file = sys.argv[1]

    if not Path(output_file).exists():
        print(f"Error: File not found: {output_file}", file=sys.stderr)
        return 1

    # Parse process output
    parsed = parse_process_output(output_file)

    # Save parsed data
    parsed_file = f"{output_file}.parsed.json"
    with open(parsed_file, 'w') as f:
        json.dump(parsed, f, indent=2)

    # Print summary
    print(f"Status: {parsed['status']}")
    print(f"Success: {parsed['success']}")
    if parsed['exit_code'] is not None:
        print(f"Exit code: {parsed['exit_code']}")
    print(f"Errors: {len(parsed['errors'])}")
    print(f"Warnings: {len(parsed['warnings'])}")
    print(f"Output lines: {parsed['output_lines']}")
    print(f"Parsed data saved to: {parsed_file}")

    # Exit code based on success
    return 0 if parsed["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
