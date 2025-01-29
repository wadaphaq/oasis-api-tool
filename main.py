import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import datetime
import os
import time
import threading

# ---------------------------------------
# EXAMPLE node list (replace with real!)
# ---------------------------------------
ALL_NODES = [
    "PINEFLT_2_B1",
    "AVA_AVA.BPAT-APND",
    "0096WD_7_N001",
    # ... add more nodes as needed
]

class CAISODownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("CAISO LMP Downloader")

        # ----------------------------
        # Variables / State
        # ----------------------------
        self.start_date_var = tk.StringVar(value="2020-01-01")
        self.end_date_var = tk.StringVar(value="2020-12-31")
        
        # We'll use a Combobox for Node selection.
        # We'll provide a few single nodes plus an "ALL_NODES" choice.
        self.node_options = ALL_NODES + ["ALL_NODES"]  # user picks from these
        self.node_var = tk.StringVar(value="TH_N001")  # default node

        self.market_var = tk.StringVar(value="DAM")  # Could also be "RTM", "RUC", ...
        self.download_path_var = tk.StringVar(value=os.path.expanduser("~"))

        # For controlling the thread
        self.downloading = False
        self.abort_flag = False
        
        # ----------------------------
        # Create GUI components
        # ----------------------------
        self.create_widgets()

    def create_widgets(self):
        """
        Build and layout all the GUI widgets (labels, entries, buttons, etc.).
        """
        # --- Row 0: Start Date ---
        lbl_start_date = ttk.Label(self, text="Start Date (YYYY-MM-DD):")
        lbl_start_date.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        ent_start_date = ttk.Entry(self, textvariable=self.start_date_var, width=12)
        ent_start_date.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # --- Row 1: End Date ---
        lbl_end_date = ttk.Label(self, text="End Date (YYYY-MM-DD):")
        lbl_end_date.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        
        ent_end_date = ttk.Entry(self, textvariable=self.end_date_var, width=12)
        ent_end_date.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # --- Row 2: Node selection ---
        lbl_node = ttk.Label(self, text="Node:")
        lbl_node.grid(row=2, column=0, padx=5, pady=5, sticky="e")

        cmb_node = ttk.Combobox(self, textvariable=self.node_var, values=self.node_options, state="readonly")
        cmb_node.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        cmb_node.current(0)  # default to the first entry in node_options

        # --- Row 3: Market selection ---
        lbl_market = ttk.Label(self, text="Market:")
        lbl_market.grid(row=3, column=0, padx=5, pady=5, sticky="e")

        market_options = ["DAM", "RUC", "RTM"]
        cmb_market = ttk.Combobox(self, textvariable=self.market_var, values=market_options, state="readonly")
        cmb_market.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        cmb_market.current(0)  # default to "DAM"

        # --- Row 4: Download Path ---
        lbl_download_path = ttk.Label(self, text="Download Folder:")
        lbl_download_path.grid(row=4, column=0, padx=5, pady=5, sticky="e")

        frm_path = ttk.Frame(self)
        frm_path.grid(row=4, column=1, sticky="w")

        ent_path = ttk.Entry(frm_path, textvariable=self.download_path_var, width=25)
        ent_path.pack(side="left", fill="x", expand=True)

        btn_browse = ttk.Button(frm_path, text="Browse...", command=self.select_folder)
        btn_browse.pack(side="left", padx=5)

        # --- Row 5: Progress bar ---
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", length=250,
            mode="determinate", maximum=100, variable=self.progress_var
        )
        self.progress_bar.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # --- Row 6: Buttons ---
        frm_buttons = ttk.Frame(self)
        frm_buttons.grid(row=6, column=0, columnspan=2, pady=10)
        
        btn_download = ttk.Button(frm_buttons, text="Download", command=self.on_download_click)
        btn_download.pack(side="left", padx=5)

        btn_abort = ttk.Button(frm_buttons, text="Abort", command=self.on_abort_click)
        btn_abort.pack(side="left", padx=5)

    def select_folder(self):
        """Open a folder browser dialog so the user can pick a download folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.download_path_var.set(folder_selected)

    def on_download_click(self):
        """Called when the user clicks the 'Download' button."""
        if self.downloading:
            messagebox.showinfo("Download in progress", "A download is already in progress.")
            return

        # Validate user inputs
        start_date_str = self.start_date_var.get().strip()
        end_date_str = self.end_date_var.get().strip()
        node_choice = self.node_var.get().strip()  # Could be a single node or "ALL_NODES"
        market = self.market_var.get().strip()
        output_dir = self.download_path_var.get().strip()

        # Basic input checks
        if not (start_date_str and end_date_str and node_choice and market and output_dir):
            messagebox.showwarning("Missing input", "Please fill in all fields.")
            return

        # Convert to date objects
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Invalid date", "Please enter dates in YYYY-MM-DD format.")
            return

        if start_date > end_date:
            messagebox.showerror("Invalid date range", "Start date cannot be after end date.")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError:
                messagebox.showerror("Error", "Could not create or access the specified download folder.")
                return

        # Determine the actual list of nodes to download
        if node_choice == "ALL_NODES":
            nodes_to_download = ALL_NODES
        else:
            # Just a single node
            nodes_to_download = [node_choice]

        # Start the download in a new thread
        self.abort_flag = False
        self.downloading = True
        self.progress_var.set(0)

        download_thread = threading.Thread(
            target=self.worker_download, 
            args=(start_date, end_date, nodes_to_download, market, output_dir),
            daemon=True
        )
        download_thread.start()

    def on_abort_click(self):
        """Set a flag to abort the current download."""
        if self.downloading:
            self.abort_flag = True
        else:
            messagebox.showinfo("No download", "No download is currently in progress.")

    def worker_download(self, start_date, end_date, nodes_to_download, market_run_id, out_dir):
        """
        Worker thread function: handles all node downloads + date slicing.
        Updates the GUI progress bar as it goes.
        """
        base_url = "http://oasis.caiso.com/oasisapi/SingleZip"
        result_format = 6  # CSV in zip

        # Build a list of (node, window_start, window_end) tasks
        tasks = []
        for node in nodes_to_download:
            # Create 30-day windows for each node
            tmp_date = start_date
            while tmp_date < end_date:
                window_start = tmp_date
                window_end = tmp_date + datetime.timedelta(days=30)
                if window_end > end_date:
                    window_end = end_date
                tasks.append((node, window_start, window_end))
                tmp_date = window_end

        total_tasks = len(tasks)
        completed_tasks = 0

        for (node, window_start, window_end) in tasks:
            if self.abort_flag:
                break  # user requested an abort

            # Format the time for OASIS (YYYYMMDDT00:00-0000)
            oasis_start_str = window_start.strftime("%Y%m%dT00:00-0000")
            oasis_end_str = window_end.strftime("%Y%m%dT00:00-0000")

            params = {
                "queryname": "PRC_LMP",
                "startdatetime": oasis_start_str,
                "enddatetime": oasis_end_str,
                "version": 1,
                "market_run_id": market_run_id,
                "node": node,
                "resultformat": result_format
            }

            try:
                response = requests.get(base_url, params=params, timeout=60)
                if response.status_code == 200:
                    # Save the ZIP file
                    filename = (
                        f"CAISO_LMP_{market_run_id}_{node}_"
                        f"{window_start.strftime('%Y%m%d')}_"
                        f"{window_end.strftime('%Y%m%d')}.zip"
                    )
                    full_path = os.path.join(out_dir, filename)
                    with open(full_path, 'wb') as f:
                        f.write(response.content)
                else:
                    print(f"Failed request: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Exception during download for node {node}: {e}")

            completed_tasks += 1
            progress_percent = (completed_tasks / total_tasks) * 100
            self.update_progress(progress_percent)

            time.sleep(10)  # Polite delay between requests

        if self.abort_flag:
            messagebox.showwarning("Aborted", "Download was aborted by user.")
        else:
            messagebox.showinfo("Complete", "Download complete.")

        # Reset state
        self.update_progress(0)
        self.downloading = False
        self.abort_flag = False

    def update_progress(self, percent):
        """
        Safely update the progress bar from the worker thread by using `after` callback.
        """
        def _update():
            self.progress_var.set(percent)
        self.after(0, _update)

if __name__ == "__main__":
    app = CAISODownloaderApp()
    app.mainloop()
