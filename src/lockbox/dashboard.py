import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from .policy import ApplicationPolicy, TimeWindow
from .scheduler import is_application_allowed
from .storage import PolicyStorage


DATA_FILE = Path("data/policies.json")


class LockboxDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Lockbox")
        self.root.geometry("700x500")

        self.storage = PolicyStorage(DATA_FILE)
        self.policies = self.storage.load()

        self.build_ui()
        self.refresh_list()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="Lockbox",
            font=("Arial", 22, "bold"),
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            self.root,
            text="Application Access Control",
            font=("Arial", 11),
        )
        subtitle.pack()

        form = tk.Frame(self.root)
        form.pack(pady=20)

        tk.Label(form, text="Application Name").grid(
            row=0, column=0, padx=5, pady=5
        )

        self.name_entry = tk.Entry(form, width=30)
        self.name_entry.grid(
            row=0, column=1, padx=5, pady=5
        )

        tk.Label(form, text="Executable").grid(
            row=1, column=0, padx=5, pady=5
        )

        self.exe_entry = tk.Entry(form, width=30)
        self.exe_entry.grid(
            row=1, column=1, padx=5, pady=5
        )

        browse_button = tk.Button(
            form,
            text="Browse",
            command=self.browse_executable,
        )
        browse_button.grid(
            row=1, column=2, padx=5
        )

        tk.Label(form, text="Start Time (HH:MM)").grid(
            row=2, column=0, padx=5, pady=5
        )

        self.start_entry = tk.Entry(form, width=10)
        self.start_entry.grid(
            row=2, column=1, sticky="w", padx=5
        )

        tk.Label(form, text="End Time (HH:MM)").grid(
            row=3, column=0, padx=5, pady=5
        )

        self.end_entry = tk.Entry(form, width=10)
        self.end_entry.grid(
            row=3, column=1, sticky="w", padx=5
        )

        tk.Label(
            form,
            text="Days",
        ).grid(
            row=4,
            column=0,
            padx=5,
            pady=5,
        )

        self.day_vars = {}

        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

        days_frame = tk.Frame(form)
        days_frame.grid(
            row=4,
            column=1,
            columnspan=2,
            sticky="w",
        )

        for index, day in enumerate(days):
            var = tk.BooleanVar()
            self.day_vars[day] = var

            checkbox = tk.Checkbutton(
                days_frame,
                text=day[:3].capitalize(),
                variable=var,
            )

            checkbox.grid(
                row=0,
                column=index,
                padx=2,
            )

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Save Policy",
            command=self.save_policy,
            width=15,
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form,
            width=15,
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            button_frame,
            text="Delete Selected",
            command=self.delete_policy,
            width=15,
        ).grid(row=0, column=2, padx=5)

        tk.Label(
            self.root,
            text="Configured Applications",
            font=("Arial", 12, "bold"),
        ).pack(pady=(15, 5))

        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=20)

        self.policy_list = tk.Listbox(
            list_frame,
            width=80,
            height=10,
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
            self.exe_entry.delete(0, tk.END)
            self.exe_entry.insert(0, path)

    def save_policy(self):
        name = self.name_entry.get().strip()
        executable = self.exe_entry.get().strip()
        start_text = self.start_entry.get().strip()
        end_text = self.end_entry.get().strip()

        selected_days = [
            day
            for day, var in self.day_vars.items()
            if var.get()
        ]

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

        if not selected_days:
            messagebox.showerror(
                "Error",
                "Select at least one day.",
            )
            return

        try:
            start_hour, start_minute = map(
                int,
                start_text.split(":"),
            )

            end_hour, end_minute = map(
                int,
                end_text.split(":"),
            )

            from datetime import time

            start = time(start_hour, start_minute)
            end = time(end_hour, end_minute)

        except ValueError:
            messagebox.showerror(
                "Error",
                "Time must use HH:MM format.",
            )
            return

        window = TimeWindow(
            start=start,
            end=end,
        )

        schedule = {
            day: [window]
            for day in selected_days
        }

        policy = ApplicationPolicy(
            name=name,
            executable=executable,
            allowed_windows=schedule,
        )

        self.policies.append(policy)

        self.storage.save(self.policies)

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

        deleted = self.policies.pop(index)

        self.storage.save(self.policies)
        self.refresh_list()

        messagebox.showinfo(
            "Deleted",
            f"{deleted.name} policy deleted.",
        )

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.exe_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)

        for var in self.day_vars.values():
            var.set(False)

    def refresh_list(self):
        self.policy_list.delete(
            0,
            tk.END,
        )

        from datetime import datetime

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
                f"{policy.name} | {status} | "
                f"{policy.executable}",
            )


def main():
    root = tk.Tk()

    LockboxDashboard(root)

    root.mainloop()


if __name__ == "__main__":
    main()