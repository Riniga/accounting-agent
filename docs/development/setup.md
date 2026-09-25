# Sätt upp miljön lokalt

## Applikationer som måste vara installerade

Följande applikationer:

### Winget - Lite kommandon relaterat till winget

* winget upgrade --id Microsoft.AppInstaller
* winget upgrade --all
* winget source update
* winget source list

### Miniconda

winget install Anaconda.Miniconda3
conda update conda
conda update --all
conda clean --all
conda env list
conda config --show channels
conda config --add channels conda-forge
conda install \<paket\>

conda search python
conda create --name accounting-agent python=3.13
conda activate accounting-agent

### Git

winget install Git.Git
Create SSH Key: ssh-keygen -t ed25519 -C "Key description"
Add SSH Key to Github: User->Settings->SSH and GPG keys (https://github.com/settings/keys)
git clone git@github.com:riniga/accounting-agent.git

## Nästa steg — miljö och verktyg

After cloning, follow [`environment.md`](environment.md):

```bash
conda env create -f environment.yml
conda activate accounting-agent
pre-commit install
```

This installs the runtime + dev dependencies (including `ruff` and `pre-commit`) and wires
the local Git hooks. Then install the package in editable mode (`pip install -e .` — see
`AGENTS.md`'s "Local commands"), and review the standards in
`docs/standards/`.
