import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import os
import sys
from export_xz import XZExporter

class XZApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XZ Exporter")
        self.root.geometry("600x500")
        
        # Style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        
        # Main Frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL Input
        ttk.Label(main_frame, text="Article URL:").pack(anchor=tk.W, pady=(0, 5))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Output Directory
        ttk.Label(main_frame, text="Output Directory:").pack(anchor=tk.W, pady=(0, 5))
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.dir_var = tk.StringVar(value=os.getcwd())
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.browse_btn = ttk.Button(dir_frame, text="Browse...", command=self.browse_dir)
        self.browse_btn.pack(side=tk.RIGHT)
        
        # Export Button
        self.export_btn = ttk.Button(main_frame, text="Export Article", command=self.start_export)
        self.export_btn.pack(fill=tk.X, pady=(10, 20))
        
        # Log Area
        ttk.Label(main_frame, text="Log Output:").pack(anchor=tk.W, pady=(0, 5))
        self.log_area = scrolledtext.ScrolledText(main_frame, height=15, state='disabled', font=("Monaco", 10))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        # Also update status bar with last message
        self.status_var.set(message)

    def start_export(self):
        url = self.url_var.get().strip()
        output_dir = self.dir_var.get().strip()
        
        if not url:
            self.log("Error: Please enter a URL.")
            return
            
        if not output_dir:
            self.log("Error: Please select an output directory.")
            return
            
        self.export_btn.config(state='disabled')
        self.log(f"Starting export for: {url}")
        
        # Run in thread
        thread = threading.Thread(target=self.run_export, args=(url, output_dir))
        thread.daemon = True
        thread.start()

    def run_export(self, url, output_dir):
        try:
            exporter = XZExporter(log_callback=self.log_thread_safe)
            exporter.export(url, output_dir)
            self.log_thread_safe("Export Completed!")
        except Exception as e:
            self.log_thread_safe(f"Critical Error: {e}")
        finally:
            self.root.after(0, lambda: self.export_btn.config(state='normal'))

    def log_thread_safe(self, message):
        self.root.after(0, lambda: self.log(message))

if __name__ == "__main__":
    root = tk.Tk()
    # Set app icon if available, otherwise default
    # root.iconbitmap('icon.ico') 
    app = XZApp(root)
    root.mainloop()
