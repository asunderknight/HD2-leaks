import os
import json
import subprocess

# ====== CONFIG ======
folder_path = r"C:\Users\asund\Downloads\filediver_exports\Strings"
output_dir = os.path.join(folder_path, "by_language")
repo_dir = output_dir  # <-- The git repo will be initialized here
commit_message = "Auto-update merged language files"
# =====================

os.makedirs(output_dir, exist_ok=True)

merged_by_language = {}

def is_valid_json(data):
    return (
        isinstance(data, dict)
        and "Version" in data
        and "Language" in data
        and isinstance(data.get("Items"), list)
    )

# --- Merge files by language ---
for filename in sorted(os.listdir(folder_path)):
    if filename.lower().endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not is_valid_json(data):
                print(f"⚠️ Skipping corrupted file: {filename}")
                continue

            lang = (
                data["Language"].get("KnownName")
                or data["Language"].get("KnownFriendlyName")
                or "unknown"
            )

            if lang not in merged_by_language:
                merged_by_language[lang] = {"Version": 1, "Items": []}

            merged_by_language[lang]["Items"].extend(data.get("Items", []))

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

# --- Write outputs named by language ---
for lang, merged_data in merged_by_language.items():
    output_file = os.path.join(output_dir, f"{lang}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Created: {output_file}")

# --- GitHub automation ---
def run_git(cmd):
    """Run a git command in the repo_dir."""
    subprocess.run(["git"] + cmd, cwd=repo_dir, check=True)

try:
    # Initialize repo if not already
    if not os.path.exists(os.path.join(repo_dir, ".git")):
        run_git(["init"])
        # Replace with your GitHub repo URL after first manual push
        # run_git(["remote", "add", "origin", "git@github.com:USERNAME/REPO.git"])

    run_git(["add", "."])
    run_git(["commit", "-m", commit_message])
    # Push to GitHub (must have remote set & SSH/HTTPS auth configured)
    run_git(["push", "-u", "origin", "main"])
    print("🚀 Changes pushed to GitHub.")
except subprocess.CalledProcessError as e:
    print(f"⚠️ Git operation failed: {e}")
    print("Make sure the repository is initialized and remote is set correctly.")
