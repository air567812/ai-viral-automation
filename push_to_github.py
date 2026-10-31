"""
Pure-Python GitHub Pusher using Dulwich (zero external Git.exe required).
Usage:
    python push_to_github.py https://github.com/YOUR_USER/YOUR_REPO.git --token YOUR_GITHUB_PAT
"""
import os
import sys
import argparse
from dulwich import porcelain
from dulwich.repo import Repo

def main():
    parser = argparse.ArgumentParser(description="Push Autonomous AI Reels to GitHub")
    parser.add_argument("repo_url", help="GitHub repository URL (e.g. https://github.com/user/repo.git)")
    parser.add_argument("--token", help="GitHub Personal Access Token (for passwordless authentication)")
    parser.add_argument("--branch", default="main", help="Target branch (default: main)")
    
    args = parser.parse_args()
    repo_url = args.repo_url.strip()

    if args.token and "github.com" in repo_url:
        # Embed token into URL for authenticated HTTPS push
        clean = repo_url.replace("https://", "")
        repo_url = f"https://oauth2:{args.token}@{clean}"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Opening local Git repository at {base_dir}...")
    repo = Repo(base_dir)

    print("Staging all updated project files...")
    porcelain.add(base_dir, paths=["."])

    try:
        porcelain.commit(base_dir, message=b"feat: autonomous AI viral reels automation platform", committer=b"AI Assistant <ai@antigravity.local>", author=b"AI Assistant <ai@antigravity.local>")
        print("Committed latest project files.")
    except Exception as e:
        print("Working tree clean or commit already made.")

    print(f"Pushing to remote {args.repo_url} on branch '{args.branch}'...")
    try:
        refspec = f"refs/heads/{args.branch}:refs/heads/{args.branch}".encode("utf-8")
        porcelain.push(base_dir, repo_url, refspecs=[refspec])
        print("\n=======================================================")
        print("SUCCESS! Successfully pushed to GitHub.")
        print("Navigate to the 'Actions' tab in your GitHub repository")
        print("to see the autonomous 6-hour scheduler and CI running!")
        print("=======================================================")
    except Exception as e:
        print(f"\nPush encountered error: {e}")
        print("If authenticating with username/password, use a GitHub Personal Access Token (PAT):")
        print("  python push_to_github.py <repo_url> --token <your_token>")

if __name__ == "__main__":
    main()
