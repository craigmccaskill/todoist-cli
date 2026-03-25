# Installation

## From Source

```bash
git clone https://github.com/craigmccaskill/todoist-cli.git
cd todoist-cli
pip install -e .
```

Requires Python 3.10+.

## Optional Extras

### Interactive TUI

For the interactive task picker and `td review` inbox processing:

```bash
pip install -e ".[interactive]"
```

### Shell Completions

After installing, generate completions for your shell:

```bash
# Bash
td completions bash >> ~/.bashrc

# Zsh
td completions zsh >> ~/.zshrc

# Fish
td completions fish > ~/.config/fish/completions/td.fish
```

Restart your shell or `source` the file to enable.
