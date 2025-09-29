# Shopify Platform Fundamentals

This repository packages the Shopify Platform Fundamentals book as a Hugo Book site. Each chapter maps modern Shopify concepts to familiar full-stack patterns so you can move from fundamentals to advanced monetization strategies with confidence.

## Project Structure
```
.
├── content/
│   ├── _index.md
│   └── docs/
├── static/
├── themes/
├── hugo.toml
└── .github/workflows/
```

## Quick Start
1. `git init`
2. `git remote add origin https://github.com/<GITHUB-USER>/<REPO-NAME>.git`
3. `git submodule add https://github.com/alex-shpak/hugo-book themes/hugo-book`
4. `git config core.hooksPath .githooks`
5. `git add .`
6. `git commit -m "Initial commit: Shopify Platform Fundamentals with Hugo Book theme"`
7. `git push -u origin main`

## Local Development
- Install Hugo Extended 0.146.0 or newer
- `hugo server -D`
- Visit `http://localhost:1313` to preview drafts and recent changes

## Chapter Workflow
- Edit or add chapters once in the repo root (`NN - Title.md`). The sync script keeps file names aligned with the first H1.
- On commit, the pre-commit hook runs `scripts/sync_chapters.py` to refresh `content/docs/chapter-NN.md` plus the navigation lists.
- To trigger the sync manually, run `python scripts/sync_chapters.py` before staging.
- When introducing a new chapter, create the root file with the next index and heading; the hook generates the Hugo copy and updates indexes automatically.

## Features
- Hugo Book theme with instant section navigation and built-in search
- Automated duplication for clean GitHub reading and Hugo rendering
- GitHub Actions workflow for continuous deployment to GitHub Pages
- Ready-to-use dark mode, syntax highlighting, and responsive layout

## Customization
- Adjust site metadata, menus, and theme params in `hugo.toml`
- Extend styling or shortcodes by adding assets under `static/` or layouts in `layouts/`
- Update the sync script or hook if you need alternative naming or index behavior

### Verification
- `hugo --minify`
- `gh run list --workflow=hugo.yml`
