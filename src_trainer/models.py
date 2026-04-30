"""Data models for src-trainer."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class AppInfo(BaseModel):
    """Basic application metadata model."""

    name: str = "SRC Trainer"
    version: str = "0.1.0"


class ScenarioCategory(StrEnum):
    distress = "distress"
    urgency = "urgency"
    safety = "safety"
    routine = "routine"
    dsc = "dsc"
    receive = "receive"
    explore = "explore"


class RadioAction(StrEnum):
    POWER_ON = "POWER_ON"
    SET_CHANNEL = "SET_CHANNEL"
    PRESS_CH16 = "PRESS_CH16"
    OPEN_DISTRESS_COVER = "OPEN_DISTRESS_COVER"
    HOLD_DISTRESS = "HOLD_DISTRESS"
    HOLD_PTT = "HOLD_PTT"
    SPEAK_PHRASE = "SPEAK_PHRASE"
    RELEASE_PTT = "RELEASE_PTT"


class ActionEvent(BaseModel):
    action: RadioAction
    value: str | None = None


class ScenarioStep(BaseModel):
    title: str
    expected_actions: list[ActionEvent] = Field(default_factory=list)
    required_actions: list[RadioAction] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    feedback_correct: str
    feedback_incorrect: str
    score_weight: int = Field(default=10, ge=1)


class Scenario(BaseModel):
    id: str
    title: str
    description: str
    category: ScenarioCategory
    difficulty: str
    situation: str
    learning_objectives: list[str]
    steps: list[ScenarioStep]
    pass_score: int = Field(ge=1, le=100)
