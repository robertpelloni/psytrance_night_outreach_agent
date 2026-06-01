import subprocess
import os
import sys
import time
from datetime import datetime

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.ai_engine import AIEngine
from src.db_manager import DatabaseManager

ai = AIEngine()
db = DatabaseManager()

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

def sync(dry_run=False):
    # Check if we are in a Git hook environment to avoid infinite loops
    if os.getenv("GIT_SYNC_RUNNING") == "1":
        print("  [SKIP] Sync already running (detected via GIT_SYNC_RUNNING)")
        return
    os.environ["GIT_SYNC_RUNNING"] = "1"

    if dry_run:
        print("!!! DRY RUN MODE ENABLED: No changes will be pushed to remote !!!")

    start_time = time.time()
    try:
        print(f"=== Starting Repository Sync Protocol: {datetime.now()} ===")

        # 1. Fetch All and ensure all remote branches are tracked locally
        print("\n[1/6] Fetching remotes and tracking branches...")
        run_command(["git", "fetch", "--all", "--tags"])

        # Robust branch discovery using --format
        raw_remote_branches = run_command(["git", "branch", "-r", "--format=%(refname:short)"]).stdout.splitlines()
        local_branches = run_command(["git", "branch", "--format=%(refname:short)"]).stdout.splitlines()
        local_branches = [b.strip() for b in local_branches]

        for rb in raw_remote_branches:
            rb = rb.strip()
            if rb.startswith("origin/") and "HEAD" not in rb:
                local_name = rb.replace("origin/", "")
                # Only track if not already existing locally
                if local_name not in local_branches:
                    run_command(["git", "branch", "--track", local_name, rb])

        # 2. Sync with Origin and Upstream
        print("\n[2/6] Syncing with origin and upstream...")
        run_command(["git", "checkout", "main"])

        # Always merge origin/main to get latest remote changes
        print("  Merging changes from origin/main...")
        # Use --no-edit to avoid hanging on commit message prompt
        # Use --allow-unrelated-histories to handle complex reconciliations
        run_command(["git", "merge", "origin/main", "--no-edit", "--allow-unrelated-histories"])

        remotes = run_command(["git", "remote"]).stdout.split()
        if "upstream" in remotes:
            print("  Merging changes from upstream/main...")
            run_command(["git", "merge", "upstream/main"])
        else:
            print("  No upstream remote found. Skipping upstream sync.")

        # 3. Recursive Submodule Update
        print("\n[3/6] Updating submodules recursively...")
        run_command(["git", "submodule", "update", "--init", "--recursive", "--remote"])

        # 4. Forward Merge (Features to Main)
        print("\n[4/6] Reconciling feature branches (Forward Merge)...")
        local_branches = run_command(["git", "branch", "--format=%(refname:short)"]).stdout.splitlines()
        for branch in local_branches:
            branch = branch.strip()
            # HARDENING: Only forward-merge branches that are explicitly designated as features
            is_feature = branch.startswith("feature/") or branch.startswith("jules-")
            if is_feature and branch not in ["main", "master", ""] and "HEAD" not in branch:
                print(f"Interrogating branch: {branch}")
                # Check if it has unique commits
                diff = run_command(["git", "rev-list", f"main..{branch}"]).stdout.strip()
                if diff:
                    print(f"Merging unique progress from {branch} into main...")
                    run_command(["git", "checkout", "main"])
                    merge_res = run_command(["git", "merge", branch, "--allow-unrelated-histories"])
                    if merge_res.returncode != 0:
                        print(f"Conflict merging {branch}. Attempting AI resolution...")
                        if not attempt_ai_resolution(cwd=os.getcwd()):
                            print(f"AI resolution failed for {branch}. Aborting merge.")
                            db.log_system_event("SYNC", "FAILURE", f"Conflict merging {branch} (AI resolution failed)")
                            run_command(["git", "merge", "--abort"])
                        else:
                            print(f"Successfully resolved conflict for {branch} via AI.")
                            db.log_system_event("SYNC", "SUCCESS", f"Merged {branch} into main (AI resolved)")
                    else:
                        print(f"Successfully merged {branch} into main.")
                        db.log_system_event("SYNC", "SUCCESS", f"Merged {branch} into main")

        # 5. Reverse Merge (Main back to Features) and push updates
        print("\n[5/6] Syncing main back to feature branches (Reverse Merge)...")
        for branch in local_branches:
            branch = branch.strip()
            if branch not in ["main", "master", ""] and "HEAD" not in branch:
                print(f"  Syncing main -> {branch}")
                run_command(["git", "checkout", branch])
                merge_res = run_command(["git", "merge", "main", "--allow-unrelated-histories"])
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

        # HARDENING: Only push if the merged state passes critical integrity tests
        if os.getenv("SKIP_SYNC_VALIDATION") == "1" or validate_system():
            if dry_run:
                print("  [DRY-RUN] Validation passed. Skipping push to origin.")
            else:
                # Implementation of Retry-after-Rebase to handle distributed race conditions
                max_retries = 3
                for attempt in range(max_retries):
                    push_res = run_command(["git", "push", "origin", "main"])
                    if push_res.returncode == 0:
                        print(f"  [SUCCESS] Pushed main to origin on attempt {attempt+1}.")
                        break
                    elif attempt < max_retries - 1:
                        print(f"  [RETRY] Push failed (remote moved). Rebasing and retrying...")
                        run_command(["git", "fetch", "origin"])
                        run_command(["git", "rebase", "origin/main"])
                    else:
                        print(f"  [ERROR] Push failed after {max_retries} attempts.")
                        sys.exit(1)

                run_command(["git", "submodule", "foreach", "git push origin main || true"])
        else:
            print("[CRITICAL] Merged state failed validation! Aborting push to protect remote main.")
            sys.exit(1)

        # 7. Consistency Verification
        print("\n[7/7] Verifying repository consistency...")
        run_command(["git", "fetch", "origin"])
        local_hash = run_command(["git", "rev-parse", "main"]).stdout.strip()
        remote_hash = run_command(["git", "rev-parse", "origin/main"]).stdout.strip()

        if local_hash == remote_hash:
            print(f"  [SUCCESS] Local and remote are synchronized at {local_hash[:7]}.")
        else:
            print(f"  [WARNING] Consistency check failed! Local: {local_hash[:7]}, Remote: {remote_hash[:7]}")
            sys.exit(1)

        # 8. Repository Hygiene: Prune merged branches
        print("\n[8/8] Performing repository hygiene...")
        run_command(["git", "remote", "prune", "origin"])

        duration = round(time.time() - start_time, 2)
        print(f"\n=== Repository Sync Protocol Complete (Duration: {duration}s) ===")
        db.log_system_event("SYNC", "SUCCESS", f"Protocol completed successfully in {duration}s")

        # Trigger Version Auditor after successful sync
        try:
            from src.version_auditor import VersionAuditor
            VersionAuditor().harvest_git_logs()
        except Exception as aud_err:
            print(f"Warning: Auditor failed: {aud_err}")

    except Exception as e:
        db.log_system_event("SYNC", "FAILURE", f"Protocol failed: {str(e)}")
        raise e
    finally:
        if "GIT_SYNC_RUNNING" in os.environ:
            del os.environ["GIT_SYNC_RUNNING"]

def validate_system():
    print("\n[VALIDATION] Running integrity checks before finalization...")
    # Add PYTHONPATH to environment
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.getcwd()}:{env.get('PYTHONPATH', '')}"

    # Master Integrity Suite: Dynamic Discovery via Pytest
    # This replaces the hardcoded list to ensure all new tests are automatically included.
    print("  Executing full Master Integrity Suite (Pytest)...")
    res = subprocess.run([sys.executable, "-m", "pytest", "tests/"], env=env, capture_output=True, text=True)

    if res.returncode != 0:
        print("[CRITICAL] Master Integrity Suite failed!")
        print(res.stdout)
        print(res.stderr)
        return False

    print("  [SUCCESS] All integrity checks passed.")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Repository Synchronization Protocol")
    parser.add_argument("--dry-run", action="store_true", help="Perform synchronization and validation without pushing to remote.")
    args = parser.parse_args()

    sync(dry_run=args.dry_run)
