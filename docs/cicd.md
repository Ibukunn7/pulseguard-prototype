# CI/CD

## Overview

This page will document the GitHub Actions workflow once it is added to the repository.

Planned checks on every pull request:

- Markdown lint
- Link check
- Spell check
- `mkdocs build --strict`
- Service tests (pytest across all three services)
- Docker image build

Planned actions on merge to main:

- Deploy documentation to GitHub Pages
