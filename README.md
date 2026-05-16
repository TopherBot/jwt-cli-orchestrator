# jwt‑cli‑orchestrator

**jwt-cli-orchestrator** is a modern, type‑safe command line tool for managing micro‑service deployments.

- ✅ **Typed configuration** – powered by Pydantic.
- ✅ **JWT authentication** – role‑based access control for CLI commands.
- ✅ **Typer CLI** – intuitive sub‑commands with auto‑generated help.
- ✅ **Extensible plugin system** – add custom actions without touching core code.
- ✅ **Open‑source** – MIT licensed, contributions welcome!

## Features

| Feature | Description |
|---------|-------------|
| `config` | Load and validate YAML/JSON config files via Pydantic models. |
| `auth` | Generate, verify, and refresh JWT tokens; store them securely in the OS keyring. |
| `deploy` | Execute deployment pipelines defined in the configuration (Docker, Kubernetes, Helm, etc.). |
| `plugins` | Discover Python entry‑points (`jwt_cli_orchestrator.plugins`) to extend the CLI. |

## Quick start

```bash
# Install
pip install jwt-cli-orchestrator

# Initialise a config file
tjwt init config.yaml

# Generate a token (admin role)
tjwt auth login --user alice --role admin

# Deploy services
ttjwt deploy all
```

## Development

```bash
# Clone the repo
git clone https://github.com/YourOrg/jwt-cli-orchestrator.git
cd jwt-cli-orchestrator

# Install dev dependencies
pip install -e .[dev]

# Run tests
pytest
```

---

*Read the full documentation in `docs/` after cloning the repository.*