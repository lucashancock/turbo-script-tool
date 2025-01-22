import tkinter as tk
import argparse as args
from tkinter import ttk, filedialog, messagebox
from oracle_script import oracle_csv_to_json
from oracle_script import login 
from oracle_script import create_oracle_targets
from oracle_script import get_targets
from oracle_script import update_target
from oracle_script import delete_oracle_targets
from oracle_script import delete_target

class TargetManagerApp:
    def __init__(self, root, ip_address, username, password):
        self.root = root
        self.root.title("Target Manager")
        # Store filepath to the CSV file to create targets
        self.filepath = tk.StringVar(value="No file selected")

        # Store of all targets
        self.env_targets = []
        
        # Credentials
        self.token = tk.StringVar()
        self.ipAddress_var = tk.StringVar(value=ip_address)
        self.username_var = tk.StringVar(value=username)
        self.password_var = tk.StringVar(value=password)

        # Stuff needed to edit the selected targets
        self.targetID_var = tk.StringVar()
        self.db_username_var = tk.StringVar()
        self.db_password_var = tk.StringVar()
        self.target_entity_var = tk.StringVar()
        self.port_var = tk.StringVar()
        self.db_ID_var = tk.StringVar()
        self.full_validation_var = tk.BooleanVar()
        
        # Create all the widgets inside the scrollable frame
        self.create_widgets()

    def create_widgets(self):
        # Section 1: Credentials (IP Address, Username, Password)
        self.credentials_frame = ttk.LabelFrame(self.root, text="Credentials", padding="10")
        self.credentials_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(self.credentials_frame, text="IP Address:").grid(row=0, column=0, sticky="w", padx=5)
        self.ip_entry = ttk.Entry(self.credentials_frame, width=30, textvariable=self.ipAddress_var)
        self.ip_entry.grid(row=0, column=1, padx=5, sticky="ew")

        ttk.Label(self.credentials_frame, text="Username:").grid(row=1, column=0, sticky="w", padx=5)
        self.username_entry = ttk.Entry(self.credentials_frame, width=30, textvariable=self.username_var)
        self.username_entry.grid(row=1, column=1, padx=5, sticky="ew")

        ttk.Label(self.credentials_frame, text="Password:").grid(row=2, column=0, sticky="w", padx=5)
        self.password_entry = ttk.Entry(self.credentials_frame, show="*", width=30, textvariable=self.password_var)
        self.password_entry.grid(row=2, column=1, padx=5, sticky="ew")

        # Section 2: File Upload (Create Targets)
        self.upload_frame = ttk.LabelFrame(self.root, text="Create Targets", padding="10")
        self.upload_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Upload button
        self.upload_button = ttk.Button(self.upload_frame, text="Upload Target File", command=self.upload_target_file)
        self.upload_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.create_targets_button = ttk.Button(self.upload_frame, text="Create targets", command=self.create_targets)
        self.create_targets_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Label to display the file path after selecting a file
        self.filepath_label = ttk.Label(self.upload_frame, textvariable=self.filepath, wraplength=300, anchor="w")
        self.filepath_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Add Target Form
        self.form_frame = ttk.LabelFrame(self.root, text="Edit Target", padding="10")
        self.form_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(self.form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.targetUsername_entry = ttk.Entry(self.form_frame, width=30, textvariable=self.db_username_var)
        self.targetUsername_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.targetPassword_entry = ttk.Entry(self.form_frame, width=30, textvariable=self.db_password_var)
        self.targetPassword_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.form_frame, text="Target Scope/Group Name:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.targetEntity_entry = ttk.Entry(self.form_frame, width=30, textvariable=self.target_entity_var)
        self.targetEntity_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.form_frame, text="Port:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.port_entry = ttk.Entry(self.form_frame, width=30, textvariable=self.port_var)
        self.port_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.form_frame, text="Database ID:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.databaseID_entry = ttk.Entry(self.form_frame, width=30, textvariable=self.db_ID_var)
        self.databaseID_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        # Full Validation Checkbox
        self.full_validation_checkbox = ttk.Checkbutton(self.form_frame, text="Full Validation", variable=self.full_validation_var)
        self.full_validation_checkbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.change_button = ttk.Button(self.form_frame, text="Change Selected Targets", command=self.show_selected_json)
        self.change_button.grid(row=7, column=0, padx=5, pady=5, sticky="ew")

        self.delete_selection_button = ttk.Button(self.form_frame, text="Delete Selected Targets", command=self.delete_selected_targets)
        self.delete_selection_button.grid(row=8, column=0, padx=5, pady=5, sticky="ew")

        # Treeview to show targets
        self.target_treeview = ttk.Treeview(self.form_frame, columns=("uuid", "displayName", "username", "port", "databaseId", "status", "lastEditTime"), show="headings", selectmode="extended")
        self.target_treeview.grid(row=1, column=2, rowspan=7, padx=5, pady=5, sticky="news")

        # Define column headings
        self.target_treeview.heading("uuid", text="UUID")
        self.target_treeview.heading("displayName", text="Display Name")
        self.target_treeview.heading("port", text="Port")
        self.target_treeview.heading("databaseId", text="Database ID")
        self.target_treeview.heading("username", text="Username")
        self.target_treeview.heading("lastEditTime", text="Last Edit Time")
        self.target_treeview.heading("status", text="Status")

        # Set column widths
        self.target_treeview.column("uuid", width=30, anchor="center")
        self.target_treeview.column("username", width=100, anchor="center")
        self.target_treeview.column("port", width=50, anchor="center")
        self.target_treeview.column("databaseId", width=80, anchor="center")
        self.target_treeview.column("displayName", width=120, anchor="center")
        self.target_treeview.column("lastEditTime", width=100, anchor="center")
        self.target_treeview.column("status", width=150, anchor="center")

        # Fetch button to populate the treeview
        self.fetch_button = ttk.Button(self.form_frame, text="Fetch All Targets", command=self.fetch_all_targets)
        self.fetch_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Section 4: Delete Targets En Masse
        self.delete_section = ttk.LabelFrame(self.root, text="Delete Targets", padding="10")
        self.delete_section.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.delete_button = ttk.Button(self.delete_section, text="Delete CRITICAL Oracle Targets at once", command=self.delete_critical_targets)
        self.delete_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    
    def upload_target_file(self):
        file_path = filedialog.askopenfilename(title="Select Target File", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        self.filepath.set(file_path) 

    def fetch_all_targets(self):
        if (self.token.get() == ""):
            token = login(self.ipAddress_var.get(), self.username_var.get(), self.password_var.get())
            self.token.set(token)
        targets = get_targets(self.ipAddress_var.get(), self.token.get(), params={"target_type": "Oracle"})

        # Clear the Treeview before populating with new data
        for item in self.target_treeview.get_children():
            self.target_treeview.delete(item)

        # Populate Treeview with fetched data
        for target in targets:
            uuid = target["uuid"]
            displayName = target["displayName"]
            status = target["status"]
            lastEditTime = target["lastEditTime"]
            username = next((field["value"] for field in target["inputFields"] if field["name"] == "username"), None)
            port = next((field["value"] for field in target["inputFields"] if field["name"] == "port"), None)
            databaseId = next((field["value"] for field in target["inputFields"] if field["name"] == "databaseID"), None)
            self.target_treeview.insert("", "end", values=(
                uuid,            
                displayName,      
                username,     
                port,             
                databaseId,
                status,         
                lastEditTime
                ))

    
    def show_selected_json(self):
        selected_items = self.target_treeview.selection()
        selected_targets = []
        
        for item in selected_items:
            target_data = {col: self.target_treeview.item(item, "values")[i] for i, col in enumerate(self.target_treeview["columns"])}
            selected_targets.append(target_data)
        
        if (self.token.get() == ""):
            token = login(self.ipAddress_var.get(), self.username_var.get(), self.password_var.get())
            self.token.set(token)

        for selected_target in selected_targets:
            input_fields = []

            if self.db_username_var.get():
                input_fields.append({"name": "username", "value": self.db_username_var.get()})
            if self.db_password_var.get():
                input_fields.append({"name": "password", "value": self.db_password_var.get()})
            if self.target_entity_var.get():
                input_fields.append({"name": "targetEntities", "value": self.target_entity_var.get()})
            if self.port_var.get():
                input_fields.append({"name": "port", "value": self.port_var.get()})
            if self.db_ID_var.get(): 
                input_fields.append({"name": "databaseID", "value": self.db_ID_var.get()})
            if self.full_validation_var.get():
                input_fields.append({"name": "fullValidation", "value": self.full_validation_var.get()})

            data = {
                "category": "Applications and Databases",
                "type": "Oracle",  
                "uuid": selected_target["uuid"],
                "inputFields": input_fields,
            }
            update_target(self.ipAddress_var.get(), self.token.get(), selected_target["uuid"], data)
        messagebox.showinfo("Targets Updated", "Selected targets have been updated with the set credentials. Check Turbo UI.")
        
    def delete_selected_targets(self):
        if (self.token.get() == ""):
            token = login(self.ipAddress_var.get(), self.username_var.get(), self.password_var.get())
            self.token.set(token)
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected targets?")
        if confirm:
            selected_items = self.target_treeview.selection()
            selected_targets = []
            
            for item in selected_items:
                target_data = {col: self.target_treeview.item(item, "values")[i] for i, col in enumerate(self.target_treeview["columns"])}
                selected_targets.append(target_data)

            for selected_target in selected_targets:
                uuid = selected_target.get("uuid")
                delete_target(self.ipAddress_var.get(), self.token.get(), uuid) 
            messagebox.showinfo("Deleted", "The selected targets have been deleted.")
        else:
            messagebox.showinfo("Deletion Cancelled", "The deletion process was cancelled.")

    def delete_critical_targets(self):
        if self.token.get() == "":
            token = login(self.ipAddress_var.get(), self.username_var.get(), self.password_var.get())
            self.token.set(token)
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete all CRITICAL targets?")
        if confirm:
            delete_oracle_targets(self.ipAddress_var.get(), self.token.get()) 
            messagebox.showinfo("Deleted", "The selected targets have been deleted.")
        else:
            messagebox.showinfo("Deletion Cancelled", "The deletion process was cancelled.")

    def create_targets(self):
        # Add logic to create new targets based on form entries and populate them into the treeview.
        if (self.token.get() == ""):
            token = login(self.ipAddress_var.get(), self.username_var.get(), self.password_var.get())
            self.token.set(token)
        payload = oracle_csv_to_json(self.ipAddress_var.get(), self.token.get(), self.filepath.get(), header=True)
        if payload:
            create_oracle_targets(self.ipAddress_var.get(), self.token.get(), params=payload) 

        messagebox.showinfo("Created", "Targets from CSV have been created, check Turbonomic UI.")

# ---

def parse_args():
    parser = args.ArgumentParser(description="Target Manager CLI")
    parser.add_argument("--ip", type=str, help="IP address of the target, please include https:// at the front.", default="https://url_here")
    parser.add_argument("--username", type=str, help="Username for login", default="")
    parser.add_argument("--password", type=str, help="Password for login", default="")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    root = tk.Tk()
    app = TargetManagerApp(root, args.ip, args.username, args.password)
    root.mainloop()
