# Contributing to Frappe Metabase

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. Set up a Frappe bench (v15+) with developer mode enabled
2. Clone this app:
   ```bash
   cd ~/frappe-bench
   bench get-app https://github.com/your-org/frappe_metabase.git
   bench --site your-site.local install-app frappe_metabase
   ```
3. Have a Metabase instance running (Docker is easiest for dev):
   ```bash
   docker run -d -p 3000:3000 --name metabase metabase/metabase
   ```

## Making Changes

1. Fork the repo and create a feature branch: `git checkout -b feat/my-feature`
2. Make your changes
3. Run linting: `ruff check frappe_metabase/`
4. Test locally with your Frappe bench
5. Commit with conventional commit messages:
   - `feat: add X` for new features
   - `fix: resolve Y` for bug fixes
   - `docs: update Z` for documentation
6. Push and open a Pull Request

## Code Style

- Python: follow PEP 8, use ruff for formatting
- JavaScript: use Frappe conventions (tabs for indentation in JS files)
- Doctype JSON: always export from bench (`bench export-doc`) — don't hand-edit

## Reporting Issues

Use GitHub Issues. Include:
- Frappe version
- Metabase version
- Steps to reproduce
- Error messages / screenshots

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
