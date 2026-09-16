#!/usr/bin/env python3
"""
Pokemon Status Tracker
A simple GUI to track completion status of Pokemon 3D prints
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import queue
import subprocess
import threading
from pathlib import Path

from pokemon_organizer.config import DESIGNS_DIR, POKEBALLS_FOLDER
from pokemon_organizer.events import Event
from pokemon_organizer.runner import run_all

class PokemonStatusTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon Status Tracker")
        self.root.geometry("800x600")

        # Set working directory to script location
        self.base_dir = Path(__file__).parent
        os.chdir(self.base_dir)

        self.designs_dir = self.base_dir / DESIGNS_DIR
        self.status_file = self.base_dir / "pokemon-status.json"
        self.status_data = {}
        self.checkboxes = {}

        # Load status
        self.load_status()

        # Create GUI
        self.create_widgets()

        # Scan folders and populate
        self.scan_and_populate()

    def load_status(self):
        """Load status from JSON file"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    self.status_data = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load status file:\n{e}")
                self.status_data = {}
        else:
            self.status_data = {}

    def save_status(self):
        """Save status to JSON file"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save status file:\n{e}")

    def create_widgets(self):
        """Create GUI widgets"""
        # Header
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            header_frame,
            text="Pokemon 3D Print Status Tracker",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        # Stats label
        self.stats_label = ttk.Label(header_frame, text="", font=('Arial', 10))
        self.stats_label.pack(side=tk.RIGHT)

        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=10)

        # Main content area with scrollbar
        content_frame = ttk.Frame(self.root, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas and scrollbar
        self.canvas = tk.Canvas(content_frame, bg='white')
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Footer
        footer_frame = ttk.Frame(self.root, padding="10")
        footer_frame.pack(fill=tk.X)

        ttk.Button(
            footer_frame,
            text="Refresh",
            command=self.refresh
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            footer_frame,
            text="📂 Organize Files",
            command=self.organize_files
        ).pack(side=tk.LEFT, padx=5)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def scan_and_populate(self):
        """Scan directories and populate the list"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.checkboxes.clear()

        # Find all pokemon folders (format: #### - Name)
        pokemon_folders = []
        if self.designs_dir.is_dir():
            for item in sorted(self.designs_dir.iterdir()):
                if item.is_dir() and len(item.name) >= 4 and item.name[:4].isdigit():
                    pokemon_folders.append(item)

        if not pokemon_folders:
            ttk.Label(
                self.scrollable_frame,
                text=f"No Pokemon folders found in {DESIGNS_DIR}/",
                font=('Arial', 12)
            ).pack(pady=20)
            return

        # Create entries for each Pokemon
        row = 0
        total_items = 0
        done_items = 0

        for pokemon_folder in pokemon_folders:
            # Main Pokemon entry
            pokemon_name = pokemon_folder.name
            pokemon_path = pokemon_name

            # Frame for this Pokemon
            pokemon_frame = ttk.Frame(self.scrollable_frame)
            pokemon_frame.grid(row=row, column=0, sticky='ew', padx=5, pady=2)

            # Checkbox variable
            var = tk.BooleanVar(value=self.status_data.get(pokemon_path, False))

            # Checkbox
            cb = ttk.Checkbutton(
                pokemon_frame,
                text=pokemon_name,
                variable=var,
                command=lambda p=pokemon_path, v=var: self.toggle_status(p, v)
            )
            cb.pack(side=tk.LEFT, padx=(0, 10))

            # Explorer button
            ttk.Button(
                pokemon_frame,
                text="📁",
                width=3,
                command=lambda p=pokemon_folder: self.open_in_explorer(p)
            ).pack(side=tk.RIGHT)

            self.checkboxes[pokemon_path] = var
            total_items += 1
            if var.get():
                done_items += 1

            row += 1

            # Check for variants (subdirectories)
            variants = []
            for item in sorted(pokemon_folder.iterdir()):
                if item.is_dir():
                    variants.append(item)

            # Add variants
            for variant_folder in variants:
                variant_name = variant_folder.name
                variant_path = f"{pokemon_name}/{variant_name}"

                # Frame for variant
                variant_frame = ttk.Frame(self.scrollable_frame)
                variant_frame.grid(row=row, column=0, sticky='ew', padx=5, pady=2)

                # Checkbox variable
                var_variant = tk.BooleanVar(value=self.status_data.get(variant_path, False))

                # Checkbox (indented)
                cb_variant = ttk.Checkbutton(
                    variant_frame,
                    text=f"    ↳ {variant_name}",
                    variable=var_variant,
                    command=lambda p=variant_path, v=var_variant: self.toggle_status(p, v)
                )
                cb_variant.pack(side=tk.LEFT, padx=(20, 10))

                # Explorer button
                ttk.Button(
                    variant_frame,
                    text="📁",
                    width=3,
                    command=lambda p=variant_folder: self.open_in_explorer(p)
                ).pack(side=tk.RIGHT)

                self.checkboxes[variant_path] = var_variant
                total_items += 1
                if var_variant.get():
                    done_items += 1

                row += 1

        # Add Pokeballs at the end (each ball type as individual entry)
        pokeballs_dir = self.designs_dir / POKEBALLS_FOLDER
        if pokeballs_dir.exists() and pokeballs_dir.is_dir():
            # Add separator
            separator_frame = ttk.Frame(self.scrollable_frame)
            separator_frame.grid(row=row, column=0, sticky='ew', padx=5, pady=10)
            ttk.Separator(separator_frame, orient='horizontal').pack(fill=tk.X)
            row += 1

            # Scan for ball types (subdirectories in Pokeballs)
            ball_folders = []
            for item in sorted(pokeballs_dir.iterdir()):
                if item.is_dir():
                    ball_folders.append(item)

            # Add each ball type as individual entry
            for ball_folder in ball_folders:
                ball_name = ball_folder.name
                ball_path = f"{POKEBALLS_FOLDER}/{ball_name}"

                # Frame for this ball
                ball_frame = ttk.Frame(self.scrollable_frame)
                ball_frame.grid(row=row, column=0, sticky='ew', padx=5, pady=2)

                # Checkbox variable
                var_ball = tk.BooleanVar(value=self.status_data.get(ball_path, False))

                # Checkbox
                cb_ball = ttk.Checkbutton(
                    ball_frame,
                    text=f"🎱 {ball_name}",
                    variable=var_ball,
                    command=lambda p=ball_path, v=var_ball: self.toggle_status(p, v)
                )
                cb_ball.pack(side=tk.LEFT, padx=(0, 10))

                # Explorer button
                ttk.Button(
                    ball_frame,
                    text="📁",
                    width=3,
                    command=lambda p=ball_folder: self.open_in_explorer(p)
                ).pack(side=tk.RIGHT)

                self.checkboxes[ball_path] = var_ball
                total_items += 1
                if var_ball.get():
                    done_items += 1

                row += 1

        # Update stats
        self.update_stats(done_items, total_items)

    def toggle_status(self, path, var):
        """Toggle status for a Pokemon/Variant"""
        self.status_data[path] = var.get()
        self.save_status()
        self.update_stats_from_checkboxes()

    def update_stats_from_checkboxes(self):
        """Update statistics from current checkbox states"""
        total = len(self.checkboxes)
        done = sum(1 for var in self.checkboxes.values() if var.get())
        self.update_stats(done, total)

    def update_stats(self, done, total):
        """Update statistics label"""
        percentage = (done / total * 100) if total > 0 else 0
        self.stats_label.config(text=f"Progress: {done}/{total} ({percentage:.1f}%)")

    def open_in_explorer(self, path):
        """Open folder in Windows Explorer"""
        try:
            subprocess.Popen(f'explorer "{path.resolve()}"')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Explorer:\n{e}")

    def refresh(self):
        """Refresh the list"""
        self.load_status()
        self.scan_and_populate()

    def organize_files(self):
        """Extract ZIPs (if any) and organize files"""
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Organizing Files...")
        progress_window.geometry("600x400")
        progress_window.transient(self.root)
        progress_window.grab_set()

        text_frame = ttk.Frame(progress_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        output_text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 9))
        output_scrollbar = ttk.Scrollbar(text_frame, command=output_text.yview)
        output_text.configure(yscrollcommand=output_scrollbar.set)

        output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = ttk.Frame(progress_window, padding="10")
        button_frame.pack(fill=tk.X, pady=10)

        close_button = ttk.Button(
            button_frame,
            text="Close",
            command=progress_window.destroy,
            state='disabled'
        )
        close_button.pack(side=tk.RIGHT, pady=5)

        output_text.tag_config('error', foreground='red')
        output_text.tag_config('warning', foreground='#b36b00')
        output_text.tag_config('summary', foreground='green', font=('Consolas', 9, 'bold'))

        output_text.insert(tk.END, "Starting organization...\n\n")

        events = queue.Queue()

        def worker():
            try:
                run_all(self.base_dir, emit=events.put)
            except Exception as error:
                events.put(Event('error', f"❌ Error while organizing:\n{error}"))
            finally:
                events.put(None)

        def drain_events():
            finished = False

            while True:
                try:
                    event = events.get_nowait()
                except queue.Empty:
                    break

                if event is None:
                    finished = True
                    break

                if event.verbose:
                    continue

                tag = event.kind if event.kind in ('error', 'warning', 'summary') else ''
                output_text.insert(tk.END, f"{event.message}\n", tag)

            output_text.see(tk.END)

            if finished:
                close_button.config(state='normal')
                self.refresh()
            else:
                self.root.after(50, drain_events)

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(50, drain_events)

def main():
    root = tk.Tk()
    app = PokemonStatusTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
