"""Select-mode picker — choose one item from a list."""

from __future__ import annotations

from typing import Any, ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import DataTable, Input, Static


class PickerApp(App[str | None]):
    """Generic picker app — displays a table, returns the selected item's key."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #title {
        text-align: center;
        padding: 1 0;
        color: $text-muted;
    }
    #hint {
        text-align: center;
        padding: 1 0;
        color: $text-muted;
    }
    #filter-input {
        display: none;
        padding: 0 1;
    }
    #filter-input.visible {
        display: block;
    }
    DataTable {
        height: auto;
        max-height: 20;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
        Binding("slash", "filter", "Filter"),
    ]

    def __init__(
        self,
        title: str,
        columns: list[str],
        rows: list[dict[str, Any]],
        key_field: str = "id",
    ) -> None:
        super().__init__()
        self._title = title
        self._columns = columns
        self._rows = rows
        self._key_field = key_field
        self._all_rows = list(rows)
        self._filter_active = False

    def compose(self) -> ComposeResult:
        yield Static(self._title, id="title")
        yield Input(placeholder="Filter...", id="filter-input", disabled=True)
        table: DataTable[str] = DataTable(cursor_type="row")
        for col in self._columns:
            table.add_column(col, key=col)
        for row in self._rows:
            table.add_row(
                *[str(row.get(col, "")) for col in self._columns],
                key=str(row[self._key_field]),
            )
        yield table
        yield Static(
            "\u2191/\u2193 navigate \u00b7 / filter \u00b7 enter select \u00b7 esc cancel",
            id="hint",
        )

    def on_mount(self) -> None:
        """Ensure the DataTable has focus on startup."""
        self.query_one(DataTable).focus()

    def action_filter(self) -> None:
        """Show the filter input and focus it."""
        if self._filter_active:
            return
        self._filter_active = True
        filter_input = self.query_one("#filter-input", Input)
        filter_input.disabled = False
        filter_input.add_class("visible")
        filter_input.value = ""
        filter_input.focus()

    def _close_filter(self) -> None:
        """Hide the filter input, restore all rows, and refocus the table."""
        self._filter_active = False
        filter_input = self.query_one("#filter-input", Input)
        filter_input.remove_class("visible")
        filter_input.value = ""
        filter_input.disabled = True
        self._repopulate_table(self._all_rows)
        self.query_one(DataTable).focus()

    def _repopulate_table(self, rows: list[dict[str, Any]]) -> None:
        """Clear and repopulate the table with the given rows."""
        table = self.query_one(DataTable)
        table.clear()
        for row in rows:
            table.add_row(
                *[str(row.get(col, "")) for col in self._columns],
                key=str(row[self._key_field]),
            )

    @on(Input.Changed, "#filter-input")
    def on_filter_changed(self, event: Input.Changed) -> None:
        """Live-filter table rows as the user types."""
        query = event.value.strip().lower()
        if not query:
            self._repopulate_table(self._all_rows)
            return
        filtered = [
            row
            for row in self._all_rows
            if any(query in str(row.get(col, "")).lower() for col in self._columns)
        ]
        self._repopulate_table(filtered)

    @on(Input.Submitted, "#filter-input")
    def on_filter_submitted(self, _event: Input.Submitted) -> None:
        """When Enter is pressed in the filter, refocus the table."""
        self.query_one(DataTable).focus()

    def on_key(self, event: Any) -> None:
        """Handle Escape in filter input to close the filter."""
        if self._filter_active and event.key == "escape":
            event.prevent_default()
            event.stop()
            self._close_filter()

    def action_select(self) -> None:
        table = self.query_one(DataTable)
        if table.row_count > 0:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            key = row_key.value if row_key.value is not None else str(row_key)
            self.exit(key)
        else:
            self.exit(None)

    def action_cancel(self) -> None:
        self.exit(None)

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        self.exit(str(event.row_key.value))


def pick_from_list(
    title: str,
    columns: list[str],
    rows: list[dict[str, Any]],
    key_field: str = "id",
) -> str | None:
    """Show a picker and return the selected key, or None if cancelled."""
    app = PickerApp(title, columns, rows, key_field)
    return app.run()
