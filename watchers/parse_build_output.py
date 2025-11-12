#!/usr/bin/env python3
"""
Build Output Parser

Parses build logs to detect success/failure, errors, warnings, and build metrics.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime


def parse_build_output(file_path):
    """Parse build output file."""

    result = {
        "status": "unknown",
        "success": False,
        "errors": [],
        "warnings": [],
        "build_time": None,
        "error_count": 0,
        "warning_count": 0,
        "metadata": {}
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Detect build success/failure
        success_markers = [
            "Build succeeded",
            "BUILD SUCCESS",
            "BUILD SUCCESSFUL",
            "Compilation successful",
            r'\d+ succeeded',
            "All builds completed successfully"
        ]

        failure_markers = [
            "Build failed",
            "BUILD FAILED",
            "BUILD FAILURE",
            "Compilation failed",
            r'\d+ failed',
            "Error:"
        ]

        # Check success
        for marker in success_markers:
            if re.search(marker, content, re.IGNORECASE):
                result["status"] = "success"
                result["success"] = True
                break

        # Check failure (overrides success if found)
        for marker in failure_markers:
            if re.search(marker, content, re.IGNORECASE):
                result["status"] = "failed"
                result["success"] = False
                break

        # Extract errors
        error_patterns = [
            r'error\s+([A-Z0-9]+):\s*(.+)',  # C#/C++ style: error CS1234: message
            r'ERROR:\s*(.+)',                 # Generic ERROR:
            r'Error:\s*(.+)',                 # Generic Error:
            r'FAILED:\s*(.+)',                # FAILED:
            r'(\w+\.cs)\((\d+),(\d+)\):\s*error\s+([A-Z0-9]+):\s*(.+)',  # C# with location
        ]

        for pattern in error_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                if len(match.groups()) == 1:
                    error_msg = match.group(1).strip()
                elif len(match.groups()) == 2:
                    error_code = match.group(1) if match.group(1) else ""
                    error_msg = match.group(2).strip()
                else:
                    error_msg = ' '.join(match.groups()).strip()

                if error_msg and error_msg not in result["errors"]:
                    result["errors"].append(error_msg)

        result["error_count"] = len(result["errors"])

        # Extract warnings
        warning_patterns = [
            r'warning\s+([A-Z0-9]+):\s*(.+)',  # C#/C++ style
            r'WARNING:\s*(.+)',                 # Generic WARNING:
            r'Warning:\s*(.+)',                 # Generic Warning:
            r'(\w+\.cs)\((\d+),(\d+)\):\s*warning\s+([A-Z0-9]+):\s*(.+)',  # C# with location
        ]

        for pattern in warning_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                if len(match.groups()) == 1:
                    warn_msg = match.group(1).strip()
                elif len(match.groups()) == 2:
                    warn_code = match.group(1) if match.group(1) else ""
                    warn_msg = match.group(2).strip()
                else:
                    warn_msg = ' '.join(match.groups()).strip()

                if warn_msg and warn_msg not in result["warnings"]:
                    result["warnings"].append(warn_msg)

        result["warning_count"] = len(result["warnings"])

        # Extract build time
        time_patterns = [
            r'Build time:\s*(\d+\.?\d*)\s*(\w+)',
            r'Time Elapsed\s+(\d{2}):(\d{2}):(\d{2})',
            r'Finished in\s+(\d+\.?\d*)\s*(\w+)',
            r'Total time:\s*(\d+\.?\d*)\s*(\w+)'
        ]

        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    result["build_time"] = f"{match.group(1)} {match.group(2)}"
                elif len(match.groups()) == 3:
                    hours, mins, secs = match.groups()
                    result["build_time"] = f"{hours}h {mins}m {secs}s"
                break

        # Extract metadata
        result["metadata"]["file_size"] = len(content)
        result["metadata"]["line_count"] = content.count('\n')

        # Detect build system
        if "MSBuild" in content or ".csproj" in content:
            result["metadata"]["build_system"] = "MSBuild"
        elif "make" in content or "Makefile" in content:
            result["metadata"]["build_system"] = "make"
        elif "gradle" in content:
            result["metadata"]["build_system"] = "gradle"
        elif "npm" in content or "yarn" in content:
            result["metadata"]["build_system"] = "npm/yarn"
        elif "cargo" in content:
            result["metadata"]["build_system"] = "cargo"
        elif "mojo build" in content:
            result["metadata"]["build_system"] = "mojo"

    except Exception as e:
        result["status"] = "error"
        result["success"] = False
        result["errors"].append(f"Failed to parse build output: {str(e)}")

    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: parse_build_output.py <build_log>", file=sys.stderr)
        return 1

    build_log = sys.argv[1]

    if not Path(build_log).exists():
        print(f"Error: File not found: {build_log}", file=sys.stderr)
        return 1

    # Parse build output
    parsed = parse_build_output(build_log)

    # Save parsed data
    parsed_file = f"{build_log}.parsed.json"
    with open(parsed_file, 'w') as f:
        json.dump(parsed, f, indent=2)

    # Print summary
    print(f"Status: {parsed['status']}")
    print(f"Success: {parsed['success']}")
    print(f"Errors: {parsed['error_count']}")
    print(f"Warnings: {parsed['warning_count']}")
    if parsed['build_time']:
        print(f"Build time: {parsed['build_time']}")
    print(f"Parsed data saved to: {parsed_file}")

    # Exit code based on success
    return 0 if parsed["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
