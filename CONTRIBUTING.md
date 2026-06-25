# Contributing to Lingofy

We love your input! We want to make contributing to Lingofy as easy and transparent as possible, whether it's:
- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## 1. Code Style & Formatting

We enforce strict formatting rules to keep the codebase clean.

### Frontend (React/Next.js)
- **Framework:** Next.js 14 App Router.
- **Components:** Functional components only. Use `memo` where performance is critical (e.g., `LyricsPlayer.jsx`).
- **Styling:** TailwindCSS utility classes. Custom CSS should be placed in `index.css` under the `@layer utilities` or `@layer components`.
- **Linting:** We use ESLint. Run `npm run lint` before committing.

### Backend (Python/FastAPI)
- **Formatting:** We use `black`.
- **Typing:** Strict type hinting is required for all function arguments and return types.
- **Routing:** Keep business logic out of route handlers (`routes/`). Move logic to the `core/services/` or `core/providers/` layers.

## 2. Branching Strategy

We follow a Git Flow inspired model:
- `main`: Production-ready code. Never push directly to `main`.
- `develop`: Pre-production. All feature branches merge here first.
- `feature/name-of-feature`: For new features.
- `bugfix/issue-description`: For bug fixes.

## 3. Commit Convention

We use Conventional Commits. Your commit messages should look like:
`type(scope): description`

Examples:
- `feat(auth): add google oauth provider`
- `fix(lyrics): resolve abort controller memory leak`
- `docs(api): update endpoints in README`
- `refactor(ai): switch from openai to openrouter`

## 4. Pull Request Rules

1. **Keep it small:** PRs should ideally do one thing. If you're fixing a bug and adding a feature, open two PRs.
2. **Test your code:** Ensure the server runs without errors (`uvicorn backend.main:app`) and the frontend compiles (`npm run dev`).
3. **Describe your changes:** Use the PR template to explain *why* this change is needed and *how* you implemented it.
4. **Code Review:** All PRs require at least 1 approval from a core maintainer before being merged into `develop`.

Thank you for helping make Lingofy better!
