# Installation

## 1. Clone the code

```shell
git clone git@github.com:Computer-Vision-Team-Amsterdam/panorama.git
```

## 2. Install UV

We use UV as package manager, which can be installed using any method mentioned on [the UV webpage](https://docs.astral.sh/uv/getting-started/installation/).

The easiest option is to use their installer:
```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

It is also possible to use pip:
```shell
pipx install uv
```

Afterwards, uv can be updated using `uv self update`.

## 3. Install dependencies

In the terminal, navigate to the project root (the folder containing `pyproject.toml`), then use UV to create a new virtual environment and install the dependencies.

```shell
cd panorama

# Create the environment locally in the folder .venv
uv venv --python 3.14

# Activate the environment
source .venv/bin/activate

# Install dependencies for local development
uv pip install -r pyproject.toml --extra dev
```

To update dependencies (e.g. when pyproject.toml dependencies change):

```shell
uv lock --upgrade
uv sync --extra dev
```
    
## 4. Install pre-commit hooks
The pre-commit hooks help to ensure that all committed code is valid and consistently formatted. We use UV to manage pre-commit as well.

```shell
uv tool install pre-commit --with pre-commit-uv --force-reinstall

# Install pre-commit hooks
uv run pre-commit install

# Optional: update pre-commit hooks
uv run pre-commit autoupdate

# Run pre-commit hooks using
uv run .git/hooks/pre-commit
```