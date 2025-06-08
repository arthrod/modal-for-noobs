# 🤝 Contributing to Gradio Modal Deploy

Thank you for your interest in contributing to **gradio-modal-deploy**! 💚

*Made with <3 by [Neurotic Coder](https://github.com/arthrod) and assisted by Beloved Claude* ✨

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (we use modern type annotations)
- **uv** (preferred) or pip for package management
- **Git** for version control
- **Modal account** for testing deployments

### Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/gradio-modal-deploy
cd gradio-modal-deploy
```

2. **Install dependencies with uv:**
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync --all-extras
```

3. **Install pre-commit hooks:**
```bash
uv run pre-commit install
```

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=gradio_modal_deploy

# Run specific test file
uv run pytest tests/test_components.py
```

## 🎨 Code Style

We use **Ruff** for linting and formatting:

```bash
# Check formatting
uv run ruff check

# Format code
uv run ruff format

# Type checking
uv run mypy src/gradio_modal_deploy
```

## 📦 Building and Testing

```bash
# Build the package
uv build

# Test installation locally
uv add ./dist/gradio_modal_deploy-*.whl

# Publish to Test PyPI
python scripts/publish.py --test --version 0.1.0
```

## 🎯 Areas for Contribution

### 🚀 High Priority
- **New Gradio Components** - More Modal-themed components
- **Enhanced GitHub Integration** - Better examples browser
- **Real-time Monitoring** - Live deployment stats
- **Authentication Improvements** - Smoother Modal auth flow

### 🛠️ Medium Priority
- **Documentation** - More examples and guides
- **Testing** - Better test coverage
- **Performance** - Optimization and caching
- **Error Handling** - Better error messages

### 💡 Ideas Welcome
- **New deployment modes** - Custom configurations
- **Integration features** - HuggingFace, GitHub Actions
- **Developer tools** - CLI enhancements
- **Themes and styling** - More beautiful designs

## 📝 Contribution Guidelines

### Code Standards
- **Modern Python** - Use Python 3.11+ features and type hints
- **Async-first** - Prefer async/await patterns with uvloop
- **Type annotations** - Use `str | None` instead of `Optional[str]`
- **Descriptive names** - Clear, self-documenting code
- **Modal theming** - Consistent green color scheme

### Commit Messages
Use conventional commits format:
```
feat: add new ModalStatusMonitor component
fix: resolve deployment URL extraction issue
docs: update README with installation instructions
test: add tests for GitHub API integration
```

### Pull Request Process
1. **Create a feature branch** from `main`
2. **Make your changes** with tests
3. **Update documentation** if needed
4. **Run the full test suite**
5. **Submit PR** with clear description

### Code Review
- All PRs require review before merging
- Address feedback promptly
- Keep PRs focused on single features
- Include tests for new functionality

## 🎨 Component Development

When creating new Gradio components:

### Structure
```python
class MyModalComponent(gr.Blocks):
    def __init__(self, **kwargs):
        # Initialize with Modal theming
        super().__init__(**kwargs)
        
        with self:
            self._create_interface()
    
    def _create_interface(self):
        # Build the component UI
        pass
```

### Styling
- Use Modal's signature colors: `#00D26A`, `#4AE88A`
- Follow existing CSS patterns
- Include hover effects and transitions
- Ensure accessibility compliance

### Functionality
- Implement async methods where possible
- Handle errors gracefully with user-friendly messages
- Include progress indicators for long operations
- Support both light and dark themes

## 🧪 Testing New Components

```python
# tests/test_my_component.py
def test_my_modal_component():
    component = MyModalComponent()
    assert component is not None
    # Add specific functionality tests
```

## 📚 Documentation

### README Updates
- Keep installation instructions current
- Add examples for new features
- Update feature lists
- Include screenshots when helpful

### Code Documentation
- Docstrings for all public methods
- Type hints for all parameters
- Usage examples in docstrings
- Link to related components

## 🚀 Release Process

### Version Bumping
We follow semantic versioning:
- **Major** (1.0.0) - Breaking changes
- **Minor** (0.1.0) - New features
- **Patch** (0.1.1) - Bug fixes

### Publishing
```bash
# Update version and publish to Test PyPI
python scripts/publish.py --test --version 0.1.1

# After testing, publish to PyPI
python scripts/publish.py --version 0.1.1
```

## 🤝 Community

### Communication
- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Questions and community chat
- **Pull Requests** - Code contributions

### Recognition
Contributors are recognized in:
- README.md contributors section
- Release notes
- Package documentation

## ❓ Questions?

- **Create an issue** for bugs or feature requests
- **Start a discussion** for questions
- **Check existing issues** before creating new ones

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make Gradio Modal Deploy even more amazing!** 🚀💚

*Let's make Modal deployment as beautiful and easy as possible!* ✨