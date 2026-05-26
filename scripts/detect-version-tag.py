#!/usr/bin/env python3

import subprocess
import re
import sys
import os


def get_current_branch():
    if "BUILDKITE_BRANCH" in os.environ:
        return os.getenv("BUILDKITE_BRANCH").strip()
    result = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def get_latest_version_tag():
    result = subprocess.run(
        ['git', 'tag', '--sort=-version:refname'],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    pattern = re.compile(r'^(\d+\.\d+\.\d+)$')
    for tag in result.stdout.strip().split('\n'):
        m = pattern.match(tag) if tag else None
        if m:
            return m.group(1)
    return None


def extract_version_from_branch(branch_name):
    m = re.match(r'^release/(\d+\.\d+\.\d+)$', branch_name)
    return m.group(1) if m else None


def main():
    branch = get_current_branch()
    if branch == 'main':
        version = get_latest_version_tag()
        if version is None:
            sys.stderr.write("Error: Could not find version tag on main branch\n")
            sys.exit(1)
    elif branch.startswith('release/'):
        version = extract_version_from_branch(branch)
        if version is None:
            sys.stderr.write("Error: Could not extract version from release branch: {}\n".format(branch))
            sys.exit(1)
    else:
        sys.stderr.write("Error: Not on main or release branch (current: {})\n".format(branch))
        sys.exit(1)
    print(version)


if __name__ == '__main__':
    main()
