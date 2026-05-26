#!/bin/bash
# Autonomous Development Protocol: Git Hook Installer

echo "Installing Git Hooks..."
cp .git/hooks/post-commit .git/hooks/post-commit.tmp 2>/dev/null
cat <<HOOK > .git/hooks/post-commit
#!/bin/bash
echo "--- Post-Commit: Triggering Autonomous Repository Sync Protocol ---"
python3 $(pwd)/sync_repo.py
HOOK
chmod +x .git/hooks/post-commit
echo "Done. post-commit hook installed."
