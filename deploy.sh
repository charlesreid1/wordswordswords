#!/bin/bash

set -euo pipefail

# Check for command line flag `--dry-run`
DRY_RUN=""
if [[ $# > 0 ]]; then
    if [[ "$1" == "--dry-run" ]]; then
        DRY_RUN="--dry-run"
    else
        echo "Error: unrecognized argument provided."
        echo "Only valid input argument is --dry-run."
        exit 1;
    fi
fi

# Use the origin remote URL
REMOTE_URL=$(git config --get remote.origin.url)
if [[ -z "$REMOTE_URL" ]]; then
    echo "Error: could not determine remote origin URL."
    exit 1
fi

echo "Cloning repo ${REMOTE_URL} (gh-pages branch) into pelican/output..."

rm -fr pelican/output
git clone -b gh-pages "${REMOTE_URL}" pelican/output

# Clean out old rendered files, but leave .git directory
rm -fr pelican/output/*

echo "Generating pelican content..."
make all

(
echo "Committing new content..."
cd pelican/output

git config user.name "Deployment Orchestrator"
git config user.email "orchestrator@wordswordswords.local"

git add -A .

git commit -a -m "Automatic deploy at $(date -u +"%Y-%m-%d-%H-%M-%S")" || true

RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "Git commit step succeeded"
else
    echo "Git commit step failed. Maybe no changes?"
    exit 1
fi

if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "Skipping push step, --dry-run flag present"
else
    echo "Pushing to remote"
    git push origin gh-pages
fi
)

echo "Cleaning up"
rm -fr pelican/output
