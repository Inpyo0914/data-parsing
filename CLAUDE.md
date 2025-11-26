# CLAUDE.md - AI Assistant Guide for Data Parsing Project

**Last Updated:** 2025-11-26
**Repository:** Inpyo0914/data-parsing
**Purpose:** Comprehensive guide for AI assistants working on this data parsing project

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Development Setup](#development-setup)
4. [Code Conventions](#code-conventions)
5. [Common Tasks](#common-tasks)
6. [Testing Guidelines](#testing-guidelines)
7. [Git Workflow](#git-workflow)
8. [AI Assistant Best Practices](#ai-assistant-best-practices)

---

## Project Overview

### Purpose
This repository contains tools and libraries for parsing various data formats. The project aims to provide robust, efficient, and maintainable solutions for data extraction, transformation, and loading (ETL) operations.

### Key Goals
- **Reliability**: Handle malformed data gracefully with proper error reporting
- **Performance**: Process large datasets efficiently
- **Extensibility**: Easy to add support for new data formats
- **Maintainability**: Clean, well-documented code that's easy to understand

### Target Data Formats
(To be updated as the project grows)
- CSV/TSV files
- JSON/JSONL
- XML
- Excel files (XLSX, XLS)
- Parquet
- Custom proprietary formats

---

## Repository Structure

### Recommended Structure

```
data-parsing/
├── src/                    # Source code
│   ├── parsers/           # Format-specific parser implementations
│   ├── validators/        # Data validation logic
│   ├── transformers/      # Data transformation utilities
│   ├── utils/             # Shared utility functions
│   └── cli/               # Command-line interface
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test data files
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── guides/           # User guides
│   └── examples/         # Usage examples
├── scripts/               # Build and utility scripts
├── config/                # Configuration files
├── .github/               # GitHub workflows and templates
├── CLAUDE.md             # This file
├── README.md             # Project README
├── CONTRIBUTING.md       # Contribution guidelines
└── LICENSE               # License file
```

### Current State (As of 2025-11-26)

**Repository Status: Greenfield/Initial Setup**

This is a brand new repository with minimal structure:
```
data-parsing/
├── .git/                  # Git repository
└── CLAUDE.md             # This AI assistant guide
```

**What exists:**
- Git repository initialized
- CLAUDE.md documentation file

**What doesn't exist yet:**
- No source code files
- No package manager configuration (package.json, requirements.txt, etc.)
- No README.md
- No LICENSE
- No test files
- No CI/CD workflows

**Next Steps:**
When beginning development, you should:
1. Determine the primary programming language (Python, JavaScript/TypeScript, Go, etc.)
2. Create appropriate configuration files (package.json, requirements.txt, go.mod, etc.)
3. Set up the directory structure as outlined in "Recommended Structure" above
4. Create a README.md with project description
5. Add a LICENSE file
6. Set up .gitignore for the chosen language

As files are added, this section will be updated to reflect the actual structure.

---

## Development Setup

### Prerequisites
(To be defined based on implementation language)

#### For Python Projects:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

#### For Node.js Projects:
```bash
# Install dependencies
npm install
# or
yarn install
```

#### For Other Languages:
(To be documented as needed)

### Environment Variables
Store sensitive configuration in `.env` file (never commit this):
```bash
# Example .env structure
DATA_SOURCE_API_KEY=your_key_here
MAX_WORKERS=4
LOG_LEVEL=INFO
```

---

## Code Conventions

### General Principles
1. **Clarity over cleverness**: Write code that's easy to understand
2. **DRY (Don't Repeat Yourself)**: Extract common logic into reusable functions
3. **SOLID principles**: Follow object-oriented design principles
4. **Fail fast**: Validate inputs early and provide clear error messages

### Naming Conventions

#### Files and Modules
- Use lowercase with underscores for Python: `csv_parser.py`
- Use kebab-case for JavaScript/TypeScript: `csv-parser.ts`
- Use descriptive names that indicate purpose

#### Functions and Methods
- Use verbs for action functions: `parse_data()`, `validate_schema()`, `transform_records()`
- Use clear parameter names: `parse_csv(file_path, delimiter=',')`
- Avoid abbreviations unless widely understood

#### Classes
- Use PascalCase: `CsvParser`, `DataValidator`
- Name classes as nouns representing concepts

#### Variables
- Use descriptive names: `parsed_records` not `pr`
- Boolean variables should be questions: `is_valid`, `has_header`
- Constants in UPPER_CASE: `MAX_BATCH_SIZE`, `DEFAULT_ENCODING`

### Documentation
- Every public function/method needs a docstring
- Document parameters, return values, and exceptions
- Include usage examples for complex functions
- Keep comments up-to-date with code changes

#### Python Example:
```python
def parse_csv(file_path: str, delimiter: str = ',', encoding: str = 'utf-8') -> List[Dict]:
    """
    Parse a CSV file and return records as a list of dictionaries.

    Args:
        file_path: Path to the CSV file
        delimiter: Field delimiter character (default: ',')
        encoding: File encoding (default: 'utf-8')

    Returns:
        List of dictionaries where keys are column names

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the CSV is malformed

    Example:
        >>> records = parse_csv('data.csv', delimiter='|')
        >>> print(len(records))
        100
    """
    pass
```

### Error Handling
- Use specific exception types, not generic `Exception`
- Provide context in error messages
- Log errors with appropriate severity levels
- Clean up resources (files, connections) in finally blocks or using context managers

### Code Style
- Follow language-specific style guides:
  - Python: PEP 8
  - JavaScript/TypeScript: Airbnb or Standard
  - Go: gofmt conventions
- Use linters and formatters:
  - Python: `black`, `flake8`, `mypy`
  - JavaScript: `eslint`, `prettier`
  - Go: `golint`, `go vet`
- Maximum line length: 88-100 characters
- Use type hints/annotations where supported

---

## Common Tasks

### For AI Assistants Working on This Project

#### 1. Adding a New Parser
```bash
# Steps to follow:
1. Create parser file in src/parsers/
2. Implement parser class inheriting from base parser
3. Add comprehensive unit tests
4. Update documentation
5. Add example usage to docs/examples/
```

#### 2. Debugging Data Parsing Issues
- Always read the input file first to understand its structure
- Check for encoding issues (UTF-8, Latin-1, etc.)
- Look for malformed data (missing delimiters, unescaped quotes)
- Test edge cases: empty files, single row, very large files
- Add logging at key points to trace execution

#### 3. Performance Optimization
- Profile code before optimizing (don't guess!)
- Consider streaming for large files instead of loading entirely
- Use appropriate data structures (sets for lookups, generators for iteration)
- Batch operations when possible
- Cache expensive computations

#### 4. Adding Data Validation
- Create validator in src/validators/
- Support both strict and lenient validation modes
- Return detailed validation reports, not just pass/fail
- Make validators composable

#### 5. Writing Tests
- Test happy path AND error cases
- Use representative test fixtures
- Test edge cases: empty input, malformed data, huge datasets
- Aim for >80% code coverage
- Mock external dependencies

---

## Testing Guidelines

### Test Structure
```
tests/
├── unit/              # Fast, isolated tests
├── integration/       # Tests combining multiple components
├── performance/       # Performance benchmarks
└── fixtures/          # Test data files
```

### Running Tests

#### Python
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_csv_parser.py

# Run tests matching pattern
pytest -k "test_parse"
```

#### JavaScript/TypeScript
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### Test Naming
- Test files: `test_<module_name>.py` or `<module_name>.test.ts`
- Test functions: `test_<feature>_<scenario>_<expected_result>`
  - Example: `test_csv_parser_with_missing_delimiter_raises_error`

### Test Data
- Keep test fixtures small but representative
- Document what each fixture tests
- Version control fixtures
- Don't use production data in tests

### Assertions
- One logical assertion per test
- Use descriptive assertion messages
- Test both positive and negative cases

---

## Git Workflow

### Branch Naming
All feature branches must follow this pattern:
```
claude/claude-md-<session-id>
```

Current working branch: `claude/claude-md-mig4ia41hnd5hh4h-014BPofjYzgzKYrphhDwgDUW`

### Commit Messages
Follow conventional commits format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(parsers): add XML parser with namespace support

Implement XMLParser class that handles:
- Nested elements
- Namespaces
- Attributes
- CDATA sections

Closes #123

---

fix(csv): handle escaped quotes in CSV fields

Previously failed on fields like: "he said ""hello"""
Now correctly unescapes quotes per RFC 4180
```

### Commit Frequency
- Commit logical units of work
- Don't commit broken code to feature branches
- Squash WIP commits before merging

### Push Strategy
```bash
# Push with upstream tracking
git push -u origin claude/claude-md-<session-id>

# Retry on network failures (up to 4 times with exponential backoff)
```

### Pull Requests
- Provide clear description of changes
- Reference related issues
- Include test results
- Request review from appropriate team members

---

## AI Assistant Best Practices

### Before Making Changes
1. **Read before writing**: Always read files before modifying them
2. **Understand context**: Check related files and dependencies
3. **Check existing patterns**: Follow established conventions in the codebase
4. **Plan complex changes**: Use TodoWrite tool for multi-step tasks

### While Implementing
1. **Use TodoWrite tool**: Track progress on multi-step tasks
2. **Test incrementally**: Don't write all code before testing
3. **Run linters**: Ensure code style compliance
4. **Check for side effects**: Consider impact on other modules

### Code Quality
1. **No security vulnerabilities**: Watch for injection attacks, XSS, etc.
2. **No over-engineering**: Keep it simple
3. **No premature optimization**: Measure before optimizing
4. **No magic numbers**: Use named constants

### Communication
1. **Be concise**: Provide clear, brief explanations
2. **Show file locations**: Use `file_path:line_number` format
3. **Explain trade-offs**: When multiple approaches exist
4. **Ask when unclear**: Don't guess requirements

### Common Pitfalls to Avoid
- ❌ Don't create files unless necessary
- ❌ Don't add features not requested
- ❌ Don't refactor unrelated code
- ❌ Don't commit without testing
- ❌ Don't use generic error handling
- ❌ Don't skip documentation
- ❌ Don't push to wrong branch

### Recommended Workflow
1. Understand the requirement
2. Create task list with TodoWrite (if complex)
3. Read relevant files
4. Make targeted changes
5. Test changes
6. Update documentation
7. Commit with clear message
8. Push to correct branch

---

## Debugging Checklist

When investigating issues:
- [ ] Read error messages completely
- [ ] Check input data format and encoding
- [ ] Verify file paths are correct
- [ ] Look at recent commits for related changes
- [ ] Check dependencies are installed correctly
- [ ] Review logs at DEBUG level
- [ ] Test with minimal example
- [ ] Check for environment-specific issues

---

## Resources

### Documentation
- (Add links to external docs as needed)

### Tools
- (List recommended tools, editors, extensions)

### Learning Resources
- (Add tutorials, guides, reference materials)

---

## Maintenance

### Updating This File
- Update when project structure changes
- Update when new conventions are established
- Update when new tools/technologies are added
- Update when common issues are discovered
- Review quarterly for accuracy

### Version History
- **2025-11-26 (Latest)**: Updated with actual repository state, corrected branch name, clarified greenfield status
- **2025-11-26**: Initial creation - comprehensive guide for new repository

---

## Questions or Issues?

If you encounter situations not covered by this guide:
1. Check existing issues and discussions
2. Review recent pull requests for similar cases
3. Ask for clarification in comments
4. Propose updates to this guide via PR

---

*This guide is a living document. Contributions and improvements are welcome!*
