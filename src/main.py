import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
import uuid
import fnmatch  # For wildcard matching

CSV_FILE = "cases.csv"
# Updated CSV schema: two separate count fields.
FIELDNAMES = ["case_id", "timestamp", "phone_number", "email", "main_reaction", "main_response", "email_count", "phone_count", "comments"]

# Global validation: limit input length to 100 characters.
def max100(new_text):
    return len(new_text) <= 100

class LoggingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VK CRM")
        self.geometry("900x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")

        self.frames = {}
        for F in (MainFrame, NewCaseFrame, ResultsFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainFrame)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

class MainFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        main_container = tk.Frame(self)
        main_container.pack(expand=True, fill="both", padx=10, pady=10)

        # Top left: VK CRM label.
        title_label = tk.Label(main_container, text="VK CRM", font=("Helvetica", 16))
        title_label.pack(anchor="w")

        # Below it: Create New Case button.
        create_button = tk.Button(main_container, text="+",
                                  bg="#00008B", fg="white",
                                  font=("Helvetica", 12),
                                  width=4, height=1,
                                  command=lambda: self.controller.frames[NewCaseFrame].load_case_data(None, previous_frame="MainFrame") or self.controller.show_frame(NewCaseFrame))
        create_button.pack(anchor="w", pady=10)

        # Below that: search row.
        search_frame = tk.Frame(main_container)
        search_frame.pack(anchor="w", pady=10)
        vcmd = self.register(max100)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30,
                                validate="key", validatecommand=(vcmd, '%P'))
        search_entry.pack(side="left", padx=5)
        # Bind Enter key to trigger search.
        search_entry.bind("<Return>", lambda event: self.perform_search())
        search_button = tk.Button(search_frame, text="Search", command=self.perform_search)
        search_button.pack(side="left", padx=5)
        browse_all_button = tk.Button(search_frame, text="Browse All", command=self.browse_all)
        browse_all_button.pack(side="left", padx=5)

        # Bottom: loaded cases count.
        self.data_label = tk.Label(main_container, text="Loaded 0 cases", font=("Helvetica", 8, "italic"))
        self.data_label.pack(anchor="w", pady=(10, 0))
        self.load_data()

    def load_data(self):
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                cases = list(reader)
            self.data_label.config(text=f"Loaded {len(cases)} cases")
        else:
            self.data_label.config(text="Loaded 0 cases")

    def perform_search(self):
        query = self.search_var.get().strip().lower()
        if not query:
            messagebox.showinfo("Search", "Please enter a search query.")
            return

        results = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Use wildcard matching if "*" is in the query.
                    if "*" in query:
                        if (fnmatch.fnmatch(row.get("case_id", "").lower(), query) or
                            fnmatch.fnmatch(row.get("phone_number", "").lower(), query) or
                            fnmatch.fnmatch(row.get("email", "").lower(), query)):
                            results.append(row)
                    else:
                        if (query in row.get("case_id", "").lower() or
                            query in row.get("phone_number", "").lower() or
                            query in row.get("email", "").lower()):
                            results.append(row)
        # Clear search box.
        self.search_var.set("")
        if not results:
            messagebox.showinfo("Search", "No results found.")
        elif len(results) == 1:
            self.controller.frames[NewCaseFrame].load_case_data(results[0], previous_frame="MainFrame")
            self.controller.show_frame(NewCaseFrame)
        else:
            self.controller.frames[ResultsFrame].load_results("Search results", results)
            self.controller.show_frame(ResultsFrame)

    def browse_all(self):
        results = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                results = list(reader)
        if not results:
            messagebox.showinfo("Browse All", "No entries found.")
        else:
            self.controller.frames[ResultsFrame].load_results("All entries", results)
            self.controller.show_frame(ResultsFrame)


class NewCaseFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_case = None  # Initialize current_case here.
        self.previous_frame = "MainFrame"  # Default previous frame.

        container = tk.Frame(self)
        container.pack(expand=True, fill="both", padx=10, pady=10)

        # Top frame: Case ID on left, Timestamp on right.
        top_frame = tk.Frame(container)
        top_frame.pack(fill="x", pady=10)

        left_top = tk.Frame(top_frame)
        left_top.pack(side="left", padx=5)
        tk.Label(left_top, text="Case ID:").pack(side="left")
        self.case_id_var = tk.StringVar()
        self.case_id_entry = tk.Entry(left_top, textvariable=self.case_id_var,
                                      state="readonly", width=20, relief="flat")
        self.case_id_entry.pack(side="left", padx=5)

        right_top = tk.Frame(top_frame)
        right_top.pack(side="right", padx=5)
        tk.Label(right_top, text="Timestamp:").pack(side="left")
        self.timestamp_var = tk.StringVar()
        self.timestamp_entry = tk.Entry(right_top, textvariable=self.timestamp_var,
                                        state="readonly", width=20, relief="flat")
        self.timestamp_entry.pack(side="left", padx=5)

        # Form frame.
        form_frame = tk.Frame(container)
        form_frame.pack(pady=10, fill="both", expand=True)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(6, weight=1)
        vcmd = self.register(max100)

        tk.Label(form_frame, text="Phone number:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.phone_var = tk.StringVar()
        self.phone_entry = tk.Entry(form_frame, textvariable=self.phone_var, width=40,
                                    validate="key", validatecommand=(vcmd, '%P'))
        self.phone_entry.grid(row=0, column=1, pady=5, padx=5)
        self.phone_entry.bind("<FocusOut>", self.update_counts)

        tk.Label(form_frame, text="Email address:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(form_frame, textvariable=self.email_var, width=40,
                                    validate="key", validatecommand=(vcmd, '%P'))
        self.email_entry.grid(row=1, column=1, pady=5, padx=5)
        self.email_entry.bind("<FocusOut>", self.update_counts)

        tk.Label(form_frame, text="Main reaction:").grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.main_reaction_var = tk.StringVar()
        self.main_reaction_combo = ttk.Combobox(form_frame, textvariable=self.main_reaction_var,
                                                state="readonly", width=37)
        self.main_reaction_combo['values'] = ["I am not interested"]
        self.main_reaction_combo.set("Select an option")
        self.main_reaction_combo.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Main response:").grid(row=3, column=0, sticky="e", pady=5, padx=5)
        self.main_response_var = tk.StringVar()
        self.main_response_combo = ttk.Combobox(form_frame, textvariable=self.main_response_var,
                                                state="readonly", width=37)
        self.main_response_combo['values'] = ["I will call you back"]
        self.main_response_combo.set("Select an option")
        self.main_response_combo.grid(row=3, column=1, pady=5, padx=5)

        tk.Label(form_frame, text="Cases with this email:").grid(row=4, column=0, sticky="e", pady=5, padx=5)
        self.email_count_var = tk.StringVar(value="")
        self.email_count_label = tk.Label(form_frame, textvariable=self.email_count_var, width=5, relief="sunken")
        self.email_count_label.grid(row=4, column=1, sticky="w", pady=5, padx=5)

        tk.Label(form_frame, text="Cases with this phone number:").grid(row=5, column=0, sticky="e", pady=5, padx=5)
        self.phone_count_var = tk.StringVar(value="")
        self.phone_count_label = tk.Label(form_frame, textvariable=self.phone_count_var, width=5, relief="sunken")
        self.phone_count_label.grid(row=5, column=1, sticky="w", pady=5, padx=5)

        tk.Label(form_frame, text="Comments:").grid(row=6, column=0, sticky="ne", pady=5, padx=5)
        self.comments_text = tk.Text(form_frame, height=5, width=40)
        self.comments_text.grid(row=6, column=1, sticky="nsew", pady=5, padx=5)

        # Button frame: using grid so that Update is left, Delete is middle, and Back is right.
        button_frame = tk.Frame(container)
        button_frame.pack(pady=10, fill="x")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        self.update_button = tk.Button(button_frame, text="Update", bg="#00008B", fg="white",
                                       font=("Helvetica", 10), command=self.save_case)
        self.update_button.grid(row=0, column=0, padx=5)
        self.delete_button = tk.Button(button_frame, text="Delete", bg="#00008B", fg="white",
                                       font=("Helvetica", 10), command=self.delete_case)
        # Show or hide Delete button based on self.current_case.
        if self.current_case is None:
            self.delete_button.grid_forget()
        else:
            self.delete_button.grid(row=0, column=1, padx=5)
        self.back_button = tk.Button(button_frame, text="Back", bg="#00008B", fg="white",
                                     font=("Helvetica", 10), command=self.go_back)
        self.back_button.grid(row=0, column=2, padx=5)

    def load_case_data(self, case_data, previous_frame="MainFrame"):
        """Load case data into the form. 'previous_frame' indicates which frame to return to when Back is clicked."""
        self.previous_frame = previous_frame
        self.current_case = case_data
        if case_data is None:
            new_case_id = uuid.uuid4().hex[:8]
            self.case_id_var.set(new_case_id)
            self.timestamp_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.phone_var.set("")
            self.email_var.set("")
            self.main_reaction_combo.set("Select an option")
            self.main_response_combo.set("Select an option")
            self.email_count_var.set("")
            self.phone_count_var.set("")
            self.comments_text.delete("1.0", "end")
            # Hide Delete button for new case.
            self.delete_button.grid_forget()
        else:
            self.case_id_var.set(case_data.get("case_id", ""))
            self.timestamp_var.set(case_data.get("timestamp", ""))
            self.phone_var.set(case_data.get("phone_number", ""))
            self.email_var.set(case_data.get("email", ""))
            mr = case_data.get("main_reaction", "")
            self.main_reaction_combo.set(mr if mr else "Select an option")
            mresp = case_data.get("main_response", "")
            self.main_response_combo.set(mresp if mresp else "Select an option")
            self.email_count_var.set(case_data.get("email_count", ""))
            self.phone_count_var.set(case_data.get("phone_count", ""))
            self.comments_text.delete("1.0", "end")
            self.comments_text.insert("1.0", case_data.get("comments", ""))
            # Show Delete button when editing an existing case.
            self.delete_button.grid(row=0, column=1, padx=5)

    def update_counts(self, event=None):
        """Update the counters based on the current email and phone values."""
        email = self.email_var.get().strip().lower()
        phone = self.phone_var.get().strip()
        email_count = 0
        phone_count = 0
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if email and row.get("email", "").strip().lower() == email:
                        email_count += 1
                    if phone and row.get("phone_number", "").strip() == phone:
                        phone_count += 1
        # For a new case, include this unsaved record.
        if self.current_case is None:
            if email:
                email_count += 1
            if phone:
                phone_count += 1
        self.email_count_var.set(str(email_count) if email_count else "")
        self.phone_count_var.set(str(phone_count) if phone_count else "")

    def save_case(self):
        """Save (or update) the current record and update counters across matching records."""
        email = self.email_var.get().strip().lower()
        phone = self.phone_var.get().strip()
        rows = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
        email_count = sum(1 for row in rows if row.get("email", "").strip().lower() == email)
        phone_count = sum(1 for row in rows if row.get("phone_number", "").strip() == phone)
        if self.current_case is None:
            if email:
                email_count += 1
            if phone:
                phone_count += 1
        for row in rows:
            if email and row.get("email", "").strip().lower() == email:
                row["email_count"] = str(email_count)
            if phone and row.get("phone_number", "").strip() == phone:
                row["phone_count"] = str(phone_count)
        data = {
            "case_id": self.case_id_var.get(),
            "timestamp": self.timestamp_var.get(),
            "phone_number": phone,
            "email": self.email_var.get().strip(),
            "main_reaction": self.main_reaction_combo.get() if self.main_reaction_combo.get() != "Select an option" else "",
            "main_response": self.main_response_combo.get() if self.main_response_combo.get() != "Select an option" else "",
            "email_count": str(email_count),
            "phone_count": str(phone_count),
            "comments": self.comments_text.get("1.0", "end").strip()
        }
        updated = False
        for i, row in enumerate(rows):
            if row.get("case_id") == data["case_id"]:
                rows[i] = data
                updated = True
                break
        if not updated:
            rows.append(data)
        with open(CSV_FILE, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        self.controller.frames[MainFrame].load_data()
        self.controller.show_frame(MainFrame)

    def delete_case(self):
        """Immediately delete the current record and then return to the previous interface."""
        case_id = self.case_id_var.get()
        rows = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = [row for row in reader if row.get("case_id") != case_id]
        with open(CSV_FILE, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        self.go_back()

    def go_back(self):
        """Return to the previous interface (ResultsFrame if coming from search, otherwise MainFrame)."""
        if self.previous_frame == "ResultsFrame":
            self.controller.show_frame(ResultsFrame)
        else:
            self.controller.show_frame(MainFrame)

class ResultsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        container = tk.Frame(self)
        container.pack(expand=True, fill="both", padx=10, pady=10)
        self.results_label = tk.Label(container, text="", font=("Helvetica", 14))
        self.results_label.pack(anchor="w", pady=5)
        columns = ("case_id", "email", "phone_number", "timestamp")
        self.tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=150)
        self.tree.pack(expand=True, fill="both")
        self.tree.bind("<Double-1>", self.on_row_double_click)
        back_button = tk.Button(container, text="Back", command=lambda: self.controller.show_frame(MainFrame))
        back_button.pack(pady=5)

    def load_results(self, header, results):
        self.results_label.config(text=header)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in results:
            self.tree.insert("", "end", values=(row.get("case_id", ""),
                                                row.get("email", ""),
                                                row.get("phone_number", ""),
                                                row.get("timestamp", "")))

    def on_row_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            values = item['values']
            case_id = values[0]
            record = None
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if row.get("case_id") == case_id:
                            record = row
                            break
            if record:
                self.controller.frames[NewCaseFrame].load_case_data(record, previous_frame="ResultsFrame")
                self.controller.show_frame(NewCaseFrame)

if __name__ == "__main__":
    app = LoggingApp()
    app.mainloop()
