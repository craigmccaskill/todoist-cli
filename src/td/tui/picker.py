"""Select-mode picker — choose one item from a list."""

from __future__ import annotations

from typing import Any, ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import DataTable, Static


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
        self._all_rows = rows

    def compose(self) -> ComposeResult:
        yield Static(self._title, id="title")
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
            "↑/↓ navigate · enter select · esc cancel",
            id="hint",
        )

    def action_select(self) -> None:
        table = self.query_one(DataTable)
        if table.row_count > 0:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            self.exit(str(row_key))
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
