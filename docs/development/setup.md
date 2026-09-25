# Local setup

From a clean Windows machine to a working, tested checkout. The commands were verified on
2026-09-25 (MVP-001, phase 3).

## 1. Install the tools

See [`tools.md`](tools.md) for what each tool is for.

```powershell
winget install Anaconda.Miniconda3   # or an existing Anaconda installation
winget install Git.Git
```

Keep Conda current:

```bash
conda update conda
```

## 2. Clone the repository

Create an SSH key and add it to GitHub under **Settings → SSH and GPG keys**
(<https://github.com/settings/keys>):

```bash
ssh-keygen -t ed25519 -C "your description"
git clone git@github.com:riniga/accounting-agent.git
cd accounting-agent
```

## 3. Create the environment and install the package

Details in [`environment.md`](environment.md):

```bash
conda env create -f environment.yml
conda activate accounting-agent
pip install -e .
pre-commit install
```

## 4. Verify

```bash
pytest -q
accounting-agent run example --config-dir tests/fixtures/example
```

The second command should print the example organisation's enabled features and exit
with code 0.

## Next

Read [`AGENTS.md`](../../AGENTS.md) and the standards in [`docs/standards/`](../standards/).
