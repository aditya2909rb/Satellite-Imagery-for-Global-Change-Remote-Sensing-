# Contributing to Satellite Fire Detection System

First off, thank you for considering contributing to this project! 🎉

## Code of Conduct

By participating in this project, you are expected to uphold a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if applicable**
- **Note your environment** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the proposed functionality**
- **Explain why this enhancement would be useful**
- **List some examples of how it would be used**

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Write clear commit messages**
6. **Submit a pull request**

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/yourusername/satellite-fire-detection.git
   cd satellite-fire-detection
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r satellite-detection-project/requirements.txt
   pip install -r requirements.txt
   ```

4. Run tests to verify setup:
   ```bash
   cd satellite-detection-project
   python validate.py
   pytest
   ```

## Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guide for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Write comments for complex logic

### Example:

```python
def detect_fires(latitude: float, longitude: float, radius_km: float) -> List[Dict]:
    """
    Detect fires in a given region.
    
    Args:
        latitude (float): Center latitude
        longitude (float): Center longitude
        radius_km (float): Search radius in kilometers
        
    Returns:
        List[Dict]: List of detected fires with metadata
    """
    # Implementation here
    pass
```

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for good test coverage

Run tests with:
```bash
pytest
```

## Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues and pull requests when applicable

Examples:
- `Add fire detection caching mechanism`
- `Fix issue with coordinate validation #123`
- `Update README with installation instructions`

## Project Structure

```
satellite-detection-project/
├── src/
│   ├── api/              # API endpoints
│   ├── models/           # ML models
│   ├── preprocessing/    # Image processing
│   ├── visualization/    # Maps and charts
│   └── utils/           # Utility functions
├── data/                # Data storage
├── tests/               # Test files
└── static/              # Static assets
```

## Areas for Contribution

- 🔥 Fire detection algorithms
- 🗺️ Map visualization improvements
- 📧 Alert system enhancements
- 📊 Data analysis features
- 🧪 Test coverage
- 📝 Documentation
- 🐛 Bug fixes
- ⚡ Performance optimizations

## Questions?

Feel free to open an issue for any questions or discussions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🚀
