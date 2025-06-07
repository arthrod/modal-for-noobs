# 🚀 modal-for-noobs

**Async-first, idiot-proof Gradio deployment CLI for Modal**

Deploy your Gradio apps to Modal with zero configuration. Perfect for noobs who just want things to work! 🎯

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## ✨ Features

- 🚀 **Zero-config deployment** - Just point at your Gradio app and go!
- ⚡ **--time-to-get-serious** - Migrate HuggingFace Spaces to Modal in seconds
- 🔄 **Async-first** - Built with modern Python async/await patterns
- 🎯 **Two modes**: Minimum (CPU) or Optimized (GPU + ML libraries)
- 🔐 **Auto-authentication** - Handles Modal setup automatically
- 🪝 **Smart detection** - Finds your Gradio interface automatically
- 📦 **Dependency magic** - Auto-installs requirements from HF Spaces

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and install
git clone https://github.com/arthrod/modal-for-noobs.git
cd modal-for-noobs
uv sync

# Or install directly (future)
pip install modal-for-noobs
```

### 2. Deploy Your Gradio App

```bash
# Basic deployment (CPU) - beautiful Modal green UI!
modal-for-noobs deploy my_app.py

# Quick deploy (for noobs who love shortcuts)
modal-for-noobs mn my_app.py

# Optimized deployment (GPU + ML libraries)
modal-for-noobs deploy my_app.py --optimized
# or the shortcut:
modal-for-noobs mn my_app.py -o

# Dry run (generate files only)
modal-for-noobs deploy my_app.py --dry-run
```

### 3. Time to Get SERIOUS! 💪

```bash
# The nuclear option - migrate HuggingFace Spaces! 🚀
modal-for-noobs time-to-get-serious https://huggingface.co/spaces/user/space-name

# With dry run (see what happens first)
modal-for-noobs time-to-get-serious https://huggingface.co/spaces/user/space-name --dry-run
```

### 4. Authentication (auto-setup!)

```bash
# If no Modal keys found, it automatically starts auth setup! 
# But you can also manually trigger it:
modal-for-noobs auth
```

## 🛠️ Development

### Adding Dependencies

```bash
uv add requests              # Add runtime dependency
uv add pytest --dev         # Add development dependency
```

### Code Quality

```bash
uv run ruff check           # Lint code
uv run ruff format          # Format code
uv run mypy src/            # Type check
uv run pytest              # Run tests
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

- Trailing whitespace removal
- YAML/TOML/JSON validation
- Ruff linting and formatting
- MyPy type checking
- Bandit security checks

## 👥 Contributing

- 🍴 Fork the repository
- 🌿 Create your feature branch (git checkout -b feature/amazing-feature)
- 💾 Commit your changes (git commit -m 'Add some amazing feature')
- 🚢 Push to the branch (git push origin feature/amazing-feature)
- 🔍 Open a Pull Request

## ⚠️ Trusted publishing failure

That's good news!

You are not able to publish to PyPI unless you have registered your project
on PyPI. You get the following message:

```bash
Trusted publishing exchange failure:

Token request failed: the server refused the request for
the following reasons:

invalid-publisher: valid token, but no corresponding
publisher (All lookup strategies exhausted)
This generally indicates a trusted publisher
configuration error, but could
also indicate an internal error on GitHub or PyPI's part.

The claims rendered below are for debugging purposes only.
You should not
use them to configure a trusted publisher unless they
already match your expectations.
```

Please register your repository. The 'release.yml' flow is
publishing from the 'release' environment. Once you have
registered your new repo it should all work.

---

## 💚 Credits

**Made with <3 by [Neurotic Coder](https://github.com/arthrod) and assisted by Beloved Claude** ✨

*This project represents the beautiful chaos of neurotic coding meets AI assistance - resulting in something absolutely AMAZING!* 🚀💚