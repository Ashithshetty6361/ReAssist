# ReAssist Code & Style Guide

## Python Formatting
We use `ruff` to standardize Python formatting and catching lint errors. Our configuration strictly enforces a line-length of 120 and target version `py310`.

```bash
# Check code style
make lint

# Auto-format
make format
```

## Type Hinting
We enforce standard Python static typing with `mypy`.
```bash
make typecheck
```

## Git Guidelines
Please follow the `conventional commits` specification:
- `feat:` for new features
- `fix:` for fixing bugs
- `docs:` for documentation changes
- `refactor:` for zero-functional change improvements

Example: `feat: add conversational memory to synthesizer`
