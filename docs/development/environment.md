# Development Environment

The workspace uses Conda for Python itself and a hash-pinned pip lock for everything else.
The environment definition is version-controlled in `environment.yml` at the repository
root. It installs Python 3.14 from conda-forge, then every pip dependency from
`requirements-lock.txt`, which is compiled from `requirements.in`.

## Prerequisites

Miniconda or Anaconda must be installed. See [`tools.md`](tools.md).

## Create the environment

Run once after cloning, from the repository root:

```bash
conda env create -f environment.yml
conda activate accounting-agent
pip install -e .
```

`pip install -e .` installs the `accounting-agent` package in editable mode, so code
changes take effect without reinstalling. Its runtime dependencies are already in the
lock, so pip installs nothing else.

## Install the pre-commit hooks

Run once, with the environment active:

```bash
pre-commit install
```

This wires Ruff format/lint, a few file validators and detect-secrets to run on every
`git commit`. See `.pre-commit-config.yaml`.

## Activate the environment

Run at the start of every development session:

```bash
conda activate accounting-agent
```

All commands (`pytest`, `pip`, `python`, `accounting-agent`) must be run with the
environment active.

## Update the environment

Run after pulling changes that modify `environment.yml` or `requirements-lock.txt`:

```bash
conda env update -f environment.yml --prune
```

## Remove the environment

```bash
conda deactivate
conda env remove -n accounting-agent
```

## Add a new dependency

See [`docs/standards/dependencies.md`](../standards/dependencies.md). New pip dependencies
go in `requirements.in` and are compiled into `requirements-lock.txt`. A runtime
dependency of the package also goes in `[project] dependencies` in `pyproject.toml`.

1. Add the package to `requirements.in` (and to `pyproject.toml` if it's a runtime
   dependency).
2. Recompile: `pip-compile --generate-hashes --no-annotate --no-header requirements.in`
   (`pip install pip-tools` first if needed).
3. Update the environment: `conda env update -f environment.yml --prune`.
4. Commit `requirements.in` and `requirements-lock.txt` (and `pyproject.toml` if changed)
   in the same pull request as the code that needs the dependency.
5. If the dependency is significant, document the decision in an ADR.

## Verify the environment

```bash
conda activate accounting-agent
python --version   # Python 3.14.x
pytest --version   # pytest 9.x
```
