# AI Usage Log

| Date | Task | Delegated to AI | Done by me | Where the AI misled me | How I verified |
|---|---|---|---|---|---|
| 2026-10-02 | Repo setup, Git, branch protection, PR flow | Planning, step-by-step commands | Executed every step, created issues and PRs | Gave `git init` + `git remote add` steps although the repo was already cloned, which created a stray `.git` in the parent folder | `git status` showed "not a git repository"; `ls -a` revealed two repos; removed the extra `.git` and worked inside the cloned folder |