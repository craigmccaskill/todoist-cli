"""Tests for TUI infrastructure."""

from __future__ import annotations

import pytest

from td.tui import is_available


class TestTuiAvailability:
    def test_is_available(self) -> None:
        assert is_available() is True

    def test_picker_imports(self) -> None:
        from td.tui.picker import PickerApp, pick_from_list

        assert PickerApp is not None
        assert pick_from_list is not None

    def test_domain_pickers_import(self) -> None:
        from td.tui.pickers import (
            pick_label,
            pick_priority,
            pick_project,
            pick_section,
            pick_task,
        )

        assert pick_task is not None
        assert pick_project is not None
        assert pick_label is not None
        assert pick_section is not None
        assert pick_priority is not None


class TestPickerApp:
    @pytest.mark.asyncio
    async def test_picker_app_creates(self) -> None:
        """Verify PickerApp can be instantiated with test data."""
        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name", "Value"],
            rows=[
                {"id": "1", "Name": "Alpha", "Value": "100"},
                {"id": "2", "Name": "Beta", "Value": "200"},
            ],
        )
        assert app is not None

    @pytest.mark.asyncio
    async def test_picker_app_cancel(self) -> None:
        """Verify cancel returns None."""
        from textual.pilot import Pilot

        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[{"id": "1", "Name": "Alpha"}],
        )
        async with app.run_test() as pilot:
            assert isinstance(pilot, Pilot)
            await pilot.press("escape")

        assert app.return_value is None

    @pytest.mark.asyncio
    async def test_picker_app_select(self) -> None:
        """Verify enter returns the selected key."""
        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[
                {"id": "first", "Name": "Alpha"},
                {"id": "second", "Name": "Beta"},
            ],
        )
        async with app.run_test() as pilot:
            await pilot.press("enter")

        assert app.return_value == "first"

    @pytest.mark.asyncio
    async def test_picker_app_navigate_and_select(self) -> None:
        """Verify navigating down then selecting returns second row."""
        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[
                {"id": "first", "Name": "Alpha"},
                {"id": "second", "Name": "Beta"},
            ],
        )
        async with app.run_test() as pilot:
            await pilot.press("down")
            await pilot.press("enter")

        assert app.return_value == "second"
