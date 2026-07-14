# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Fixed
- **Auth API:** `register`, `login` and `refresh` routes now return `access_token` in the JSON response body along with setting the `HttpOnly` cookie, to support mobile clients and non-browser testing environments.
- **Tests:** `test_login_invalid_credentials` now uses a dynamically generated email to prevent Rate Limit (`429 Too Many Requests`) blocking across consecutive test runs.

### Tested
- Initial backend test suite now passes with 100% success rate on existing test cases. Backend coverage is currently established at 42%.
