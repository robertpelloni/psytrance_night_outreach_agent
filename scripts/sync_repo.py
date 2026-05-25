import subprocess
import os
import sys

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ai_engine import AIEngine

ai = AIEngine()

def run_command(command, cwd=None):
    print(f"  [EXEC] {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr.strip()}")
    return result

def attempt_ai_resolution(cwd=None):
    # Find conflicted files
    status = run_command(["git", "status", "--porcelain"], cwd=cwd).stdout
    conflicted_files = []
    for line in status.splitlines():
        if line.startswith("UU"):
            conflicted_files.append(line[3:])

    if not conflicted_files:
        return False

    for filepath in conflicted_files:
        full_path = os.path.join(cwd or os.getcwd(), filepath)
        with open(full_path, "r") as f:
            content = f.read()

        resolved = ai.resolve_merge_conflict(content)
        if resolved:
            # Strip markdown if any
            if resolved.startswith("```"):
                lines = resolved.splitlines()
                if lines[0].startswith("```"):
                    resolved = "\n".join(lines[1:-1])

            with open(full_path, "w") as f:
                f.write(resolved)
            run_command(["git", "add", filepath], cwd=cwd)
        else:
            return False

    # Try to commit the resolution
    res = run_command(["git", "commit", "-m", "Resolve merge conflicts via AI"], cwd=cwd)
    return res.returncode == 0

def sync():
    print("=== Starting Repository Sync Protocol ===")

    # 1. Fetch All and ensure all remote branches are tracked locally
    print("\n[1/6] Fetching remotes and tracking branches...")
    run_command(["git", "fetch", "--all", "--tags"])

    # Robust branch discovery using --format
    raw_remote_branches = run_command(["git", "branch", "-r", "--format=%(refname:short)"]).stdout.splitlines()
    for rb in raw_remote_branches:
        rb = rb.strip()
        if rb.startswith("origin/") and "HEAD" not in rb:
            local_name = rb.replace("origin/", "")
            # Only track if not already existing locally
            run_command(["git", "branch", "--track", local_name, rb])

    # 2. Identify Upstream
    print("\n[2/6] Syncing with upstream (if exists)...")
    remotes = run_command(["git", "remote"]).stdout.split()
    if "upstream" in remotes:
        run_command(["git", "checkout", "main"])
        run_command(["git", "merge", "upstream/main"])
    else:
        print("  No upstream remote found. Skipping.")

    # 3. Recursive Submodule Update
    print("\n[3/6] Updating submodules recursively...")
    run_command(["git", "submodule", "update", "--init", "--recursive", "--remote"])

    # 4. Forward Merge (Features to Main)
    print("\n[4/6] Reconciling feature branches (Forward Merge)...")
    local_branches = run_command(["git", "branch", "--format=%(refname:short)"]).stdout.splitlines()
    for branch in local_branches:
        branch = branch.strip()
        if branch not in ["main", "master", ""] and "HEAD" not in branch:
            print(f"Interrogating branch: {branch}")
            # Check if it has unique commits
            diff = run_command(["git", "rev-list", f"main..{branch}"]).stdout.strip()
            if diff:
                print(f"Merging unique progress from {branch} into main...")
                run_command(["git", "checkout", "main"])
                merge_res = run_command(["git", "merge", branch])
                if merge_res.returncode != 0:
                    print(f"Conflict merging {branch}. Attempting AI resolution...")
                    if not attempt_ai_resolution(cwd=os.getcwd()):
                        print(f"AI resolution failed for {branch}. Aborting merge.")
                        run_command(["git", "merge", "--abort"])
                    else:
                        print(f"Successfully resolved conflict for {branch} via AI.")
                else:
                    print(f"Successfully merged {branch} into main.")

    # 5. Reverse Merge (Main back to Features) and push updates
    print("\n[5/6] Syncing main back to feature branches (Reverse Merge)...")
    for branch in local_branches:
        branch = branch.strip()
        if branch not in ["main", "master", ""] and "HEAD" not in branch:
            print(f"  Syncing main -> {branch}")
            run_command(["git", "checkout", branch])
            merge_res = run_command(["git", "merge", "main"])
            if merge_res.returncode != 0:
                print(f"Conflict syncing main into {branch}. Attempting AI resolution...")
                if not attempt_ai_resolution(cwd=os.getcwd()):
                    print(f"AI resolution failed for {branch}. Aborting merge.")
                    run_command(["git", "merge", "--abort"])
                    run_command(["git", "checkout", "main"])
                else:
                    print(f"Successfully synced main into {branch} (AI resolved).")
                    run_command(["git", "push", "origin", branch])
            else:
                print(f"Successfully synced main into {branch}.")
                run_command(["git", "push", "origin", branch])

    # 6. Final Push for main and submodules
    print("\n[6/6] Finalizing and pushing changes...")
    run_command(["git", "checkout", "main"])
    run_command(["git", "push", "origin", "main"])
    run_command(["git", "submodule", "foreach", "git push origin main || true"])

    print("\n=== Repository Sync Protocol Complete ===")

if __name__ == "__main__":
    sync()
