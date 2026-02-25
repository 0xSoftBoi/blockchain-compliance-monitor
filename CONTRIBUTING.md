# Contributing to Blockchain Compliance Monitor

## Internal Development Guidelines

Thank you for contributing to Global Settlement's Blockchain Compliance Monitor.

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/0xSoftBoi/blockchain-compliance-monitor.git
cd blockchain-compliance-monitor
```

### 2. Set Up Development Environment

```bash
# Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Frontend
cd frontend
npm install
cd ..

# Pre-commit hooks
pre-commit install
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with development settings
```

### 4. Start Services

```bash
# Start databases
docker-compose up -d postgres redis

# Initialize database
python scripts/init_db.py

# Start API server
python -m backend.main

# Start frontend (in another terminal)
cd frontend && npm run dev
```

## Code Style

### Python

- **Formatter**: Black (line length 100)
- **Linter**: Flake8
- **Type Checker**: MyPy
- **Docstrings**: Google style

```python
def function_name(param: str) -> Dict:
    """Brief description.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
    """
    pass
```

### TypeScript/React

- **Formatter**: Prettier
- **Linter**: ESLint
- **Style Guide**: Airbnb

```typescript
interface Props {
  name: string
  value: number
}

export function Component({ name, value }: Props) {
  return <div>{name}: {value}</div>
}
```

## Testing

### Writing Tests

```python
import pytest

@pytest.mark.asyncio
async def test_feature():
    """Test description."""
    result = await some_function()
    assert result == expected_value
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Specific test
pytest tests/test_monitoring.py::test_submit_transaction

# Frontend tests
cd frontend && npm test
```

## Pull Request Process

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run Checks**
   ```bash
   # Format code
   black backend/
   cd frontend && npm run format
   
   # Run tests
   pytest
   npm test
   
   # Run linters
   flake8 backend/
   npm run lint
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   
   **Commit Message Format:**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `test:` Tests
   - `refactor:` Code refactoring
   - `chore:` Maintenance

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **PR Requirements**
   - All tests passing
   - Code coverage maintained or improved
   - Documentation updated
   - Changelog entry (if applicable)
   - Reviewed by at least one team member

## Security

- **Never commit secrets** or credentials
- **Report security issues** to security@globalsettlement.com
- **Follow secure coding practices**
- **Update dependencies** regularly

## Code Review Guidelines

### For Authors

- Keep PRs focused and small
- Write clear descriptions
- Respond to feedback promptly
- Test thoroughly before requesting review

### For Reviewers

- Be constructive and respectful
- Check for:
  - Code correctness
  - Test coverage
  - Security implications
  - Performance considerations
  - Documentation completeness

## Getting Help

- **Slack**: #compliance-dev
- **Email**: dev-team@globalsettlement.com
- **Documentation**: `/docs` directory

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
