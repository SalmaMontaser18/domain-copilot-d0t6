# AI Usage Log

How I used AI on this project, where it helped, where it misled me, and how I
caught the problems. Dates are 2026. Entries are added as work happens.

## 1. Tools and roles

| Tool | Used for |
|---|---|
| Claude (chat) | Reading the brief, planning the 6 days, step-by-step Git/Docker/CI instructions, code for the skeleton, LLM port, fake provider and fallback chain |
| A separate AI chat session (Claude) | Generating the synthetic medical documents and draft Q&A pairs |

## 2. What I delegated and what I did myself

| Area | Delegated to AI | Done by me |
|---|---|---|
| Project plan | Day-by-day breakdown, requirement explanations | Chose to follow it, adjusted order when time was short |
| Repository setup | Command sequences, file templates | Created the repo, ran every command, enabled branch protection, created issues, milestones and PRs |
| Skeleton, CI, Docker | Draft code and YAML | Created files, ran tests and lint locally, read CI logs, fixed failures |
| LLM provider port | Draft of port, fake adapter, fallback chain, tests | Reviewed, ran tests and lint, committed in small steps |
| Synthetic corpus | Text of the documents and draft Q&A | Saved files, fixed front-matter, moved Q&A out of documents, audited contradictions, committed |
| This log | Structure | Facts, verification, honesty about mistakes |

## 3. Where the AI was wrong or misled me

| Date | What the AI did wrong | How I found out | What I did | Lesson |
|---|---|---|---|---|
| 10-02 | Told me to run `git init` and `git remote add` although I had already cloned the repo. This created a stray `.git` in the parent folder. | `git add` failed with "not a git repository"; `ls -a` showed two repositories. | Deleted the extra `.git` and worked inside the cloned folder. | Check `git status` and where I am before running setup commands. |
| 10-02 | Wrote commands for Git Bash (`touch`, `mkdir -p`, `source`, `cp`) while I was working in PowerShell. | PowerShell reported `touch` as not recognized. | Switched to Git Bash in VS Code. | State the shell with every command and check the prompt. |
| 10-02 | Said the CI test job probably failed because of Python version differences in installed packages. This was a guess. | I opened the job log: the real cause was `ruff check` failing. | Fixed the lint errors. | Read the actual log before accepting a diagnosis. |
| 10-03 | Generated code using `from typing import Iterator`, which violates the project's ruff rule UP035. The first CI run on the LLM port PR failed. | Local `ruff check .` showed it, and the CI log listed three files. | Ran `ruff check . --fix` and committed the style fix. | Run `ruff check . && pytest` before every push. |
| 10-03 | The corpus prompt did not ask for raw Markdown, so the copied text lost its front-matter lines, `##` headings and table pipes. | Text pasted into `GL-01.md` had no `---` lines. | Asked the AI to resend as one code block and added that line to every later request. | Ask for raw output in a code block when the text is used as data. |
| 10-03 | In GL-01 the generated worked example contradicted the document's own rules. Clause 12.1: a 72-year-old started at 2.5 mg, but clause 4.4 gives that dose only at 75 or older or if frail. Clause 12.2: 134/80 was called on target, but clause 3.3 requires below 130/80. | Reading the document against its numbered rules. | Changed the age to 78 and the reading to 128/78. | Generated medical-style text is not self-consistent. Worked examples are where errors cluster. |
| 10-03 | Asked an AI to audit GL-02, GL-03, GL-03-v1 and GL-04 for internal contradictions. It reported none, and I accepted that without re-reading every clause. | AI audit prompt on each document. | Nothing to fix at that point. | An AI audit is not proof. I later found the swapped GL-03 files only by reading the PR diff myself. |

## 4. My own process errors

| Date | Error | Cause | Fix |
|---|---|---|---|
| 10-02 | Created `.github/workflows/ci.yml` inside a nested `.github/workflows/.github/workflows/` path | Created the file while a subfolder was open | Moved the file with `mv` and deleted the empty folder |
| 10-02 | A stray file named `witch main` appeared | Typo of `git switch main` | Deleted it before committing |
| 10-02 | Ran commands from the parent folder `F:\ITI Task` several times | Did not check the prompt | `cd` into the project folder first |
| 10-03 | Saved `.dockerignore` as `dockerignore` | Created the file without the leading dot | Renamed with `mv` |
| 10-03 | Docker commands failed: Docker Desktop was not running | Engine not started | Started Docker Desktop and waited for "Engine running" |
| 10-03 | `docker compose` failed with "no configuration file provided" | Ran it from the parent folder | Ran it from the project folder |
| 10-03 | Committed `errors.py` on local `main` instead of the feature branch | Did not check the current branch | `merge --ff-only` into the feature branch, then `git reset --hard origin/main`. Nothing was pushed to `main`; branch protection would have rejected it. |
| 10-03 | Created `data/golden/` inside `data/corpus/source/` by mistake | Created the file while a subfolder was selected | Moved the file to `data/golden/` and removed the nested folder |
| 10-06 | Content of GL-03 and GL-03-v1 was pasted into the wrong files, and the Q&A headings followed the wrong labels | Pasted two similar documents one after the other | Found by reading the PR diff before merging; swapped the files with `git mv` and checked `version` and `status` with grep |
| 10-06 | Placeholder text in this log was replaced with another word so a TODO check would pass | Wanted the grep check to stop reporting | Found while resolving a merge conflict; replaced with real content in a follow-up PR |

## 5. How I verify AI output

- Run `pytest` and `ruff check .` locally before pushing; CI repeats them.
- Read CI logs myself before applying a suggested fix.
- Check `git status`, the current branch and the folder before each commit.
- For generated documents: check every worked example against the numbered rules, then audit with a second prompt and confirm each reported clause by hand.
- Read the PR diff before merging.
- Dependency rule: an architecture test fails if domain or application import an SDK or web framework.

## 6. Not yet verified

- Local Python is 3.14 while CI and Docker use 3.12. No failure has been observed yet, but I have not checked `requirements.txt` for platform-specific packages.
- The synthetic documents have been audited for internal consistency only. Draft Q&A pairs have not been reviewed yet and must be reviewed before use in the golden set.