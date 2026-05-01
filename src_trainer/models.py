"""Data models for src-trainer."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


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


class ScenarioContext(BaseModel):
    what_is_happening: str = ""
    concerns: str = "your vessel"
    user_role: str = "radio operator"
    known_vessels: list[str] = Field(default_factory=list)
    position: str | None = None
    risk_level: str = "training"
    current_objective: str = ""


class CorrectSequenceItem(BaseModel):
    title: str
    action: RadioAction | None = None
    value: str | None = None
    message_structure: str = ""
    why_it_matters: str = ""
    common_mistakes: list[str] = Field(default_factory=list)


class ScenarioStep(BaseModel):
    title: str
    expected_actions: list[ActionEvent] = Field(default_factory=list)
    required_actions: list[RadioAction] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    feedback_correct: str
    feedback_incorrect: str
    score_weight: int = Field(default=10, ge=1)
    event: str | None = None
    objective: str | None = None
    message_elements: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)


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
    context: ScenarioContext = Field(default_factory=ScenarioContext)
    initial_conditions: list[str] = Field(default_factory=list)
    incoming_events: list[str] = Field(default_factory=list)
    required_assessment: str = ""
    correct_procedure: str = ""
    expected_message_elements: list[str] = Field(default_factory=list)
    possible_wrong_actions: list[str] = Field(default_factory=list)
    final_explanation: str = ""
    correct_sequence: list[CorrectSequenceItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def fill_training_metadata(self) -> "Scenario":
        if not self.context.what_is_happening:
            self.context.what_is_happening = self.situation
        if not self.context.current_objective and self.steps:
            self.context.current_objective = self.steps[0].objective or self.steps[0].title
        if not self.initial_conditions:
            self.initial_conditions = [self.situation]
        if not self.required_assessment:
            self.required_assessment = "Assess the signal priority, choose the correct channel, and transmit only when appropriate."
        if not self.correct_procedure:
            self.correct_procedure = "Follow the expected radio sequence for this scenario and keep transmissions brief."
        if not self.final_explanation:
            self.final_explanation = "The correct outcome uses the right priority signal, channel, and message structure without unnecessary transmissions."
        if not self.correct_sequence:
            sequence: list[CorrectSequenceItem] = []
            for step in self.steps:
                for expected in step.expected_actions:
                    sequence.append(
                        CorrectSequenceItem(
                            title=step.title,
                            action=expected.action,
                            value=expected.value,
                            message_structure=", ".join(step.message_elements or self.expected_message_elements),
                            why_it_matters=step.objective or step.feedback_correct,
                            common_mistakes=step.common_mistakes or self.possible_wrong_actions,
                        )
                    )
            self.correct_sequence = sequence
        return self
