"""Data models for src-trainer."""

from pydantic import BaseModel


class AppInfo(BaseModel):
    """Basic application metadata model."""

    name: str = "SRC Trainer"
    version: str = "0.1.0"
