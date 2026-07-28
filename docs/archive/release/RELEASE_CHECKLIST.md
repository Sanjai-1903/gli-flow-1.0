# Release Checklist

> Semantic versioning: https://semver.org
> Current version: **v1.0.0**

---

## Pre-release Checklist

- [ ] All unit tests pass (`pytest`)
- [ ] Golden regression suite passes (counter, uart, gpio, fir)
- [ ] Failure corpus passes (all known-failing designs produce expected errors)
- [ ] `gli-flow doctor` validation passes
- [ ] **Environment resilience tests pass** (`tests/adversarial/environment/`, `tests/regressions/test_path_shadowing_prefers_functional_binary.py`)
- [ ] **Release validation passes** (`python3 release/validate_release.py` — checks 4 environment resilience gates)
- [ ] CHANGELOG.md updated with new version entry
- [ ] Version bumped in `gli_flow/version.py`
- [ ] `RELEASE_READINESS.md` reviewed and scorecard ≥ 6/10
- [ ] License headers present on all new source files
- [ ] No open security advisories (see `SECURITY.md`)

### Environment Resilience Gates

The release validation (`release/validate_release.py`) enforces:

1. **Multi-candidate discovery** — Fails if single-candidate `find_magic_binary` remains
2. **Path shadowing regression tests** — Fails if regression test file missing
3. **Doctor repair framework** — Fails if `PathShadowingRepair` or `repair_path_shadowing` missing
4. **Adversarial environment tests** — Fails if no test files in `tests/adversarial/environment/`

## Release Build

- [ ] `pyproject.toml` / `setup.py` validated (`python -m build --sdist --wheel`)
- [ ] Build wheel (`python -m build --wheel`)
- [ ] Build source distribution (`python -m build --sdist`)
- [ ] Sign the release commit (`git commit -S`)
- [ ] Tag the release (`git tag -s v{major}.{minor}.{patch}`)
- [ ] Verify tag signature (`git tag -v v{major}.{minor}.{patch}`)
- [ ] Push commit and tag (`git push && git push --tags`)

## Post-release Steps

- [ ] Publish to PyPI (`twine upload dist/*`)
- [ ] Build and publish Docker image (`docker build -t gli-flow:{tag} . && docker push`)
- [ ] Create GitHub Release with release notes
- [ ] Update documentation to reflect new version
- [ ] Verify install from PyPI (`pip install gli-flow=={version}`)
- [ ] Verify Docker image (`docker run gli-flow:{version} gli-flow doctor`)

---

## Version Bump Policy

| Bump | When | Example |
|------|------|---------|
| **MAJOR** | Breaking changes to CLI, API, data model, or workflow compatibility | `1.0.0` → `2.0.0` |
| **MINOR** | New features, backwards-compatible additions | `1.0.0` → `1.1.0` |
| **PATCH** | Bug fixes, documentation, performance improvements | `1.0.0` → `1.0.1` |
