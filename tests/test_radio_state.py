"""Unit tests for simulator radio UI state transitions."""

from __future__ import annotations

import unittest

from src_trainer.components.radio_state import (
    CHANNEL_70_VOICE_MESSAGE,
    DEFAULT_CHANNEL,
    MAX_CHANNEL,
    MIN_CHANNEL,
    RADIO_OFF_MESSAGE,
    RadioState,
)
from src_trainer.models import RadioAction


class RadioStateTests(unittest.TestCase):
    def test_radio_starts_off(self) -> None:
        radio = RadioState()

        self.assertFalse(radio.power)
        self.assertEqual(DEFAULT_CHANNEL, radio.channel)
        self.assertFalse(radio.tx)
        self.assertTrue(radio.rx)
        self.assertFalse(radio.standby)
        self.assertFalse(radio.display_active)

    def test_power_on_emits_backend_action(self) -> None:
        radio = RadioState()

        command = radio.toggle_power()

        self.assertTrue(radio.power)
        self.assertTrue(radio.standby)
        self.assertTrue(radio.display_active)
        self.assertIsNotNone(command)
        self.assertEqual(RadioAction.POWER_ON, command.action)

    def test_channel_controls_update_only_when_powered(self) -> None:
        radio = RadioState(channel=DEFAULT_CHANNEL)

        radio.channel_up()
        self.assertEqual(DEFAULT_CHANNEL, radio.channel)
        self.assertEqual(RADIO_OFF_MESSAGE, radio.last_feedback)
        self.assertTrue(radio.last_mistake)

        radio.toggle_power()
        radio.channel_up()
        self.assertEqual(DEFAULT_CHANNEL + 1, radio.channel)
        radio.channel_down()
        self.assertEqual(DEFAULT_CHANNEL, radio.channel)

        radio.enter_channel(72)
        self.assertEqual(72, radio.channel)

    def test_channel_controls_are_bounded(self) -> None:
        radio = RadioState(power=True, channel=MIN_CHANNEL)

        radio.channel_down()
        self.assertEqual(MIN_CHANNEL, radio.channel)

        radio.channel = MAX_CHANNEL
        radio.channel_up()
        self.assertEqual(MAX_CHANNEL, radio.channel)

    def test_ch16_sets_channel_and_emits_backend_action(self) -> None:
        radio = RadioState(power=True, channel=72)

        command = radio.press_ch16()

        self.assertEqual(DEFAULT_CHANNEL, radio.channel)
        self.assertIsNotNone(command)
        self.assertEqual(RadioAction.PRESS_CH16, command.action)

    def test_powered_off_commands_are_ignored_except_cover(self) -> None:
        radio = RadioState(channel=72)

        self.assertIsNone(radio.press_ch16())
        self.assertEqual(72, radio.channel)
        self.assertIsNone(radio.set_working_channel())
        self.assertIsNone(radio.hold_distress())
        self.assertIsNone(radio.hold_ptt())
        self.assertIsNone(radio.release_ptt())
        self.assertIsNone(radio.transmit_phrase())
        self.assertEqual(RADIO_OFF_MESSAGE, radio.last_feedback)

        cover_command = radio.toggle_distress_cover()
        self.assertTrue(radio.distress_cover_open)
        self.assertIsNone(cover_command)

    def test_distress_cover_emits_when_opened_while_powered(self) -> None:
        radio = RadioState(power=True)

        command = radio.toggle_distress_cover()

        self.assertTrue(radio.distress_cover_open)
        self.assertIsNotNone(command)
        self.assertEqual(RadioAction.OPEN_DISTRESS_COVER, command.action)

    def test_distress_requires_power_and_open_cover(self) -> None:
        radio = RadioState(power=True)

        self.assertIsNone(radio.hold_distress())

        radio.toggle_distress_cover()
        command = radio.hold_distress()

        self.assertIsNotNone(command)
        self.assertEqual(RadioAction.HOLD_DISTRESS, command.action)

    def test_set_working_channel_emits_live_channel_value(self) -> None:
        radio = RadioState(power=True, channel=72)

        command = radio.set_working_channel()

        self.assertIsNotNone(command)
        self.assertEqual(RadioAction.SET_CHANNEL, command.action)
        self.assertEqual("72", command.value)

    def test_ptt_and_release_update_tx_rx_state(self) -> None:
        radio = RadioState(power=True)

        hold_command = radio.hold_ptt()
        self.assertIsNotNone(hold_command)
        self.assertEqual(RadioAction.HOLD_PTT, hold_command.action)
        self.assertTrue(radio.tx)
        self.assertFalse(radio.rx)
        self.assertFalse(radio.standby)

        release_command = radio.release_ptt()
        self.assertIsNotNone(release_command)
        self.assertEqual(RadioAction.RELEASE_PTT, release_command.action)
        self.assertFalse(radio.tx)
        self.assertTrue(radio.rx)
        self.assertTrue(radio.standby)

    def test_transmit_phrase_uses_current_phrase(self) -> None:
        radio = RadioState(power=True, phrase="  Mayday voice call  ")

        command = radio.transmit_phrase()

        self.assertIsNotNone(command)
        self.assertEqual(RadioAction.SPEAK_PHRASE, command.action)
        self.assertEqual("Mayday voice call", command.value)

    def test_channel_70_voice_transmission_is_rejected(self) -> None:
        radio = RadioState(power=True, channel=70, phrase="Radio check")

        self.assertIsNone(radio.hold_ptt())
        self.assertEqual(CHANNEL_70_VOICE_MESSAGE, radio.last_feedback)
        self.assertTrue(radio.last_mistake)

        self.assertIsNone(radio.transmit_phrase())
        self.assertEqual(CHANNEL_70_VOICE_MESSAGE, radio.last_feedback)
        self.assertTrue(radio.last_mistake)


if __name__ == "__main__":
    unittest.main()
