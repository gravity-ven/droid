#!/usr/bin/env python3
"""
Claude Output Parser

Extracts structured data from Claude Code output files.
Detects status, errors, warnings, completions, and action items.
"""

import sys
import json
import re
from pathlib import Path


def parse_claude_output(file_path):
    """Parse Claude Code output file."""

    result = {
        "status": "unknown",
        "success": False,
        "errors": [],
        "warnings": [],
        "actions_needed": [],
        "completions": [],
        "metadata": {}
    }

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check for completion markers
        if "<<COMPLETE>>" in content or "Task completed" in content:
            result["status"] = "complete"
            result["success"] = True
        elif "<<ERROR>>" in content or "Error:" in content:
            result["status"] = "error"
            result["success"] = False
        elif "<<PENDING>>" in content:
            result["status"] = "pending"
            result["success"] = False
        else:
            result["status"] = "in_progress"
            result["success"] = False

        # Extract errors
        error_patterns = [
            r'Error:\s*(.+)',
            r'ERROR:\s*(.+)',
            r'<<ERROR>>\s*(.+)',
            r'Failed:\s*(.+)',
            r'Exception:\s*(.+)'
        ]

        for pattern in error_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                error_msg = match.group(1).strip()
                if error_msg and error_msg not in result["errors"]:
                    result["errors"].append(error_msg)

        # Extract warnings
        warning_patterns = [
            r'Warning:\s*(.+)',
            r'WARN:\s*(.+)',
            r'<<WARNING>>\s*(.+)'
        ]

        for pattern in warning_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                warn_msg = match.group(1).strip()
                if warn_msg and warn_msg not in result["warnings"]:
                    result["warnings"].append(warn_msg)

        # Extract action items
        action_patterns = [
            r'TODO:\s*(.+)',
            r'Action needed:\s*(.+)',
            r'Next step:\s*(.+)',
            r'Please:\s*(.+)'
        ]

        for pattern in action_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                action = match.group(1).strip()
                if action and action not in result["actions_needed"]:
                    result["actions_needed"].append(action)

        # Extract completions
        completion_patterns = [
            r'Completed:\s*(.+)',
            r'Done:\s*(.+)',
            r'Finished:\s*(.+)',
            r'Successfully:\s*(.+)'
        ]

        for pattern in completion_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                completion = match.group(1).strip()
                if completion and completion not in result["completions"]:
                    result["completions"].append(completion)

        # Extract metadata
        result["metadata"]["file_size"] = len(content)
        result["metadata"]["line_count"] = content.count('\n')
        result["metadata"]["has_errors"] = len(result["errors"]) > 0
        result["metadata"]["has_warnings"] = len(result["warnings"]) > 0
        result["metadata"]["has_actions"] = len(result["actions_needed"]) > 0

    except Exception as e:
        result["status"] = "error"
        result["success"] = False
        result["errors"].append(f"Failed to parse file: {str(e)}")

    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: parse_claude_output.py <output_file>", file=sys.stderr)
        return 1

    output_file = sys.argv[1]

    if not Path(output_file).exists():
        print(f"Error: File not found: {output_file}", file=sys.stderr)
        return 1

    # Parse output
    parsed = parse_claude_output(output_file)

    # Save parsed data
    parsed_file = f"{output_file}.parsed.json"
    with open(parsed_file, 'w') as f:
        json.dump(parsed, f, indent=2)

    # Print summary
    print(f"Status: {parsed['status']}")
    print(f"Success: {parsed['success']}")
    print(f"Errors: {len(parsed['errors'])}")
    print(f"Warnings: {len(parsed['warnings'])}")
    print(f"Actions needed: {len(parsed['actions_needed'])}")
    print(f"Parsed data saved to: {parsed_file}")

    # Exit code based on success
    return 0 if parsed["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
