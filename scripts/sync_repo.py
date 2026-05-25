import subprocess
import os
import sys

def run_command(command, cwd=None):
    print(f"  [EXEC] {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr.strip()}")
    return result

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
        if branch != "main" and branch != "" and "HEAD" not in branch:
            print(f"Interrogating branch: {branch}")
            # Check if it has unique commits
            diff = run_command(["git", "rev-list", f"main..{branch}"]).stdout.strip()
            if diff:
                print(f"Merging unique progress from {branch} into main...")
                run_command(["git", "checkout", "main"])
                merge_res = run_command(["git", "merge", branch])
                if merge_res.returncode != 0:
                    print(f"Conflict merging {branch}. Aborting merge.")
                    run_command(["git", "merge", "--abort"])
                else:
                    print(f"Successfully merged {branch} into main.")

    # 5. Reverse Merge (Main back to Features) and push updates
    print("\n[5/6] Syncing main back to feature branches (Reverse Merge)...")
    for branch in local_branches:
        branch = branch.strip()
        if branch != "main" and branch != "" and "HEAD" not in branch:
            print(f"  Syncing main -> {branch}")
            run_command(["git", "checkout", branch])
            merge_res = run_command(["git", "merge", "main"])
            if merge_res.returncode != 0:
                print(f"Conflict syncing main into {branch}. Aborting merge.")
                run_command(["git", "merge", "--abort"])
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
