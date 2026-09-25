# Development Environment

The workspace uses Conda to manage the Python environment. The environment definition is version-controlled in `environment.yml` at the repository root.

## Prerequisites

Miniconda or Anaconda must be installed before working with this repository. See `docs/development/tools.md` for installation instructions.

## Create the environment

Run once after cloning the repository:

```bash
conda env create -f environment.yml
```

This creates a Conda environment named `<your-env-name>` with Python 3.13 and all required development dependencies (including `ruff` and `pre-commit`).

## Install the pre-commit hooks

Run once, from the repo root, after creating the environment:

```bash
pre-commit install
```

This wires the Ruff format/lint checks (and a few file validators) to run on every
`git commit`. See `.pre-commit-config.yaml` and the ADR that recorded the formatter/linter
choice (see `docs/architecture/decisions/`).

## Activate the environment

Run at the start of every development session:

```bash
conda activate <your-env-name>
```

All commands (`pytest`, `pip`, `python`) must be run with the environment active.

## Deactivate the environment

```bash
conda deactivate
```

## Update the environment

Run after pulling changes that modify `environment.yml`:

```bash
conda env update -f environment.yml --prune
```

The `--prune` flag removes packages that are no longer listed in `environment.yml`.

## Remove the environment

```bash
conda env remove -n <your-env-name>
```

## Add a new dependency

See [`docs/standards/dependencies.md`](../standards/dependencies.md) — new pip
dependencies go in `requirements.in`, then get compiled into `requirements-lock.txt`
(`environment.yml`'s `pip:` block just points at the lock). Only genuinely Conda-native
packages (not installable via pip) belong directly in `environment.yml`.

1. Add the package to `requirements.in` (or `environment.yml` if it's Conda-native).
2. Recompile: `pip-compile --generate-hashes --no-annotate --no-header requirements.in`.
3. Update the environment: `conda env update -f environment.yml --prune`.
4. Commit `requirements.in` and `requirements-lock.txt` (and `environment.yml` if changed)
   in the same pull request as the code that needs the dependency.
5. If the dependency is significant, document the decision in an ADR.

## Verify the environment

```bash
conda activate <your-env-name>
python --version   # should print Python 3.13.x
pytest --version   # should print pytest 8.x or later
```
