from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from typer import Argument, Option

from . import config, auth

app = typer.Typer(help="JWT‑secured CLI for micro‑service orchestration")


@app.command()
def init(
    output: Path = Argument(..., help="Path where the starter config.yaml will be written"),
):
    """Create a skeleton configuration file."""
    starter = {
        "version": "v1",
        "global_env": {"ENV": "production"},
        "services": [
            {
                "name": "web",
                "image": "myorg/web:latest",
                "replicas": 2,
                "env": {"DEBUG": "false"},
            },
            {
                "name": "db",
                "image": "postgres:15",
                "replicas": 1,
                "env": {"POSTGRES_PASSWORD": "example"},
            },
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("""# JWT CLI Orchestrator configuration
""" + yaml.safe_dump(starter))
    typer.secho(f"Skeleton config written to {output}", fg=typer.colors.GREEN)


@auth_app = typer.Typer(name="auth", help="Authentication utilities")
app.add_typer(auth_app, name="auth")


@auth_app.command()
def login(
    username: str = Option(..., "--user", "-u", help="Username for the token"),
    role: str = Option("viewer", "--role", "-r", help="Role to embed in the token"),
):
    """Generate and store a JWT for a user."""
    token = auth.create_token(username, role)
    typer.secho(f"Token for {username} (role: {role}) created and stored.", fg=typer.colors.GREEN)
    typer.echo(token)


@auth_app.command()
def verify(
    token: Optional[str] = Option(None, "--token", "-t", help="JWT string to verify"),
    username: Optional[str] = Option(None, "--user", "-u", help="Username whose stored token will be verified"),
):
    """Verify a JWT either passed directly or retrieved from the keyring."""
    if not token and username:
        token = auth.get_stored_token(username)
        if not token:
            typer.secho(f"No stored token for user {username}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
    if not token:
        typer.secho("Either --token or --user must be provided", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    try:
        payload = auth.verify_token(token)
        typer.secho("Token is valid! Payload:", fg=typer.colors.GREEN)
        typer.echo(payload)
    except PermissionError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def deploy(
    target: str = Argument("all", help="Service name or 'all' to deploy every service"),
    config_path: Path = Option("config.yaml", "--config", "-c", help="Path to the deployment config"),
    username: str = Option(..., "--user", "-u", help="Username whose JWT will be used"),
):
    """Deploy services defined in the config after verifying the caller's JWT."""
    # Load and validate config
    try:
        cfg = config.DeployConfig.load(config_path)
    except Exception as exc:
        typer.secho(f"Failed to load config: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Retrieve and verify token
    token = auth.get_stored_token(username)
    if not token:
        typer.secho(f"No token found for user {username}. Please run 'jwt-cli auth login' first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    try:
        payload = auth.verify_token(token)
    except PermissionError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Simple RBAC check
    allowed_roles = {"admin", "deployer"}
    if payload.get("role") not in allowed_roles:
        typer.secho(f"User role '{payload.get('role')}' is not permitted to deploy.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Determine which services to act on
    services = cfg.services if target == "all" else [svc for svc in cfg.services if svc.name == target]
    if not services:
        typer.secho(f"No matching service(s) for target '{target}'.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    merged_env = cfg.merge_env()
    for svc in services:
        env = merged_env[svc.name]
        typer.secho(f"Deploying {svc.name} (image={svc.image}, replicas={svc.replicas})", fg=typer.colors.CYAN)
        # Placeholder for real deployment logic – here we just simulate
        typer.echo(f"  Using env: {env}")
        # In a real implementation we would invoke Docker/Kubectl/Helm APIs
    typer.secho("Deployment finished.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
