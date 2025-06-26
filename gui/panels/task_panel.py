#!/usr/bin/env python3
"""
Dream.OS Task Panel
==================

GUI panel for task tracking with MMORPG theming.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from core.task_tracker import TaskTracker, Task, TaskPriority, TaskStatus
from core.mmorpg_engine import MMORPGEngine

class TaskPanel(ttk.Frame):
    """Task tracking panel with MMORPG theme."""
    
    def __init__(self, parent, mmorpg_engine: MMORPGEngine):
        super().__init__(parent)
        self.mmorpg_engine = mmorpg_engine
        self.task_tracker = TaskTracker(mmorpg_engine)
        
        self._init_styles()
        self._create_widgets()
        self._layout_widgets()
        self.refresh_tasks()
    
    def _init_styles(self):
        """Initialize custom styles for the panel."""
        style = ttk.Style()
        
        # Task priority styles
        style.configure("Scout.TLabel", foreground="gray")
        style.configure("Adventurer.TLabel", foreground="green")
        style.configure("Hero.TLabel", foreground="blue")
        style.configure("Legendary.TLabel", foreground="purple")
        
        # Task status styles
        style.configure("Available.TLabel", background="lightgray")
        style.configure("Accepted.TLabel", background="lightblue")
        style.configure("Blocked.TLabel", background="pink")
        style.configure("Completed.TLabel", background="lightgreen")
    
    def _create_widgets(self):
        """Create all panel widgets."""
        # Task list frame
        self.task_list_frame = ttk.LabelFrame(self, text="Quest Log")
        self.task_tree = ttk.Treeview(
            self.task_list_frame,
            columns=("Priority", "Status", "Due Date", "XP"),
            show="tree headings"
        )
        
        # Configure treeview
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.heading("Due Date", text="Due By")
        self.task_tree.heading("XP", text="XP Reward")
        
        # Task details frame
        self.details_frame = ttk.LabelFrame(self, text="Quest Details")
        self.title_label = ttk.Label(self.details_frame, text="Title:")
        self.title_entry = ttk.Entry(self.details_frame)
        self.desc_label = ttk.Label(self.details_frame, text="Description:")
        self.desc_text = tk.Text(self.details_frame, height=4, width=40)
        
        # Priority selection
        self.priority_label = ttk.Label(self.details_frame, text="Priority:")
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(
            self.details_frame,
            textvariable=self.priority_var,
            values=[p.value for p in TaskPriority]
        )
        
        # Due date selection
        self.due_label = ttk.Label(self.details_frame, text="Due Date:")
        self.due_entry = ttk.Entry(self.details_frame)
        
        # Tags entry
        self.tags_label = ttk.Label(self.details_frame, text="Tags:")
        self.tags_entry = ttk.Entry(self.details_frame)
        
        # Buttons
        self.button_frame = ttk.Frame(self.details_frame)
        self.add_btn = ttk.Button(
            self.button_frame,
            text="Accept New Quest",
            command=self._add_task
        )
        self.update_btn = ttk.Button(
            self.button_frame,
            text="Update Quest",
            command=self._update_task
        )
        self.complete_btn = ttk.Button(
            self.button_frame,
            text="Complete Quest",
            command=self._complete_task
        )
        
        # Daily summary frame
        self.summary_frame = ttk.LabelFrame(self, text="Daily Quest Summary")
        self.summary_text = tk.Text(self.summary_frame, height=6, width=40, state="disabled")
        
        # Bind events
        self.task_tree.bind("<<TreeviewSelect>>", self._on_task_select)
    
    def _layout_widgets(self):
        """Layout all widgets in the panel."""
        # Task list layout
        self.task_list_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.task_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Details layout
        self.details_frame.pack(side="right", fill="both", padx=5, pady=5)
        
        # Title
        self.title_label.pack(anchor="w", padx=5, pady=(5,0))
        self.title_entry.pack(fill="x", padx=5, pady=(0,5))
        
        # Description
        self.desc_label.pack(anchor="w", padx=5, pady=(5,0))
        self.desc_text.pack(fill="x", padx=5, pady=(0,5))
        
        # Priority
        self.priority_label.pack(anchor="w", padx=5, pady=(5,0))
        self.priority_combo.pack(fill="x", padx=5, pady=(0,5))
        
        # Due date
        self.due_label.pack(anchor="w", padx=5, pady=(5,0))
        self.due_entry.pack(fill="x", padx=5, pady=(0,5))
        
        # Tags
        self.tags_label.pack(anchor="w", padx=5, pady=(5,0))
        self.tags_entry.pack(fill="x", padx=5, pady=(0,5))
        
        # Buttons
        self.button_frame.pack(fill="x", padx=5, pady=5)
        self.add_btn.pack(side="left", padx=5)
        self.update_btn.pack(side="left", padx=5)
        self.complete_btn.pack(side="left", padx=5)
        
        # Summary
        self.summary_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        self.summary_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _add_task(self):
        """Add a new task/quest."""
        try:
            # Get values from inputs
            title = self.title_entry.get().strip()
            description = self.desc_text.get("1.0", "end").strip()
            priority = TaskPriority(self.priority_var.get())
            due_date_str = self.due_entry.get().strip()
            tags = [tag.strip() for tag in self.tags_entry.get().split(",") if tag.strip()]
            
            # Validate inputs
            if not title or not description:
                messagebox.showerror("Error", "Title and description are required!")
                return
            
            # Parse due date
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                    return
            
            # Create task
            task = self.task_tracker.create_task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                tags=tags
            )
            
            # Clear inputs
            self._clear_inputs()
            
            # Refresh display
            self.refresh_tasks()
            
            messagebox.showinfo(
                "Quest Accepted",
                f"New quest accepted: {task.title}\nXP Reward: {task.xp_reward}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create quest: {str(e)}")
    
    def _update_task(self):
        """Update the selected task."""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a quest to update!")
            return
        
        task_id = selection[0]
        task = self.task_tracker.tasks.get(task_id)
        if not task:
            return
        
        try:
            # Update basic properties
            task.title = self.title_entry.get().strip()
            task.description = self.desc_text.get("1.0", "end").strip()
            task.priority = TaskPriority(self.priority_var.get())
            
            # Update due date
            due_date_str = self.due_entry.get().strip()
            if due_date_str:
                task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            
            # Update tags
            task.tags = [tag.strip() for tag in self.tags_entry.get().split(",") if tag.strip()]
            
            # Refresh display
            self.refresh_tasks()
            
            messagebox.showinfo("Success", "Quest updated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update quest: {str(e)}")
    
    def _complete_task(self):
        """Mark the selected task as completed."""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a quest to complete!")
            return
        
        task_id = selection[0]
        if self.task_tracker.update_task_status(task_id, TaskStatus.COMPLETED):
            self.refresh_tasks()
            messagebox.showinfo(
                "Quest Completed",
                "Congratulations! Quest completed successfully!"
            )
    
    def _on_task_select(self, event):
        """Handle task selection in the treeview."""
        selection = self.task_tree.selection()
        if not selection:
            return
        
        task_id = selection[0]
        task = self.task_tracker.tasks.get(task_id)
        if not task:
            return
        
        # Update input fields
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, task.title)
        
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", task.description)
        
        self.priority_var.set(task.priority.value)
        
        self.due_entry.delete(0, "end")
        if task.due_date:
            self.due_entry.insert(0, task.due_date.strftime("%Y-%m-%d"))
        
        self.tags_entry.delete(0, "end")
        if task.tags:
            self.tags_entry.insert(0, ", ".join(task.tags))
    
    def _clear_inputs(self):
        """Clear all input fields."""
        self.title_entry.delete(0, "end")
        self.desc_text.delete("1.0", "end")
        self.priority_var.set("")
        self.due_entry.delete(0, "end")
        self.tags_entry.delete(0, "end")
    
    def refresh_tasks(self):
        """Refresh the task display."""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Add tasks to tree
        for task in self.task_tracker.tasks.values():
            values = (
                task.priority.value,
                task.status.value,
                task.due_date.strftime("%Y-%m-%d") if task.due_date else "",
                task.xp_reward
            )
            
            # Add task
            self.task_tree.insert(
                task.parent_quest_id or "",
                "end",
                task.id,
                text=task.title,
                values=values,
                tags=(task.priority.name.lower(),)
            )
        
        # Update daily summary
        self._update_summary()
    
    def _update_summary(self):
        """Update the daily summary display."""
        summary = self.task_tracker.get_daily_summary()
        
        # Format summary text
        summary_text = f"""Total Quests: {summary['total_tasks']}
Active Quests: {summary['status_breakdown'][TaskStatus.IN_PROGRESS]}
Available Quests: {summary['status_breakdown'][TaskStatus.TODO]}
Completed Quests: {summary['status_breakdown'][TaskStatus.COMPLETED]}
Overdue Quests: {summary['overdue_tasks']}
Available XP: {summary['total_xp_available']}"""
        
        # Update text widget
        self.summary_text.config(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", summary_text)
        self.summary_text.config(state="disabled")