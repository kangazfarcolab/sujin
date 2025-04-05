# Contributing to Sujin

Thank you for your interest in contributing to Sujin! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/sujin.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Create a new branch for your changes: `git checkout -b feature/your-feature-name`

## Development Workflow

1. Make your changes
2. Write tests for your changes
3. Run the tests: `python -m unittest discover tests`
4. Format your code: `black .`
5. Commit your changes: `git commit -m "Add your feature"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Create a pull request

## Pull Request Guidelines

1. Provide a clear and descriptive title
2. Include a detailed description of the changes
3. Reference any related issues
4. Ensure all tests pass
5. Follow the code style guidelines

## Code Style Guidelines

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions, classes, and methods
- Keep lines under 100 characters
- Use descriptive variable names

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Aim for high test coverage

## Documentation

- Update documentation for any changes to the API
- Add examples for new features
- Keep the README.md up to date

## License

By contributing to Sujin, you agree that your contributions will be licensed under the project's MIT license.
