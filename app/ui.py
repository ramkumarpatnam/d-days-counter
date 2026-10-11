"""User interface: main window + add/edit dialog (Tkinter)."""

from __future__ import annotations

import tkinter as tk
import calendar
from datetime import date
from tkinter import ttk
from typing import Optional

from app.model import Event, EventStore
from app.timer import compute_row, format_calendar_span


EVENT_COLORS = {
    "Blue": "blue",
    "Mint": "mint",
    "Purple": "purple",
    "Amber": "amber",
    "Rose": "rose",
    "Slate": "slate",
}

EVENT_COLOR_VALUES = {
    "blue": ("#EAF0FF", "#3157B7", "#26334B", "#C2D3FF"),
    "mint": ("#E6F6F0", "#167A56", "#263B37", "#A8E8D0"),
    "purple": ("#F1EBFF", "#7046B8", "#352F43", "#D8C6FF"),
    "amber": ("#FFF3DB", "#93600A", "#3D372C", "#F5D99E"),
    "rose": ("#FCE9ED", "#B33D59", "#3D3038", "#F2BBC9"),
    "slate": ("#EDF0F5", "#536176", "#2D3542", "#C9D2E0"),
}


class EventDialog:
    """Add / edit modal dialog."""

    def __init__(self, parent: tk.Tk, event: Optional[Event]) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Add an event" if event is None else "Edit event")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        self.result: Optional[dict] = None
        self.calendar_window: Optional[tk.Toplevel] = None
        self.calendar_month = date.today().replace(day=1)

        self.label_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.color_var = tk.StringVar(value="Blue")
        if event is not None:
            self.label_var.set(event.label)
            self.date_var.set(event.target_date)
            self.color_var.set(
                next(
                    (name for name, value in EVENT_COLORS.items() if value == event.color),
                    "Blue",
                )
            )

        self._build()

        self.label_var.trace_add("write", lambda *_: self._on_change())
        self.date_var.trace_add("write", lambda *_: self._on_change())
        self._on_change()
        self.window.wait_window(self.window)

    def _build(self) -> None:
        frame = ttk.Frame(self.window, style="Dialog.TFrame", padding=22)
        frame.pack(fill="x")

        ttk.Label(frame, text="Event name", style="DialogHeading.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )
        ttk.Label(frame, text="Name", style="Dialog.TLabel").grid(
            row=1, column=0, sticky="w", pady=6
        )
        self.label_entry = ttk.Entry(frame, textvariable=self.label_var, width=38)
        self.label_entry.grid(row=1, column=1, sticky="we", pady=6)

        ttk.Label(frame, text="Target date", style="Dialog.TLabel").grid(
            row=2, column=0, sticky="w", pady=6
        )
        date_controls = ttk.Frame(frame, style="Dialog.TFrame")
        date_controls.grid(row=2, column=1, sticky="we", pady=6)
        self.date_entry = ttk.Entry(
            date_controls, textvariable=self.date_var, width=27
        )
        self.date_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(
            date_controls, text="Select date", command=self._open_calendar
        ).pack(side="left", padx=(8, 0))

        ttk.Label(frame, text="Event color", style="Dialog.TLabel").grid(
            row=3, column=0, sticky="w", pady=6
        )
        color_picker = ttk.Combobox(
            frame,
            textvariable=self.color_var,
            values=tuple(EVENT_COLORS),
            state="readonly",
            width=35,
        )
        color_picker.grid(row=3, column=1, sticky="we", pady=6)

        ttk.Label(
            frame, text="Date format: YYYY-MM-DD (e.g. 2026-10-11)",
            style="DialogHint.TLabel",
        ).grid(
            row=4, column=1, sticky="w", pady=(0, 4)
        )
        self.date_error = ttk.Label(frame, text="", style="DialogError.TLabel")
        self.date_error.grid(row=5, column=1, sticky="w", pady=(0, 6))

        btn_frame = ttk.Frame(frame, style="Dialog.TFrame")
        btn_frame.grid(row=6, column=1, sticky="e", pady=(8, 0))
        ttk.Button(btn_frame, text="Cancel", command=self._cancel).pack(
            side="right", padx=(8, 0)
        )
        self.ok_btn = ttk.Button(
            btn_frame, text="Save event", command=self._ok, style="Accent.TButton"
        )
        self.ok_btn.pack(side="right")
        frame.columnconfigure(1, weight=1)
        self.label_entry.focus_set()

    def _open_calendar(self) -> None:
        if self.calendar_window is not None and self.calendar_window.winfo_exists():
            self.calendar_window.lift()
            return
        try:
            self.calendar_month = date.fromisoformat(
                self.date_var.get().strip()
            ).replace(day=1)
        except ValueError:
            self.calendar_month = date.today().replace(day=1)

        self.calendar_window = tk.Toplevel(self.window)
        self.calendar_window.title("Select a date")
        self.calendar_window.transient(self.window)
        self.calendar_window.resizable(False, False)
        body = ttk.Frame(
            self.calendar_window, style="Dialog.TFrame", padding=14
        )
        body.pack()
        self.calendar_header = ttk.Frame(body, style="Dialog.TFrame")
        self.calendar_header.pack(fill="x", pady=(0, 8))
        ttk.Button(
            self.calendar_header, text="<", width=3,
            command=lambda: self._shift_calendar_month(-1),
        ).pack(side="left")
        self.month_var = tk.StringVar()
        self.month_picker = ttk.Combobox(
            self.calendar_header, textvariable=self.month_var,
            values=tuple(calendar.month_name)[1:], state="readonly", width=12,
        )
        self.month_picker.pack(side="left", padx=(8, 4))
        self.month_picker.bind("<<ComboboxSelected>>", self._calendar_month_selected)
        self.year_var = tk.StringVar()
        self.year_picker = ttk.Combobox(
            self.calendar_header, textvariable=self.year_var,
            values=(),
            state="readonly", width=7,
        )
        self.year_picker.pack(side="left", padx=4)
        self.year_picker.bind("<<ComboboxSelected>>", self._calendar_year_selected)
        ttk.Button(
            self.calendar_header, text=">", width=3,
            command=lambda: self._shift_calendar_month(1),
        ).pack(side="right")
        self.calendar_grid = ttk.Frame(body, style="Dialog.TFrame")
        self.calendar_grid.pack()
        self._render_calendar()
        self.calendar_window.grab_set()

    def _shift_calendar_month(self, amount: int) -> None:
        month_index = self.calendar_month.month - 1 + amount
        year = self.calendar_month.year + month_index // 12
        month = month_index % 12 + 1
        self.calendar_month = date(year, month, 1)
        self._render_calendar()

    def _calendar_month_selected(self, _event: tk.Event) -> None:
        month = self.month_picker.current() + 1
        self.calendar_month = self.calendar_month.replace(month=month, day=1)
        self._render_calendar()

    def _calendar_year_selected(self, _event: tk.Event) -> None:
        self.calendar_month = self.calendar_month.replace(
            year=int(self.year_var.get()), day=1
        )
        self._render_calendar()

    def _render_calendar(self) -> None:
        for child in self.calendar_grid.winfo_children():
            child.destroy()
        self.month_var.set(self.calendar_month.strftime("%B"))
        self.year_var.set(str(self.calendar_month.year))
        first_year = max(1, self.calendar_month.year - 100)
        last_year = min(9999, self.calendar_month.year + 100)
        self.year_picker.configure(
            values=tuple(str(year) for year in range(first_year, last_year + 1))
        )
        for column, day_name in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
            ttk.Label(
                self.calendar_grid, text=day_name, style="CalendarHeading.TLabel",
                anchor="center", width=4,
            ).grid(row=0, column=column, padx=1, pady=(2, 6))

        selected = None
        try:
            selected = date.fromisoformat(self.date_var.get().strip())
        except ValueError:
            pass

        for row, week in enumerate(
            calendar.monthcalendar(self.calendar_month.year, self.calendar_month.month),
            start=1,
        ):
            for column, day_number in enumerate(week):
                if day_number == 0:
                    ttk.Label(self.calendar_grid, text="", width=4).grid(
                        row=row, column=column, padx=1, pady=1
                    )
                    continue
                day = date(
                    self.calendar_month.year, self.calendar_month.month, day_number
                )
                style = (
                    "CalendarSelected.TButton"
                    if day == selected else "Calendar.TButton"
                )
                ttk.Button(
                    self.calendar_grid, text=str(day_number), width=4, style=style,
                    command=lambda chosen=day: self._select_calendar_date(chosen),
                ).grid(row=row, column=column, padx=1, pady=1)

    def _select_calendar_date(self, selected: date) -> None:
        self.date_var.set(selected.isoformat())
        if self.calendar_window is not None:
            self.calendar_window.destroy()
            self.calendar_window = None

    def _on_change(self) -> None:
        raw_date = self.date_var.get().strip()
        if not raw_date:
            self.date_error.config(text="")
        else:
            try:
                date.fromisoformat(raw_date)
                self.date_error.config(text="")
            except ValueError:
                self.date_error.config(text="Enter a valid date in YYYY-MM-DD format.")
        valid = (
            bool(self.label_var.get().strip())
            and bool(raw_date)
            and not self.date_error.cget("text")
        )
        self.ok_btn.configure(state="normal" if valid else "disabled")

    def _cancel(self) -> None:
        self.result = None
        self.window.destroy()

    def _ok(self) -> None:
        self._on_change()
        if str(self.ok_btn["state"]) == "disabled":
            return
        self.result = {
            "label": self.label_var.get().strip(),
            "target_date": self.date_var.get().strip(),
            "color": EVENT_COLORS[self.color_var.get()],
        }
        self.window.destroy()


class MainWindow:
    """Main application window."""

    def __init__(self, store: EventStore):
        self.root = tk.Tk()
        self.root.title("Days Counter")
        self.root.geometry("1220x620")
        self.root.minsize(1080, 500)
        self.dark_mode = False
        self.root.configure(background="#F3F5F9")
        self.store = store
        self._configure_styles()

        shell = ttk.Frame(self.root, style="App.TFrame", padding=(28, 24, 28, 18))
        shell.pack(fill="both", expand=True)

        header = ttk.Frame(shell, style="App.TFrame")
        header.pack(fill="x", pady=(0, 20))

        title_area = ttk.Frame(header, style="App.TFrame")
        title_area.pack(side="left", fill="x", expand=True)
        ttk.Label(title_area, text="Days Counter", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_area,
            text="Keep the important dates in view.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))
        self.add_button = ttk.Button(
            header, text="+  Add event", command=self.add_event, style="Accent.TButton"
        )
        self.add_button.pack(side="right", anchor="center")
        self.theme_button = ttk.Button(
            header, text="Dark mode", command=self._toggle_theme
        )
        self.theme_button.pack(side="right", padx=(0, 10), anchor="center")

        section = ttk.Frame(shell, style="App.TFrame")
        section.pack(fill="both", expand=True)
        section_header = ttk.Frame(section, style="App.TFrame")
        section_header.pack(fill="x", pady=(0, 9))
        ttk.Label(section_header, text="YOUR EVENTS", style="Section.TLabel").pack(
            side="left"
        )
        self.event_count = ttk.Label(
            section_header, text="0 events", style="Hint.TLabel"
        )
        self.event_count.pack(side="right", padx=(12, 0))
        self.edit_button = ttk.Button(
            section_header, text="Edit", command=self.edit_event, state="disabled"
        )
        self.edit_button.pack(side="right", padx=(8, 0))
        self.delete_button = ttk.Button(
            section_header, text="Delete", command=self.delete_event, state="disabled"
        )
        self.delete_button.pack(side="right")

        table_frame = ttk.Frame(section, style="Card.TFrame", padding=1)
        table_frame.pack(fill="both", expand=True)

        columns = ("label", "target_date", "status", "count", "calendar_span")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.tree.heading("label", text="EVENT", anchor="w")
        self.tree.heading("target_date", text="TARGET DATE", anchor="w")
        self.tree.heading("status", text="STATUS", anchor="center")
        self.tree.heading("count", text="DAYS  /  TIME", anchor="center")
        self.tree.heading(
            "calendar_span", text="YEARS / MONTHS / DAYS / TIME", anchor="center"
        )
        self.tree.column("label", width=270, minwidth=180, anchor="w")
        self.tree.column("target_date", width=145, minwidth=120, anchor="w")
        self.tree.column("status", width=140, minwidth=110, anchor="center")
        self.tree.column("count", width=190, minwidth=170, anchor="center")
        self.tree.column("calendar_span", width=310, minwidth=285, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self._configure_event_colors()

        self.empty_state = ttk.Frame(table_frame, style="Empty.TFrame", padding=24)
        ttk.Label(self.empty_state, text="Nothing on the calendar yet", style="EmptyTitle.TLabel").pack()
        ttk.Label(
            self.empty_state,
            text="Add a birthday, trip, deadline, or any date you want to track.",
            style="EmptyBody.TLabel",
            wraplength=380,
            justify="center",
        ).pack(pady=(7, 16))
        ttk.Button(
            self.empty_state, text="Add your first event", command=self.add_event,
            style="Accent.TButton",
        ).pack()

        footer = ttk.Frame(shell, style="App.TFrame")
        footer.pack(fill="x", pady=(14, 0))
        self.hint_label = ttk.Label(
            footer, text="Select an event and choose Edit, double-click it, or press Enter.",
            style="Hint.TLabel"
        )
        self.hint_label.pack(side="left")

        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)
        self.tree.bind("<Double-1>", self._edit_selected)
        self.tree.bind("<Return>", self._edit_selected)
        self.root.bind("<Delete>", self._delete_selected)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(1000, self._tick)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        if self.dark_mode:
            app_bg, card_bg = "#151922", "#1D2430"
            primary, secondary, muted = "#F0F3F8", "#B9C3D2", "#929DB0"
            heading_bg = "#252E3D"
            selected_bg, selected_fg = "#3A465C", "#FFFFFF"
            entry_bg, border = "#1A202B", "#343E4E"
            accent, accent_active, disabled_bg = "#607FE8", "#4D6DD4", "#465168"
        else:
            app_bg, card_bg = "#F3F5F9", "#FFFFFF"
            primary, secondary, muted = "#172033", "#748096", "#8791A2"
            heading_bg = "#F7F8FB"
            selected_bg, selected_fg = "#E9EEFC", "#263248"
            entry_bg, border = "#FFFFFF", "#D6DCE7"
            accent, accent_active, disabled_bg = "#365FDB", "#284FC5", "#AAB6D4"

        self.root.configure(background=app_bg)
        style.configure("App.TFrame", background=app_bg)
        style.configure("Card.TFrame", background=border)
        style.configure("Empty.TFrame", background=card_bg)
        style.configure("Dialog.TFrame", background=card_bg)
        style.configure(
            "Dialog.TLabel", background=card_bg, foreground=primary,
            font=("Segoe UI", 10),
        )
        style.configure(
            "DialogHint.TLabel", background=card_bg, foreground=muted,
            font=("Segoe UI", 9),
        )
        style.configure(
            "DialogError.TLabel", background=card_bg, foreground="#EF7782",
            font=("Segoe UI", 9),
        )
        style.configure(
            "CalendarHeading.TLabel", background=card_bg, foreground=secondary,
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Calendar.TButton", padding=(4, 5), font=("Segoe UI", 9),
        )
        style.configure(
            "CalendarSelected.TButton", background=accent, foreground="#FFFFFF",
            padding=(4, 5), font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "CalendarSelected.TButton",
            background=[("active", accent_active)],
            foreground=[("active", "#FFFFFF")],
        )
        style.configure(
            "Title.TLabel", background=app_bg, foreground=primary,
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel", background=app_bg, foreground=secondary,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Section.TLabel", background=app_bg, foreground=secondary,
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Hint.TLabel", background=app_bg, foreground=muted,
            font=("Segoe UI", 9),
        )
        style.configure(
            "EmptyTitle.TLabel", background=card_bg, foreground=primary,
            font=("Segoe UI", 14, "bold"),
        )
        style.configure(
            "EmptyBody.TLabel", background=card_bg, foreground=secondary,
            font=("Segoe UI", 10),
        )
        style.configure(
            "DialogHeading.TLabel", background=card_bg, foreground=primary,
            font=("Segoe UI", 15, "bold")
        )
        style.configure("Error.TLabel", foreground="#EF7782", font=("Segoe UI", 9))
        style.configure(
            "Accent.TButton", background=accent, foreground="#FFFFFF",
            padding=(16, 9), font=("Segoe UI", 10, "bold"), borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", accent_active), ("disabled", disabled_bg)],
            foreground=[("disabled", "#F4F6FA")],
        )
        style.configure(
            "TButton", background=card_bg, foreground=primary,
            padding=(13, 7), font=("Segoe UI", 9), borderwidth=0,
        )
        style.map(
            "TButton",
            background=[("active", heading_bg), ("disabled", app_bg)],
            foreground=[("disabled", muted)],
        )
        style.configure(
            "TCombobox", fieldbackground=entry_bg, background=card_bg,
            foreground=primary, arrowcolor=primary, bordercolor=border,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", entry_bg)],
            foreground=[("readonly", primary)],
            selectbackground=[("readonly", entry_bg)],
            selectforeground=[("readonly", primary)],
        )
        self.root.option_add("*TCombobox*Listbox.background", entry_bg)
        self.root.option_add("*TCombobox*Listbox.foreground", primary)
        style.configure(
            "TEntry", fieldbackground=entry_bg, foreground=primary,
            insertcolor=primary, bordercolor=border, padding=(7, 6),
        )
        style.map(
            "TEntry",
            fieldbackground=[("disabled", app_bg), ("!disabled", entry_bg)],
            foreground=[("disabled", muted), ("!disabled", primary)],
        )
        style.configure(
            "Treeview", background=card_bg, fieldbackground=card_bg,
            foreground=primary, rowheight=42, borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading", background=heading_bg, foreground=secondary,
            padding=(12, 11), font=("Segoe UI", 8, "bold"), relief="flat",
        )
        style.map(
            "Treeview.Heading",
            background=[("active", border)],
        )
        style.map(
            "Treeview",
            background=[("selected", selected_bg)],
            foreground=[("selected", selected_fg)],
        )

    def _configure_event_colors(self) -> None:
        for name, (light_bg, light_fg, dark_bg, dark_fg) in EVENT_COLOR_VALUES.items():
            self.tree.tag_configure(
                f"event-{name}",
                background=dark_bg if self.dark_mode else light_bg,
                foreground=dark_fg if self.dark_mode else light_fg,
            )

    def _toggle_theme(self) -> None:
        self.dark_mode = not self.dark_mode
        self.theme_button.configure(
            text="Light mode" if self.dark_mode else "Dark mode"
        )
        self._configure_styles()
        self._configure_event_colors()

    # ----------------- menu actions -----------------
    def add_event(self) -> None:
        dialog = EventDialog(self.root, None)
        if dialog.result:
            event = Event(**dialog.result)
            self.store.save(self._events + [event])
            self._refresh()

    def edit_event(self) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        tag = selection[0]
        event = next(e for e in self._events if e.id == tag)
        dialog = EventDialog(self.root, event)
        if dialog.result:
            event.label = dialog.result["label"]
            event.target_date = dialog.result["target_date"]
            event.color = dialog.result["color"]
            self.store.save(self._events)
            self._refresh()

    def delete_event(self) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        tag = selection[0]
        self._events = [e for e in self._events if e.id != tag]
        self.store.save(self._events)
        self._refresh()

    # ----------------- core -----------------
    @property
    def _events(self) -> list[Event]:
        return self.store.load()

    def _refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        events = self._events
        self.event_count.configure(
            text=f"{len(events)} event" + ("" if len(events) == 1 else "s")
        )
        self.empty_state.place_forget()
        if not events:
            self.empty_state.place(relx=0.5, rely=0.5, anchor="center")
        self._configure_event_colors()
        for ev in events:
            status, count = compute_row(ev)
            color_tag = ev.color if ev.color in EVENT_COLOR_VALUES else "blue"
            self.tree.insert(
                "", "end", iid=ev.id,
                values=(
                    ev.label, ev.target_date, status, count,
                    format_calendar_span(ev),
                ),
                tags=(f"event-{color_tag}",),
            )
        self._on_selection_change()

    def _tick(self) -> None:
        events_by_id = {event.id: event for event in self._events}
        for item in self.tree.get_children():
            event = events_by_id.get(item)
            if event is not None:
                status, count = compute_row(event)
                self.tree.set(item, "status", status)
                self.tree.set(item, "count", count)
                self.tree.set(item, "calendar_span", format_calendar_span(event))
        self.root.after(1000, self._tick)

    def _on_selection_change(self, _event: Optional[tk.Event] = None) -> None:
        state = "normal" if self.tree.selection() else "disabled"
        self.edit_button.configure(state=state)
        self.delete_button.configure(state=state)

    def _edit_selected(self, _event: tk.Event) -> None:
        self.edit_event()

    def _delete_selected(self, _event: tk.Event) -> None:
        if self.tree.selection():
            self.delete_event()

    def on_close(self) -> None:
        self.store.save(self._events)
        self.root.destroy()

    def run(self) -> None:
        self._refresh()
        self.root.mainloop()