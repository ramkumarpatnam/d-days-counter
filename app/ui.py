"""User interface: main window + add/edit dialog (Tkinter)."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk
from typing import Optional

from app.model import Event, EventStore
from app.timer import compute_row


class EventDialog:
    """Add / edit modal dialog."""

    def __init__(self, parent: tk.Tk, event: Optional[Event]) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Add / Edit Event" if event is None else "Edit Event")
        self.window.transient(parent)
        self.window.grab_set()
        self.result: Optional[dict] = None

        label_var = tk.StringVar()
        date_var = tk.StringVar()
        if event is not None:
            label_var.set(event.label)
            date_var.set(event.target_date)

        self._build(label_var, date_var)

        label_var.trace_add("write", lambda *_: self._on_change())
        date_var.trace_add("write", lambda *_: self._on_change())

    def _build(self, label_var: tk.StringVar, date_var: tk.StringVar) -> None:
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="x")

        ttk.Label(frame, text="Label:").grid(row=0, column=0, sticky="w", pady=4)
        label_entry = ttk.Entry(frame, textvariable=label_var, width=40)
        label_entry.grid(row=0, column=1, sticky="we", pady=4)
        label_entry.focus()

        ttk.Label(frame, text="Target date (YYYY-MM-DD):").grid(
            row=1, column=0, sticky="w", pady=4
        )
        date_entry = ttk.Entry(frame, textvariable=date_var, width=40)
        date_entry.grid(row=1, column=1, sticky="we", pady=4)
        date_entry.bind("<KeyRelease>", lambda _e: self._try_parse(date_var.get()))

        self.date_entry = date_entry
        self.date_error = ttk.Label(frame, text="", foreground="red")
        self.date_error.grid(row=2, column=1, sticky="w", pady=(0, 6))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=1, sticky="e")
        ttk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side="right", padx=4)
        self.ok_btn = ttk.Button(btn_frame, text="OK", command=self._ok)
        self.ok_btn.pack(side="right")

        self.window.wait_window(self.window)

    def _try_parse(self, raw: str) -> None:
        try:
            date.fromisoformat(raw)
            self.date_error.config(text="")
        except ValueError:
            self.date_error.config(text="Invalid date. Use YYYY-MM-DD.")

    def _on_change(self) -> None:
        self.ok_btn.configure(state="disabled" if self.date_error.cget("text") else "normal")

    def _cancel(self) -> None:
        self.result = None
        self.window.destroy()

    def _ok(self) -> None:
        label = self.date_entry.master.grid_slaves(row=0, column=1)[0].get()
        date_val = self.date_entry.master.grid_slaves(row=1, column=1)[0].get()
        self._try_parse(date_val)
        if self.date_error.cget("text"):
            return
        self.result = {"label": label, "target_date": date_val}
        self.window.destroy()


class MainWindow:
    """Main application window."""

    def __init__(self, store: EventStore):
        self.root = tk.Tk()
        self.root.title("Days Counter")
        self.root.geometry("800x300")
        self.store = store

        columns = ("label", "target_date", "status", "count")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col, header in zip(
            columns, ("Label", "Target Date", "Status", "Time Remaining / Elapsed")
        ):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=180)
        self.tree.column("count", width=220)

        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(toolbar, text="Add", command=self.add_event).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Edit", command=self.edit_event).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Delete", command=self.delete_event).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Close", command=self.on_close).pack(side="right", padx=4)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(1000, self._tick)

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
        for ev in self._events:
            status, count = compute_row(ev)
            self.tree.insert("", "end", iid=ev.id, values=(
                ev.label, ev.target_date, status, count
            ))

    def _tick(self) -> None:
        for item in self.tree.get_children():
            self.tree.set(item, "count", compute_row(
                self._events[[i for i, e in enumerate(self._events) if e.id == item][0]]
            )[1])
        self.root.after(1000, self._tick)

    def on_close(self) -> None:
        self.store.save(self._events)
        self.root.destroy()

    def run(self) -> None:
        self._refresh()
        self.root.mainloop()