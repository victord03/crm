import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
import uuid
import fnmatch  # for wildcard matching

CSV_FILE = 'cases.csv'
FIELDNAMES = ["case_id", "timestamp", "phone_number", "email", "main_reaction", "main_response", "call_count", "comments"]

# Global validation function to limit input length to 100 characters.
def max100(new_text):
    return len(new_text) <= 100

class LoggingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VK CRM")
        self.geometry("900x600")
        # Configure grid to center container
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
        # Clear temporary deletion message if switching to main frame.
        if frame_class == MainFrame:
            frame.clear_delete_message()
        frame.tkraise()

class MainFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Main container for padding
        main_container = tk.Frame(self)
        main_container.pack(expand=True, fill="both", padx=10, pady=10)

        # Top row: VK CRM label (left) and search bar with buttons (right)
        top_frame = tk.Frame(main_container)
        top_frame.pack(side="top", fill="x")

        # VK CRM label left-aligned
        title_label = tk.Label(top_frame, text="VK CRM", font=("Helvetica", 16))
        title_label.pack(side="left")

        # On the right: Search bar, Search button, and Browse All button.
        vcmd = self.register(max100)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(top_frame, textvariable=self.search_var, width=30,
                                validate="key", validatecommand=(vcmd, '%P'))
        search_entry.pack(side="right", padx=5)
        # Bind Enter key to trigger search.
        search_entry.bind("<Return>", lambda event: self.perform_search())

        search_button = tk.Button(top_frame, text="Search", command=self.perform_search)
        search_button.pack(side="right", padx=5)

        browse_all_button = tk.Button(top_frame, text="Browse All", command=self.browse_all)
        browse_all_button.pack(side="right", padx=5)

        # Create New button: placed below the top row, left-aligned.
        new_button_frame = tk.Frame(main_container)
        new_button_frame.pack(side="top", anchor="w", pady=10)
        self.create_button = tk.Button(new_button_frame, text="+",
                                       bg="#00008B", fg="white",
                                       font=("Helvetica", 12),
                                       width=4, height=1,
                                       command=self.create_new_case)
        self.create_button.pack()

        # Bottom left: loaded cases count in small italic letters.
        self.data_label = tk.Label(main_container, text="Loaded 0 cases", font=("Helvetica", 8, "italic"))
        self.data_label.pack(side="bottom", anchor="w", pady=(10, 0))
        # Label for deletion message (initially empty)
        self.delete_message_label = tk.Label(main_container, text="", font=("Helvetica", 8, "italic"), fg="red")
        self.delete_message_label.pack(side="bottom", anchor="w")
        self.load_data()

    def load_data(self):
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                cases = list(reader)
            self.data_label.config(text=f"Loaded {len(cases)} cases")
        else:
            self.data_label.config(text="Loaded 0 cases")

    def clear_delete_message(self):
        self.delete_message_label.config(text="")

    def display_delete_message(self, msg):
        self.delete_message_label.config(text=msg)
        # Clear message after 5 seconds.
        self.after(5000, lambda: self.delete_message_label.config(text=""))

    def create_new_case(self):
        new_case_frame = self.controller.frames[NewCaseFrame]
        new_case_frame.load_case_data(None)
        self.controller.show_frame(NewCaseFrame)

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
                    # If query contains a wildcard, use fnmatch for pattern matching.
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

        # Clear the search field after performing search.
        self.search_var.set("")

        if not results:
            messagebox.showinfo("Search", "No results found.")
        elif len(results) == 1:
            new_case_frame = self.controller.frames[NewCaseFrame]
            new_case_frame.load_case_data(results[0])
            self.controller.show_frame(NewCaseFrame)
        else:
            results_frame = self.controller.frames[ResultsFrame]
            results_frame.load_results("Search results", results)
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
            results_frame = self.controller.frames[ResultsFrame]
            results_frame.load_results("All entries", results)
            self.controller.show_frame(ResultsFrame)

class NewCaseFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Container for centering and resizing.
        container = tk.Frame(self)
        container.pack(expand=True, fill="both", padx=10, pady=10)

        # Top frame: left for Case ID and right for Timestamp.
        top_frame = tk.Frame(container)
        top_frame.pack(fill="x", pady=10)

        # Left side: Case ID (read-only and selectable)
        left_top = tk.Frame(top_frame)
        left_top.pack(side="left", padx=5)
        tk.Label(left_top, text="Case ID:").pack(side="left")
        self.case_id_var = tk.StringVar()
        self.case_id_entry = tk.Entry(left_top, textvariable=self.case_id_var,
                                      state="readonly", width=20, relief="flat")
        self.case_id_entry.pack(side="left", padx=5)

        # Right side: Timestamp (label then read-only entry)
        right_top = tk.Frame(top_frame)
        right_top.pack(side="right", padx=5)
        tk.Label(right_top, text="Timestamp:").pack(side="left")
        self.timestamp_var = tk.StringVar()
        self.timestamp_entry = tk.Entry(right_top, textvariable=self.timestamp_var,
                                        state="readonly", width=20, relief="flat")
        self.timestamp_entry.pack(side="left", padx=5)

        # Form frame for remaining fields.
        form_frame = tk.Frame(container)
        form_frame.pack(pady=10, fill="both", expand=True)
        # Allow Comments field to expand.
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(5, weight=1)
        vcmd = self.register(max100)

        # Phone number field.
        tk.Label(form_frame, text="Phone number:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.phone_var = tk.StringVar()
        self.phone_entry = tk.Entry(form_frame, textvariable=self.phone_var, width=40,
                                    validate="key", validatecommand=(vcmd, '%P'))
        self.phone_entry.grid(row=0, column=1, pady=5, padx=5)
        self.phone_entry.bind("<FocusOut>", self.update_call_count)

        # Email address field.
        tk.Label(form_frame, text="Email address:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(form_frame, textvariable=self.email_var, width=40,
                                    validate="key", validatecommand=(vcmd, '%P'))
        self.email_entry.grid(row=1, column=1, pady=5, padx=5)

        # Main reaction dropdown.
        tk.Label(form_frame, text="Main reaction:").grid(row=2, column=0, sticky="e", pady=5, padx=5)
        self.main_reaction_var = tk.StringVar()
        self.main_reaction_combo = ttk.Combobox(form_frame, textvariable=self.main_reaction_var,
                                                state="readonly", width=37)
        self.main_reaction_combo['values'] = ["I am not interested"]
        self.main_reaction_combo.set("Select an option")
        self.main_reaction_combo.grid(row=2, column=1, pady=5, padx=5)

        # Main response dropdown.
        tk.Label(form_frame, text="Main response:").grid(row=3, column=0, sticky="e", pady=5, padx=5)
        self.main_response_var = tk.StringVar()
        self.main_response_combo = ttk.Combobox(form_frame, textvariable=self.main_response_var,
                                                state="readonly", width=37)
        self.main_response_combo['values'] = ["I will call you back"]
        self.main_response_combo.set("Select an option")
        self.main_response_combo.grid(row=3, column=1, pady=5, padx=5)

        # Call count display (starts blank).
        tk.Label(form_frame, text="Call count:").grid(row=4, column=0, sticky="e", pady=5, padx=5)
        self.call_count_var = tk.StringVar(value="")
        self.call_count_label = tk.Label(form_frame, textvariable=self.call_count_var, width=5, relief="sunken")
        self.call_count_label.grid(row=4, column=1, sticky="w", pady=5, padx=5)

        # Comments section: a resizable text field.
        tk.Label(form_frame, text="Comments:").grid(row=5, column=0, sticky="ne", pady=5, padx=5)
        self.comments_text = tk.Text(form_frame, height=5, width=40)
        self.comments_text.grid(row=5, column=1, sticky="nsew", pady=5, padx=5)

        # Button frame for Update, Delete, and Back.
        button_frame = tk.Frame(container)
        button_frame.pack(pady=10)
        self.update_button = tk.Button(button_frame, text="Update", bg="#00008B", fg="white",
                                       font=("Helvetica", 10), width=10, command=self.save_case)
        self.update_button.pack(side="left", padx=5)
        self.delete_button = tk.Button(button_frame, text="Delete", bg="#00008B", fg="white",
                                       font=("Helvetica", 10), width=10, command=self.delete_case)
        self.delete_button.pack(side="left", padx=5)
        self.back_button = tk.Button(button_frame, text="Back", bg="#00008B", fg="white",
                                     font=("Helvetica", 10), width=10,
                                     command=lambda: self.controller.show_frame(MainFrame))
        self.back_button.pack(side="left", padx=5)

        self.current_case = None

    def load_case_data(self, case_data):
        """Load case data into the form; if None, initialize a new case."""
        self.current_case = case_data
        if case_data is None:
            new_case_id = uuid.uuid4().hex[:8]
            self.case_id_var.set(new_case_id)
            self.timestamp_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.phone_var.set("")
            self.email_var.set("")
            self.main_reaction_combo.set("Select an option")
            self.main_response_combo.set("Select an option")
            self.call_count_var.set("")
            self.comments_text.delete("1.0", "end")
        else:
            self.case_id_var.set(case_data.get("case_id", ""))
            self.timestamp_var.set(case_data.get("timestamp", ""))
            self.phone_var.set(case_data.get("phone_number", ""))
            self.email_var.set(case_data.get("email", ""))
            mr = case_data.get("main_reaction", "")
            self.main_reaction_combo.set(mr if mr else "Select an option")
            mresp = case_data.get("main_response", "")
            self.main_response_combo.set(mresp if mresp else "Select an option")
            self.call_count_var.set(case_data.get("call_count", ""))
            self.comments_text.delete("1.0", "end")
            self.comments_text.insert("1.0", case_data.get("comments", ""))

    def update_call_count(self, event=None):
        """When phone field loses focus, update call count (only in-memory here)."""
        phone = self.phone_var.get().strip()
        if not phone:
            self.call_count_var.set("")
            return
        count = ""
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                count = sum(1 for row in reader if row.get("phone_number", "").strip() == phone)
        self.call_count_var.set(str(count) if count else "")

    def save_case(self):
        """Save (or update) the current record and update call counts for matching phone numbers."""
        phone = self.phone_var.get().strip()
        rows = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
        if phone:
            count = sum(1 for row in rows if row.get("phone_number", "").strip() == phone)
            if self.current_case is None:
                count += 1
            for row in rows:
                if row.get("phone_number", "").strip() == phone:
                    row["call_count"] = str(count)
        else:
            count = ""
        data = {
            "case_id": self.case_id_var.get(),
            "timestamp": self.timestamp_var.get(),
            "phone_number": phone,
            "email": self.email_var.get().strip(),
            "main_reaction": self.main_reaction_combo.get() if self.main_reaction_combo.get() != "Select an option" else "",
            "main_response": self.main_response_combo.get() if self.main_response_combo.get() != "Select an option" else "",
            "call_count": str(count),
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
        """Show confirmation pop-up; if confirmed, delete record from CSV and return to main page."""
        case_id = self.case_id_var.get()
        popup = tk.Toplevel(self)
        popup.title("Confirm Deletion")
        popup.grab_set()  # Make modal

        msg = f"You are about to delete CaseID {case_id}. Are you sure you want to continue?"
        tk.Label(popup, text=msg, wraplength=300).pack(padx=20, pady=20)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        def confirm_delete():
            rows = []
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    rows = [row for row in reader if row.get("case_id") != case_id]
            with open(CSV_FILE, "w", newline='', encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(rows)
            popup.destroy()
            main_frame = self.controller.frames[MainFrame]
            main_frame.load_data()
            # Display a generic deletion confirmation message.
            main_frame.display_delete_message("Entry deleted successfully")
            self.controller.show_frame(MainFrame)

        def cancel_delete():
            popup.destroy()

        yes_button = tk.Button(btn_frame, text="Yes", bg="#00008B", fg="white",
                               font=("Helvetica", 10), width=10, command=confirm_delete)
        yes_button.pack(side="left", padx=5)
        no_button = tk.Button(btn_frame, text="No", bg="#00008B", fg="white",
                              font=("Helvetica", 10), width=10, command=cancel_delete)
        no_button.pack(side="left", padx=5)

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
        back_button = tk.Button(container, text="Back", command=lambda: controller.show_frame(MainFrame))
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
                new_case_frame = self.controller.frames[NewCaseFrame]
                new_case_frame.load_case_data(record)
                self.controller.show_frame(NewCaseFrame)

if __name__ == "__main__":
    app = LoggingApp()
    app.mainloop()
