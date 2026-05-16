from __future__ import annotations

import yaml
from pathlib import Path
from typing import Literal, List, Optional

from pydantic import BaseModel, Field, ValidationError, validator


class ServiceConfig(BaseModel):
    name: str = Field(..., description="Unique service identifier")
    image: str = Field(..., description="Docker image reference")
    replicas: int = Field(1, ge=1, description="Number of instances to run")
    env: Optional[dict[str, str]] = Field(default_factory=dict)
    command: Optional[List[str]] = None

    @validator("name")
    def no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("service name must not contain spaces")
        return v


class DeployConfig(BaseModel):
    version: Literal["v1"] = "v1"
    services: List[ServiceConfig]
    global_env: Optional[dict[str, str]] = Field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> "DeployConfig":
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")
        data = yaml.safe_load(path.read_text())
        try:
            return cls.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"Invalid configuration: {exc}") from exc

    def merge_env(self) -> dict[str, dict[str, str]]:
        """Return a mapping of service name → merged env (global + service)."""
        merged: dict[str, dict[str, str]] = {}
        for svc in self.services:
            env = {**self.global_env, **(svc.env or {})}
            merged[svc.name] = env
        return merged
