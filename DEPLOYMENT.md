# Deployment Guide

## Checklist
- Hugo extended 0.146.0 installed locally or on CI
- Theme submodule added and initialized
- `baseURL` in `hugo.toml` updated to match the GitHub Pages URL
- GitHub Pages enabled for the repository
- Secrets and branch protections configured as needed

## Add the Hugo Book Theme
```bash
git submodule add https://github.com/alex-shpak/hugo-book themes/hugo-book
git submodule update --init --recursive
```

## Publish to GitHub Pages
1. Push `main` (or your default branch) to GitHub.
2. Ensure the `hugo.yml` workflow is present under `.github/workflows/`.
3. In the repository settings, enable GitHub Pages with the `gh-pages` branch.
4. Trigger the workflow manually or push a commit to build and deploy the site.

## Troubleshooting
- **Submodule missing:** Run the submodule commands above and commit the resulting `.gitmodules` update.
- **Workflow fails:** Verify the Hugo version, theme submodule checkout, and that `baseURL` points to the correct GitHub Pages URL.
- **Broken links:** Run `hugo --minify` locally to detect build-time issues before pushing.

## Local Testing Commands
```bash
hugo --minify
hugo server -D
```
