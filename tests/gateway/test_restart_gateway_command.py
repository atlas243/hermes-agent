"""Tests for /restart-gateway branch safety checks."""

from unittest.mock import patch, MagicMock

import pytest

from gateway.config import Platform
from gateway.platforms.base import MessageEvent
from gateway.session import SessionSource


def _make_event(text="/restart-gateway", platform=Platform.TELEGRAM,
                user_id="12345", chat_id="67890"):
    source = SessionSource(
        platform=platform,
        user_id=user_id,
        chat_id=chat_id,
        user_name="testuser",
    )
    return MessageEvent(text=text, source=source)


def _make_runner():
    from gateway.run import GatewayRunner
    runner = object.__new__(GatewayRunner)
    runner.adapters = {}
    runner._voice_mode = {}
    return runner


class TestRestartGatewayCommand:
    @pytest.mark.asyncio
    async def test_blocks_restart_on_wrong_branch(self):
        runner = _make_runner()
        event = _make_event()

        launchd_ok = MagicMock(returncode=0, stdout="loaded", stderr="")

        with patch("subprocess.run", return_value=launchd_ok), \
             patch("gateway.run.check_expected_live_branch", return_value=(False, "main", None)):
            result = await runner._handle_restart_gateway_command(event)

        assert "Refusing to restart gateway from branch 'main'" in result
        assert "blaize-customizations" in result

    @pytest.mark.asyncio
    async def test_blocks_restart_when_branch_cannot_be_verified(self):
        runner = _make_runner()
        event = _make_event()

        launchd_ok = MagicMock(returncode=0, stdout="loaded", stderr="")

        with patch("subprocess.run", return_value=launchd_ok), \
             patch("gateway.run.check_expected_live_branch", return_value=(False, None, "boom")):
            result = await runner._handle_restart_gateway_command(event)

        assert "Could not verify the active git branch" in result
        assert "boom" in result

    @pytest.mark.asyncio
    async def test_allows_restart_on_expected_branch(self):
        runner = _make_runner()
        event = _make_event()

        responses = [
            MagicMock(returncode=0, stdout="loaded", stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]

        with patch("subprocess.run", side_effect=responses), \
             patch("gateway.run.check_expected_live_branch", return_value=(True, "blaize-customizations", None)), \
             patch("subprocess.Popen") as mock_popen:
            result = await runner._handle_restart_gateway_command(event)

        assert "Restarting gateway" in result
        mock_popen.assert_called_once()