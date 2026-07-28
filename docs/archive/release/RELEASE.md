# Release Process

This document describes how to cut a release of GLI-FLOW.

## Semantic Versioning

GLI-FLOW follows [Semantic Versioning 2.0.0](https://semver.org).

Given a version number `MAJOR.MINOR.PATCH`:

- **MAJOR** — incompatible API, CLI, or data-model changes
- **MINOR** — backwards-compatible new functionality
- **PATCH** — backwards-compatible bug fixes

Pre-release suffixes (`-alpha`, `-beta`, `-rc.1`) may be used for
intermediate releases.

## Pre-release Validation

Before a release is cut, the following must pass:

1. **Test suite** — `pytest` with zero failures.
2. **Golden regression** — every design in the golden regression suite
   (counter, uart, gpio, fir) must pass in mock mode.
3. **Failure corpus** — every known-failing design in the failure corpus
   must produce the expected diagnostic (proving error detection works).
4. **Doctor** — `gli-flow doctor` must report all checks green.
5. **CHANGELOG** — updated with the new version and date.
6. **Version file** — `gli_flow/version.py` bumped.

## Release Automation

Release builds are currently manual. Future automation
(GitHub Actions) will:

- Run the full CI matrix on `main`
- Build wheels and source distributions
- Publish to PyPI on tagged commits
- Build and push Docker images
- Create GitHub Releases with auto-generated notes

## How to Cut a Release

```bash
# 1. Ensure working tree is clean
git status

# 2. Bump version
echo 'VERSION = "v{major}.{minor}.{patch}"' > gli_flow/version.py

# 3. Update CHANGELOG.md with new version entry and date

# 4. Commit the version bump
git add gli_flow/version.py CHANGELOG.md
git commit -S -m "chore: bump version to v{major}.{minor}.{patch}"

# 5. Tag the release
git tag -s v{major}.{minor}.{patch} -m "v{major}.{minor}.{patch}"

# 6. Build distributions
python -m build --sdist --wheel

# 7. Push
git push && git push --tags

# 8. Publish to PyPI
twine upload dist/gli_flow-{major}.{minor}.{patch}*

# 9. Build and push Docker image
docker build -t gli-flow:v{major}.{minor}.{patch} .
docker push gli-flow:v{major}.{minor}.{patch}

# 10. Create GitHub Release
gh release create v{major}.{minor}.{patch} \
  --title "v{major}.{minor}.{patch}" \
  --notes "$(sed -n '/^## \['"${major}.${minor}.${patch}"'\]/,/^## \[/p' CHANGELOG.md | head -n -2)"
```
