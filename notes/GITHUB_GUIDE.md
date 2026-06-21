# GitHub Guide — Olist E-Commerce Analysis
# WAP 228 | OSTIM Technical University

---

## Quick Git Workflow

### First Time Setup
```bash
# Configure your identity (do this once)
git config --global user.name "Your Name"
git config --global user.email "your.email@ostim.edu.tr"
```

### Daily Workflow
```bash
# 1. Check what changed
git status

# 2. Stage specific files
git add src/main.py
# OR stage everything
git add .

# 3. Commit with a meaningful message
git commit -m "feat: Add monthly revenue analysis query"

# 4. Push to GitHub
git push origin main
```

---

## Commit Message Conventions

Use these prefixes to demonstrate professional git workflow:

| Prefix | When to use |
|--------|-------------|
| `feat:` | Adding new functionality |
| `fix:` | Fixing a bug |
| `docs:` | Documentation changes |
| `style:` | Code formatting (no logic change) |
| `refactor:` | Refactoring code |
| `test:` | Adding or modifying tests |
| `chore:` | Build, deps, config changes |

### Example Commit History (Target: 15-20 commits)
```
feat: Initial project setup — requirements, gitignore, folder structure
feat: Database schema — 7 tables with FK relationships and indexes
feat: CSV data loading module (database.py)
feat: Add monthly revenue trend query
feat: Add top product categories analysis query
feat: Add geographic sales distribution query
feat: Add payment method breakdown query
feat: Add delivery time analysis query
feat: Add customer satisfaction vs delivery query
feat: Add seller performance ranking query
feat: Add seasonal patterns query
feat: Add customer retention analysis query
feat: Add price analysis by category query
feat: Python analysis module — execute all 10 queries (analysis.py)
feat: Visualizations module — 7 professional charts (visualizations.py)
feat: Main pipeline orchestrator (main.py)
docs: Analysis report with key findings and recommendations
docs: Comprehensive README with setup guide and architecture
polish: Final code review — add docstrings and inline comments
chore: Final test run — all charts generated, pipeline verified
```

---

## Making the Repository Public

1. Go to your repository on GitHub
2. Click **Settings** (top right)
3. Scroll to **Danger Zone**
4. Click **Change visibility** → **Make public**
5. Confirm

---

## Checking Your Commit History

```bash
# One-line summary of all commits
git log --oneline

# With graph (shows branches)
git log --oneline --graph --all

# Detailed view of last 5 commits
git log -5
```

---

## Useful Commands

```bash
# Undo the last commit (keep changes)
git reset --soft HEAD~1

# See what changed in a file
git diff src/main.py

# Revert a file to last commit state
git checkout -- src/analysis.py

# Create and switch to a new branch
git checkout -b feature/new-chart

# Merge branch back to main
git checkout main
git merge feature/new-chart
```
