# ICLR 2027 Project Backup

**"All Memory Is Local: Measuring the Horizon of Persistent Test-Time Training"**

This repository contains the complete project backup for server migration.

## Directory Structure

```
.
├── All_Memory_Is_Local__...pdf   # Final paper PDF
├── paper/                         # LaTeX source
│   ├── main.tex                   # Main paper
│   ├── references.bib             # Bibliography
│   ├── figs/                      # Figures (PDF)
│   └── *.sty                      # Style files
├── ptt/                           # Main codebase
│   ├── run.py                     # Experiment runner
│   ├── ptt/                       # Core library
│   │   ├── fastweight.py          # Fast-weight manager
│   │   ├── runner.py              # Streaming evaluation
│   │   └── streams/               # Data streams
│   ├── scripts/                   # Experiment scripts
│   └── results/                   # Experiment results (JSON)
├── results/                       # Additional results
├── PROGRESS.md                    # Development progress log
├── REVISION_BLUEPRINT.md          # Revision planning
├── DRAFT_*.md                     # Paper draft sections
├── PAPER_OUTLINE_v3.md            # Paper outline
├── TTT_PAPER_OUTLINE_AND_CITATIONS.md
├── CROSSCHECK.md                  # Verification checklist
├── WRITING_CHECKLIST.md           # Writing checklist
├── figlib.py                      # Figure generation utilities
├── memory_excess.py               # Memory analysis scripts
└── week3_repo.py                  # Development script
```

## Notes

- **Excluded from backup**: Large data directories (repos/, repos50/, repos180/, repos_fresh/) and zip archives
- **Code release**: The clean public release is at: https://github.com/FlowerFire7/All-Memory-Is-Local-Measuring-the-Horizon-of-Persistent-Test-Time-Training

## To Restore on New Server

```bash
git clone https://github.com/FlowerFire7/ICLR2027.git
cd ICLR2027

# Re-download test repositories
cd ptt/ptt
python scripts/fetch_repos.py --out repos50 --max 50
```
