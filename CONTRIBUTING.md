# Contributing to Lingofy

We welcome contributions! Please follow these guidelines to maintain code quality and project consistency.

## 1. Branch Strategy
We follow a simplified GitFlow model:
- `main`: Production-ready code. Never commit directly to `main`.
- `develop`: The active development branch.
- `feature/your-feature-name`: For new features.
- `bugfix/issue-name`: For bug fixes.

## 2. Commit Convention
Use conventional commits for clear history:
- `feat:` A new feature.
- `fix:` A bug fix.
- `docs:` Documentation only changes.
- `style:` Changes that do not affect the meaning of the code (white-space, formatting).
- `refactor:` A code change that neither fixes a bug nor adds a feature.
- `test:` Adding missing tests or correcting existing tests.

*Example:* `feat: add pronunciation shadowing mode`

## 3. PR Rules (Pull Requests)
- Create a PR against the `develop` branch.
- Ensure all tests pass (`pytest backend/tests`).
- Ensure the frontend builds successfully (`npm run build`).
- Request a review from at least one core maintainer.

## 4. Coding Style
**Backend (Python):**
- Follow PEP 8 guidelines.
- Use type hints (`def func(a: int) -> str:`).
- Use the central `logger` instead of `print()`.

**Frontend (React/Next.js):**
- Use functional components and Hooks.
- Optimize heavy renders with `React.memo` and `useCallback`.
- Use Tailwind CSS utility classes instead of inline styles.

## 5. Folder Rules
- **`backend/core/`**: Core utilities (db, config, logger).
- **`backend/routes/`**: FastAPI endpoints.
- **`backend/tests/`**: Pytest scenarios.
- **`frontend/components/`**: Reusable React components.
- **`frontend/src/app/`**: Next.js App Router pages.
