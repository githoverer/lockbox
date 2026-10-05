import tkinter as tk
from datetime import datetime, time
from pathlib import Path
from tkinter import filedialog, messagebox

from .policy import ApplicationPolicy, TimeWindow
from .scheduler import is_application_allowed
from .storage import PolicyStorage


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "policies.json"

DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


class LockboxDashboard:

    def __init__(self, root):

        self.root = root

        self.root.title("Lockbox")
        self.root.geometry("850x650")

        self.storage = PolicyStorage(DATA_FILE)
        self.policies = self.storage.load()

        # Temporary windows being added to the current policy.
        self.pending_windows = {
            day: []
            for day in DAYS
        }

        self.build_ui()
        self.refresh_list()

    def build_ui(self):

        title = tk.Label(
            self.root,
            text="Lockbox",
            font=("Arial", 24, "bold"),
        )
        title.pack(pady=(15, 2))

        subtitle = tk.Label(
            self.root,
            text="Application Access Control",
            font=("Arial", 11),
        )
        subtitle.pack()

        form = tk.Frame(self.root)
        form.pack(pady=15)

        # Application name
        tk.Label(
            form,
            text="Application Name",
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="e",
        )

        self.name_entry = tk.Entry(
            form,
            width=35,
        )
        self.name_entry.grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
        )

        # Executable
        tk.Label(
            form,
            text="Executable",
        ).grid(
            row=1,
            column=0,
            padx=5,
            pady=5,
            sticky="e",
        )

        self.exe_entry = tk.Entry(
            form,
            width=35,
        )
        self.exe_entry.grid(
            row=1,
            column=1,
            padx=5,
            pady=5,
        )

        tk.Button(
            form,
            text="Browse",
            command=self.browse_executable,
        ).grid(
            row=1,
            column=2,
            padx=5,
        )

        # Day selection
        tk.Label(
            form,
            text="Day",
        ).grid(
            row=2,
            column=0,
            padx=5,
            pady=5,
            sticky="e",
        )

        self.selected_day = tk.StringVar(
            value="monday"
        )

        day_menu = tk.OptionMenu(
            form,
            self.selected_day,
            *DAYS,
        )
        day_menu.config(width=12)
        day_menu.grid(
            row=2,
            column=1,
            padx=5,
            pady=5,
            sticky="w",
        )

        # Start time
        tk.Label(
            form,
            text="Start Time",
        ).grid(
            row=3,
            column=0,
            padx=5,
            pady=5,
            sticky="e",
        )

        self.start_entry = tk.Entry(
            form,
            width=12,
        )
        self.start_entry.grid(
            row=3,
            column=1,
            padx=5,
            pady=5,
            sticky="w",
        )

        # End time
        tk.Label(
            form,
            text="End Time",
        ).grid(
            row=4,
            column=0,
            padx=5,
            pady=5,
            sticky="e",
        )

        self.end_entry = tk.Entry(
            form,
            width=12,
        )
        self.end_entry.grid(
            row=4,
            column=1,
            padx=5,
            pady=5,
            sticky="w",
        )

        tk.Label(
            form,
            text="Use HH:MM",
            fg="gray",
        ).grid(
            row=4,
            column=2,
            padx=5,
            sticky="w",
        )

        # Add window
        tk.Button(
            form,
            text="Add Time Window",
            command=self.add_time_window,
            width=18,
        ).grid(
            row=5,
            column=1,
            pady=8,
            sticky="w",
        )

        # Pending windows
        tk.Label(
            self.root,
            text="Current Schedule",
            font=("Arial", 12, "bold"),
        ).pack(pady=(5, 5))

        schedule_frame = tk.Frame(self.root)
        schedule_frame.pack(
            fill="both",
            padx=30,
        )

        self.schedule_list = tk.Listbox(
            schedule_frame,
            height=8,
            width=80,
        )

        self.schedule_list.pack(
            side="left",
            fill="both",
            expand=True,
        )

        schedule_scrollbar = tk.Scrollbar(
            schedule_frame,
            command=self.schedule_list.yview,
        )

        schedule_scrollbar.pack(
            side="right",
            fill="y",
        )

        self.schedule_list.config(
            yscrollcommand=schedule_scrollbar.set
        )

        tk.Button(
            self.root,
            text="Remove Selected Window",
            command=self.remove_time_window,
        ).pack(pady=5)

        # Main buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Save Policy",
            command=self.save_policy,
            width=16,
        ).grid(
            row=0,
            column=0,
            padx=5,
        )

        tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form,
            width=16,
        ).grid(
            row=0,
            column=1,
            padx=5,
        )

        tk.Button(
            button_frame,
            text="Delete Selected",
            command=self.delete_policy,
            width=16,
        ).grid(
            row=0,
            column=2,
            padx=5,
        )

        # Existing applications
        tk.Label(
            self.root,
            text="Configured Applications",
            font=("Arial", 12, "bold"),
        ).pack(pady=(10, 5))

        list_frame = tk.Frame(self.root)
        list_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 15),
        )

        self.policy_list = tk.Listbox(
            list_frame,
            width=100,
            height=8,
        )

        self.policy_list.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar = tk.Scrollbar(
            list_frame,
            command=self.policy_list.yview,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

        self.policy_list.config(
            yscrollcommand=scrollbar.set
        )

    def browse_executable(self):

        path = filedialog.askopenfilename(
            title="Select Application Executable",
            filetypes=[
                ("Executable files", "*.exe"),
                ("All files", "*.*"),
            ],
        )

        if path:
            self.exe_entry.delete(
                0,
                tk.END,
            )

            self.exe_entry.insert(
                0,
                path,
            )

    def parse_time(self, value):

        try:

            hour, minute = map(
                int,
                value.split(":"),
            )

            return time(
                hour,
                minute,
            )

        except (ValueError, TypeError):

            raise ValueError(
                "Time must use HH:MM format."
            )

    def add_time_window(self):

        day = self.selected_day.get()

        start_text = self.start_entry.get().strip()
        end_text = self.end_entry.get().strip()

        if not start_text or not end_text:

            messagebox.showerror(
                "Error",
                "Enter both start and end times.",
            )

            return

        try:

            start = self.parse_time(
                start_text
            )

            end = self.parse_time(
                end_text
            )

        except ValueError as error:

            messagebox.showerror(
                "Error",
                str(error),
            )

            return

        window = TimeWindow(
            start=start,
            end=end,
        )

        self.pending_windows[day].append(
            window
        )

        self.start_entry.delete(
            0,
            tk.END,
        )

        self.end_entry.delete(
            0,
            tk.END,
        )

        self.refresh_schedule_list()

    def remove_time_window(self):

        selection = self.schedule_list.curselection()

        if not selection:

            messagebox.showerror(
                "Error",
                "Select a time window first.",
            )

            return

        index = selection[0]

        entries = []

        for day in DAYS:

            for window in self.pending_windows[day]:

                entries.append(
                    (day, window)
                )

        day, window = entries[index]

        self.pending_windows[day].remove(
            window
        )

        self.refresh_schedule_list()

    def refresh_schedule_list(self):

        self.schedule_list.delete(
            0,
            tk.END,
        )

        for day in DAYS:

            for window in self.pending_windows[day]:

                start = window.start.strftime(
                    "%H:%M"
                )

                end = window.end.strftime(
                    "%H:%M"
                )

                self.schedule_list.insert(
                    tk.END,
                    f"{day.capitalize():<10} "
                    f"{start} → {end}",
                )

    def save_policy(self):

        name = self.name_entry.get().strip()
        executable = self.exe_entry.get().strip()

        if not name:

            messagebox.showerror(
                "Error",
                "Enter an application name.",
            )

            return

        if not executable:

            messagebox.showerror(
                "Error",
                "Select an executable.",
            )

            return

        has_windows = any(
            self.pending_windows[day]
            for day in DAYS
        )

        if not has_windows:

            messagebox.showerror(
                "Error",
                "Add at least one time window.",
            )

            return

        policy = ApplicationPolicy(
            name=name,
            executable=executable,
            allowed_windows={
                day: windows
                for day, windows
                in self.pending_windows.items()
                if windows
            },
        )

        self.policies.append(
            policy
        )

        self.storage.save(
            self.policies
        )

        self.refresh_list()
        self.clear_form()

        messagebox.showinfo(
            "Saved",
            f"{name} policy saved.",
        )

    def delete_policy(self):

        selection = self.policy_list.curselection()

        if not selection:

            messagebox.showerror(
                "Error",
                "Select a policy first.",
            )

            return

        index = selection[0]

        deleted = self.policies.pop(
            index
        )

        self.storage.save(
            self.policies
        )

        self.refresh_list()

        messagebox.showinfo(
            "Deleted",
            f"{deleted.name} policy deleted.",
        )

    def clear_form(self):

        self.name_entry.delete(
            0,
            tk.END,
        )

        self.exe_entry.delete(
            0,
            tk.END,
        )

        self.start_entry.delete(
            0,
            tk.END,
        )

        self.end_entry.delete(
            0,
            tk.END,
        )

        self.selected_day.set(
            "monday"
        )

        self.pending_windows = {
            day: []
            for day in DAYS
        }

        self.refresh_schedule_list()

    def refresh_list(self):

        self.policy_list.delete(
            0,
            tk.END,
        )

        now = datetime.now()

        for policy in self.policies:

            allowed = is_application_allowed(
                policy,
                now,
            )

            status = (
                "ALLOWED"
                if allowed
                else "BLOCKED"
            )

            self.policy_list.insert(
                tk.END,
                f"{policy.name} | "
                f"{status} | "
                f"{policy.executable}",
            )


def main():

    root = tk.Tk()

    LockboxDashboard(root)

    root.mainloop()


if __name__ == "__main__":
    main()