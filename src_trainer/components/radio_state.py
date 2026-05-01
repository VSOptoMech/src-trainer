"""State transitions for the simulator radio faceplate."""

from __future__ import annotations

from dataclasses import dataclass

from src_trainer.models import RadioAction

MIN_CHANNEL = 1
MAX_CHANNEL = 88
DEFAULT_CHANNEL = 16
CHANNEL_70 = 70
RADIO_OFF_MESSAGE = "Radio is off. Turn it on first."
CHANNEL_70_VOICE_MESSAGE = "Channel 70 is DSC only. Voice transmission is not allowed."


@dataclass(frozen=True)
class RadioCommand:
    """Backend action emitted by a radio state transition."""

    action: RadioAction
    value: str | None = None


@dataclass
class RadioState:
    """UI state for a generic marine VHF radio."""

    power: bool = False
    channel: int = DEFAULT_CHANNEL
    tx: bool = False
    rx: bool = True
    hi_power: bool = True
    standby: bool = False
    distress_cover_open: bool = False
    phrase: str = ""
    last_feedback: str = ""
    last_mistake: bool = False

    @property
    def display_active(self) -> bool:
        return self.power

    def reset(self, *, channel: int | str | None = DEFAULT_CHANNEL) -> None:
        self.power = False
        self.channel = normalize_channel(channel)
        self.tx = False
        self.rx = True
        self.hi_power = True
        self.standby = False
        self.distress_cover_open = False
        self.phrase = ""
        self._set_feedback("")

    def toggle_power(self) -> RadioCommand | None:
        self.power = not self.power
        self.tx = False
        self.rx = True
        self.standby = self.power
        if self.power:
            self._set_feedback("Radio powered on. LCD active.")
            return RadioCommand(RadioAction.POWER_ON)
        self._set_feedback("Radio powered off.")
        return None

    def channel_up(self) -> None:
        if not self._require_power():
            return
        self.channel = min(MAX_CHANNEL, self.channel + 1)
        self._set_feedback(f"Channel {self.channel} selected.")

    def channel_down(self) -> None:
        if not self._require_power():
            return
        self.channel = max(MIN_CHANNEL, self.channel - 1)
        self._set_feedback(f"Channel {self.channel} selected.")

    def enter_channel(self, value: int | str | None) -> None:
        if not self._require_power():
            return
        self.channel = normalize_channel(value)
        self._set_feedback(f"Channel {self.channel} selected.")

    def press_ch16(self) -> RadioCommand | None:
        if not self._require_power():
            return None
        self.channel = DEFAULT_CHANNEL
        self._set_feedback("Switched to Channel 16.")
        return RadioCommand(RadioAction.PRESS_CH16)

    def set_working_channel(self) -> RadioCommand | None:
        if not self._require_power():
            return None
        self._set_feedback(f"Working channel set to {self.channel}.")
        return RadioCommand(RadioAction.SET_CHANNEL, str(self.channel))

    def toggle_hi_lo(self) -> None:
        if not self._require_power():
            return
        self.hi_power = not self.hi_power
        self._set_feedback(f"Transmit power set to {'HI' if self.hi_power else 'LO'}.")

    def toggle_distress_cover(self) -> RadioCommand | None:
        self.distress_cover_open = not self.distress_cover_open
        if self.power and self.distress_cover_open:
            self._set_feedback("Distress cover opened.")
            return RadioCommand(RadioAction.OPEN_DISTRESS_COVER)
        if self.distress_cover_open:
            self._set_feedback("Distress cover opened. Radio is still off.")
        else:
            self._set_feedback("Distress cover closed.")
        return None

    def hold_distress(self) -> RadioCommand | None:
        if not self._require_power():
            return None
        if not self.distress_cover_open:
            self._set_feedback("Open the distress cover before pressing DISTRESS.", mistake=True)
            return None
        self._set_feedback("Distress button held.")
        return RadioCommand(RadioAction.HOLD_DISTRESS)

    def hold_ptt(self) -> RadioCommand | None:
        if not self._require_power():
            return None
        if self.channel == CHANNEL_70:
            self._set_feedback(CHANNEL_70_VOICE_MESSAGE, mistake=True)
            return None
        self.tx = True
        self.rx = False
        self.standby = False
        self._set_feedback("PTT held. Transmitter active.")
        return RadioCommand(RadioAction.HOLD_PTT)

    def release_ptt(self) -> RadioCommand | None:
        if not self._require_power():
            return None
        self.tx = False
        self.rx = True
        self.standby = True
        self._set_feedback("PTT released. Receiver active.")
        return RadioCommand(RadioAction.RELEASE_PTT)

    def transmit_phrase(self) -> RadioCommand | None:
        if not self._require_power():
            return None
        if self.channel == CHANNEL_70:
            self._set_feedback(CHANNEL_70_VOICE_MESSAGE, mistake=True)
            return None
        self._set_feedback("Voice message transmitted.")
        return RadioCommand(RadioAction.SPEAK_PHRASE, self.phrase.strip())

    def clear_feedback(self) -> None:
        self._set_feedback("")

    def _require_power(self) -> bool:
        if self.power:
            return True
        self._set_feedback(RADIO_OFF_MESSAGE, mistake=True)
        return False

    def _set_feedback(self, message: str, *, mistake: bool = False) -> None:
        self.last_feedback = message
        self.last_mistake = mistake


def normalize_channel(value: int | str | None) -> int:
    """Return a bounded VHF channel number for display and commands."""
    if value is None:
        return DEFAULT_CHANNEL
    try:
        channel = int(str(value).strip())
    except ValueError:
        return DEFAULT_CHANNEL
    return max(MIN_CHANNEL, min(MAX_CHANNEL, channel))
