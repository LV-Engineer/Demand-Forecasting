# Git Workflow

Goal: keep the **full history** of the project (many small commits that tell the story of the work), not one big commit at the end. Recruiters can open the commit log and see how the project grew: EDA, baseline, models, threshold, A/B design, README.

## 1. Core principles

- **Commit early, commit often.** One commit = one logical change that can be described in one line.
- **Never rewrite published history.** No `git push --force` on `main`, no squashing everything into one commit. History is part of the portfolio.
- **The repo should work at every commit.** Do not commit a half-broken state to `main`.
- **Commit code, not artifacts.** Data, models and the virtual environment are reproducible from code and seeds (see `.gitignore`).

## 2. Branching

`main` is always in a working state. Each step of `03_Work_Plan.md` gets a short branch named `<type>/<short-name>` (lowercase, words separated by hyphens). The `<type>` is the same set of prefixes as in commit messages (see section 3).

| Plan step | Branch |
| --- | --- |
| 1-2 Problem definition, EDA | `feat/eda` |
| 3 Preprocessing pipeline | `feat/preprocessing` |
| 4 Baseline | `feat/baseline` |
| 5 RF / XGBoost | `feat/classical-models` |
| 6 PyTorch MLP | `feat/mlp` |
| 7 Threshold by business cost | `feat/threshold` |
| 8 Interpretation | `feat/interpretation` |
| 9 A/B test design | `docs/ab-test-design` |
| 10 README, cleanup | `docs/readme` |

Other examples: `fix/scaler-leakage`, `chore/add-xgboost`, `refactor/pipeline-module`.

Naming is enforced by convention only: GitHub rulesets on this account have no branch-name restriction.

Flow for each step:

```bash
git switch main
git pull
git switch -c feat/baseline          # create the step branch
# ... work, several commits ...
git push -u origin feat/baseline     # back up the branch on GitHub
git switch main
git merge --no-ff feat/baseline      # keep the branch visible in history
git push
git branch -d feat/baseline          # optional cleanup
```

Why `--no-ff`: it creates a merge commit, so the graph shows "this group of commits was the baseline step". With a fast-forward merge the branch structure disappears.

Optional: open a Pull Request on GitHub for each branch and merge it there. It leaves a readable record of the decisions, even for a solo project.

### Protection on GitHub

A ruleset on the default branch (`main`) enables **Restrict deletions** and **Block force pushes**, so the history of `main` cannot be rewritten or removed. Feature branches are not protected and can be deleted freely after merging.

## 3. Commit messages

English, imperative mood, [Conventional Commits](https://www.conventionalcommits.org/) prefixes:

| Prefix | Use for |
| --- | --- |
| `feat:` | new functionality (a model, a pipeline, a script) |
| `fix:` | a bug fix (for example a data leakage fix) |
| `docs:` | README, brief, experiment log, work plan |
| `refactor:` | code restructuring without behavior change |
| `chore:` | environment, dependencies, `.gitignore` |
| `test:` | tests |

Examples:

```
feat: add logistic regression baseline
fix: fit scaler on train split only to remove leakage
docs: log experiment 3 (XGBoost, ROC-AUC 0.84)
chore: add scikit-learn and xgboost with uv
```

Keep the first line under about 70 characters. Add a body only when the "why" is not obvious.

## 4. What to commit and when

Commit after each of these moments:

- a new module/script/notebook section works;
- an experiment finished: **code and the `02_Experiment_Log.md` row together**, or in two consecutive commits;
- a decision changed (metric, threshold, split): commit the change plus the docs update;
- a plan step finished: tick it in `03_Work_Plan.md` (`docs: complete step 4`).

Do **not** commit:

- `.venv/`, `data/raw/`, `models/`, `*.pkl`, `.env` (already in `.gitignore`);
- notebooks with huge outputs (clear outputs or keep them small);
- secrets, tokens, personal data.

## 5. Review before every commit

```bash
git status          # what changed
git diff            # exactly what changed (unstaged)
git add <files>     # stage deliberately, avoid blind `git add .`
git diff --staged   # what is about to be committed
git commit -m "feat: ..."
```

Staging files selectively lets you split a messy working session into several clean commits (`git add -p` for parts of a file).

## 6. Tags (milestones)

Mark important points so they are easy to find:

```bash
git tag -a v0.1-baseline -m "Baseline done: logistic regression, ROC-AUC X"
git tag -a v1.0 -m "Project complete"
git push --tags
```

Suggested tags: `v0.1-baseline`, `v0.2-classical-models`, `v0.3-mlp`, `v1.0`.

## 7. Undoing mistakes safely

| Situation | Command |
| --- | --- |
| Unstage a file | `git restore --staged <file>` |
| Discard local edits in a file | `git restore <file>` (destructive, edits are lost) |
| Fix the last **unpushed** commit message | `git commit --amend` |
| Undo a **pushed** commit | `git revert <hash>` (adds a new commit, history stays) |
| Look at history | `git log --oneline --graph --decorate` |

Rule: `amend`/`rebase` only for commits that are not pushed yet. After a push use `revert`.

## 8. Checklist for a healthy history

- [ ] more than 30 meaningful commits by the end of the project
- [ ] each plan step visible as a branch/merge
- [ ] commit messages follow the convention
- [ ] no data, models or secrets in history
- [ ] tags at the main milestones
- [ ] the experiment log and the work plan are updated in commits alongside the code
