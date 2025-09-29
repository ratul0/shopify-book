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
4. `git add .`
5. `git commit -m "Initial commit: Shopify Platform Fundamentals with Hugo Book theme"`
6. `git push -u origin main`

## Local Development
- Install Hugo Extended 0.146.0 or newer
- `hugo server -D`
- Visit `http://localhost:1313` to preview drafts and recent changes

## Features
- Hugo Book theme with instant section navigation and built-in search
- Dual chapter copies for clean GitHub reading and Hugo rendering
- GitHub Actions workflow for continuous deployment to GitHub Pages
- Ready-to-use dark mode, syntax highlighting, and responsive layout

## Customization
- Add or reorder chapters by updating the root Markdown files and letting the Hugo copies mirror them
- Adjust site metadata, menus, and theme params in `hugo.toml`
- Extend styling or shortcodes by adding assets under `static/` or layouts in `layouts/`

### Verification
- `hugo --minify`
- `gh run list --workflow=hugo.yml`
