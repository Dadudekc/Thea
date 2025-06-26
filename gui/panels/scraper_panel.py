#!/usr/bin/env python3
"""
Scraper Panel for Dream.OS GUI
==============================

Concise GUI panel that integrates with the ScraperOrchestrator.
Stays within 300-350 LOC requirement.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
from typing import Optional, List
import logging
import json
from pathlib import Path

from scrapers.chatgpt_scraper import ChatGPTScraper
from core.scraper_orchestrator import ScraperOrchestrator, ConversationData, ScrapingResult

logger = logging.getLogger(__name__)

class ScraperPanel(ttk.Frame):
    """GUI panel for ChatGPT scraping operations."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize state
        self.orchestrator: Optional[ScraperOrchestrator] = None
        self.conversations: List[ConversationData] = []
        self.thread_queue = queue.Queue()
        self.worker_thread: Optional[threading.Thread] = None
        
        # Setup UI
        self._setup_ui()
        self._setup_threading()
        
        logger.info("ScraperPanel initialized")
    
    def _setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        ttk.Label(main_frame, text="ChatGPT Scraper", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Control Panel
        self._create_control_panel(main_frame)
        
        # Status Panel
        self._create_status_panel(main_frame)
        
        # Results Panel
        self._create_results_panel(main_frame)
        
        # AI Interaction Panel
        self._create_interaction_panel(main_frame)
    
    def _create_control_panel(self, parent):
        """Create the control panel."""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Login Section
        login_frame = ttk.Frame(control_frame)
        login_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(login_frame, text="Login:").pack(anchor=tk.W)
        
        # Credentials
        cred_frame = ttk.Frame(login_frame)
        cred_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cred_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.username_var = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(cred_frame, text="Password:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.password_var = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.password_var, show="*", width=30).grid(row=0, column=3, sticky=tk.W)
        
        # Cookie file
        cookie_frame = ttk.Frame(login_frame)
        cookie_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cookie_frame, text="Cookie File:").pack(side=tk.LEFT, padx=(0, 5))
        self.cookie_file_var = tk.StringVar(value="chatgpt_cookies.pkl")
        ttk.Entry(cookie_frame, textvariable=self.cookie_file_var, width=40).pack(side=tk.LEFT)
        
        # Login button
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.login_button = ttk.Button(button_frame, text="Login with Credentials", command=self._login)
        self.login_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cookie_login_button = ttk.Button(button_frame, text="Login with Cookies", command=self._login_with_cookies)
        self.cookie_login_button.pack(side=tk.LEFT)
        
        # Scraping Section
        scraping_frame = ttk.Frame(control_frame)
        scraping_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(scraping_frame, text="Scraping:").pack(anchor=tk.W)
        
        # Options frame
        options_frame = ttk.Frame(scraping_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        # Max conversations
        ttk.Label(options_frame, text="Max Conversations:").pack(side=tk.LEFT)
        self.max_conv_var = tk.StringVar(value="1500")
        ttk.Entry(options_frame, textvariable=self.max_conv_var, width=10).pack(side=tk.LEFT, padx=(5, 10))
        
        # Output file
        ttk.Label(options_frame, text="Output File:").pack(side=tk.LEFT, padx=(10, 5))
        self.output_file_var = tk.StringVar(value="chatgpt_conversations.json")
        ttk.Entry(options_frame, textvariable=self.output_file_var, width=30).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(scraping_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.extract_button = ttk.Button(button_frame, text="Extract Conversations", command=self._extract_conversations)
        self.extract_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.content_button = ttk.Button(button_frame, text="Extract Content", command=self._extract_content)
        self.content_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_button = ttk.Button(button_frame, text="Save Results", command=self._save_results)
        self.save_button.pack(side=tk.LEFT)
    
    def _create_status_panel(self, parent):
        """Create the status panel."""
        status_frame = ttk.LabelFrame(parent, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_details = scrolledtext.ScrolledText(status_frame, height=4, width=80)
        self.status_details.pack(fill=tk.X, pady=(5, 0))
    
    def _create_results_panel(self, parent):
        """Create the results panel."""
        results_frame = ttk.LabelFrame(parent, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Title", "Messages", "Model", "Status", "URL")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_interaction_panel(self, parent):
        """Create the AI interaction panel."""
        interaction_frame = ttk.LabelFrame(parent, text="AI Interaction", padding=10)
        interaction_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Conversation viewer
        viewer_frame = ttk.Frame(interaction_frame)
        viewer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split view
        paned = ttk.PanedWindow(viewer_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - conversation list
        left_frame = ttk.Frame(paned)
        ttk.Label(left_frame, text="Conversations").pack(anchor=tk.W)
        
        self.conv_listbox = tk.Listbox(left_frame, height=10)
        self.conv_listbox.pack(fill=tk.BOTH, expand=True)
        self.conv_listbox.bind('<<ListboxSelect>>', self._on_conversation_selected)
        
        # Add scrollbar
        list_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.conv_listbox.yview)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.conv_listbox.configure(yscrollcommand=list_scroll.set)
        
        paned.add(left_frame)
        
        # Right side - conversation content and interaction
        right_frame = ttk.Frame(paned)
        
        # Conversation content
        content_frame = ttk.Frame(right_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(content_frame, text="Conversation Content").pack(anchor=tk.W)
        
        self.content_text = scrolledtext.ScrolledText(content_frame, height=10, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Interaction area
        interaction_frame = ttk.Frame(right_frame)
        interaction_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Prompt input
        prompt_frame = ttk.Frame(interaction_frame)
        prompt_frame.pack(fill=tk.X)
        
        ttk.Label(prompt_frame, text="Prompt:").pack(anchor=tk.W)
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=3, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(interaction_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.send_button = ttk.Button(button_frame, text="Send Prompt", command=self._send_prompt)
        self.send_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.regenerate_button = ttk.Button(button_frame, text="Regenerate Response", command=self._regenerate_response)
        self.regenerate_button.pack(side=tk.LEFT)
        
        paned.add(right_frame)
        
        # Set initial pane sizes
        paned.paneconfig(left_frame, minsize=200)
        paned.paneconfig(right_frame, minsize=400)
    
    def _on_conversation_selected(self, event):
        """Handle conversation selection."""
        if not self.conv_listbox.curselection():
            return
        
        idx = self.conv_listbox.curselection()[0]
        conv = self.conversations[idx]
        
        # Update content display
        self.content_text.delete(1.0, tk.END)
        if conv.get('content'):
            self.content_text.insert(tk.END, conv['content'])
        
        # Enable interaction buttons
        self.send_button.config(state="normal")
        self.regenerate_button.config(state="normal")
    
    def _send_prompt(self):
        """Send a prompt to the current conversation."""
        if not self.conv_listbox.curselection():
            messagebox.showerror("Error", "Please select a conversation first")
            return
        
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt")
            return
        
        idx = self.conv_listbox.curselection()[0]
        conv = self.conversations[idx]
        
        self._update_status("Sending prompt...", f"Sending prompt to conversation: {conv['title']}")
        self._disable_controls()
        
        self.worker_thread = threading.Thread(target=self._send_prompt_worker, args=(conv, prompt))
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def _send_prompt_worker(self, conversation: dict, prompt: str):
        """Worker thread for sending prompts."""
        try:
            scraper = ChatGPTScraper(
                headless=False,
                use_undetected=True,
                cookie_file=self.cookie_file_var.get().strip()
            )
            
            with scraper:
                # Navigate to conversation
                if not scraper.enter_conversation(conversation['url']):
                    raise Exception("Failed to enter conversation")
                
                # Send prompt and wait for response
                if not scraper.send_prompt(prompt, wait_for_response=True):
                    raise Exception("Failed to send prompt")
                
                # Get updated conversation content
                content = scraper.get_conversation_content()
                conversation.update(content)
                
                self.thread_queue.put(("send_prompt", ScrapingResult(
                    success=True,
                    data=conversation,
                    metadata={'prompt': prompt}
                )))
                
        except Exception as e:
            logger.error(f"Send prompt worker error: {e}")
            self.thread_queue.put(("send_prompt", ScrapingResult(success=False, error=str(e))))
    
    def _regenerate_response(self):
        """Regenerate the last response in the current conversation."""
        if not self.conv_listbox.curselection():
            messagebox.showerror("Error", "Please select a conversation first")
            return
        
        idx = self.conv_listbox.curselection()[0]
        conv = self.conversations[idx]
        
        self._update_status("Regenerating response...", f"Regenerating response in conversation: {conv['title']}")
        self._disable_controls()
        
        self.worker_thread = threading.Thread(target=self._regenerate_response_worker, args=(conv,))
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def _regenerate_response_worker(self, conversation: dict):
        """Worker thread for regenerating responses."""
        try:
            scraper = ChatGPTScraper(
                headless=False,
                use_undetected=True,
                cookie_file=self.cookie_file_var.get().strip()
            )
            
            with scraper:
                # Navigate to conversation
                if not scraper.enter_conversation(conversation['url']):
                    raise Exception("Failed to enter conversation")
                
                # Click regenerate button
                if not scraper.regenerate_response():
                    raise Exception("Failed to regenerate response")
                
                # Get updated conversation content
                content = scraper.get_conversation_content()
                conversation.update(content)
                
                self.thread_queue.put(("regenerate_response", ScrapingResult(
                    success=True,
                    data=conversation
                )))
                
        except Exception as e:
            logger.error(f"Regenerate response worker error: {e}")
            self.thread_queue.put(("regenerate_response", ScrapingResult(success=False, error=str(e))))
    
    def _handle_send_prompt_result(self, result: ScrapingResult):
        """Handle send prompt result."""
        if result.success:
            conversation = result.data
            self._update_status(
                "Prompt sent",
                f"Successfully sent prompt to conversation: {conversation['title']}"
            )
            self._update_conversation_content(conversation)
            messagebox.showinfo("Success", "Prompt sent successfully!")
        else:
            self._update_status("Failed to send prompt", result.error)
            messagebox.showerror("Error", f"Failed to send prompt: {result.error}")
    
    def _handle_regenerate_response_result(self, result: ScrapingResult):
        """Handle regenerate response result."""
        if result.success:
            conversation = result.data
            self._update_status(
                "Response regenerated",
                f"Successfully regenerated response in conversation: {conversation['title']}"
            )
            self._update_conversation_content(conversation)
            messagebox.showinfo("Success", "Response regenerated successfully!")
        else:
            self._update_status("Failed to regenerate response", result.error)
            messagebox.showerror("Error", f"Failed to regenerate response: {result.error}")
    
    def _update_conversation_content(self, conversation: dict):
        """Update the conversation content display."""
        if not conversation.get('content'):
            return
        
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, conversation['content'])
        
        # Update conversation in list
        idx = self.conv_listbox.curselection()[0]
        self.conversations[idx] = conversation
        self._update_results_tree()
    
    def _handle_thread_result(self, result_tuple):
        """Handle results from worker threads."""
        operation, scraping_result = result_tuple
        
        handlers = {
            "login": self._handle_login_result,
            "extract_conversations": self._handle_extract_conversations_result,
            "extract_content": self._handle_extract_content_result,
            "send_prompt": self._handle_send_prompt_result,
            "regenerate_response": self._handle_regenerate_response_result
        }
        
        if operation in handlers:
            handlers[operation](scraping_result)
        
        self._enable_controls()
        self.progress_var.set(0)
    
    def _handle_login_result(self, result: ScrapingResult):
        """Handle login result."""
        if result.success:
            self._update_status("Login successful", f"Logged in via {result.metadata.get('method', 'unknown')}")
            messagebox.showinfo("Success", "Login successful!")
        else:
            self._update_status("Login failed", result.error)
            messagebox.showerror("Login Failed", result.error)
    
    def _handle_extract_conversations_result(self, result: ScrapingResult):
        """Handle conversation extraction result."""
        if result.success:
            self.conversations = result.data
            self._update_status("Conversations extracted", f"Extracted {len(self.conversations)} conversations")
            self._update_results_tree()
            messagebox.showinfo("Success", f"Extracted {len(self.conversations)} conversations!")
        else:
            self._update_status("Extraction failed", result.error)
            messagebox.showerror("Extraction Failed", result.error)
    
    def _handle_extract_content_result(self, result: ScrapingResult):
        """Handle content extraction result."""
        if result.success:
            self.conversations = result.data
            self._update_status(
                "Content extracted",
                f"Extracted content from {result.metadata['successful']}/{result.metadata['total']} conversations "
                f"({result.metadata['failed']} failed)"
            )
            self._update_results_tree()
            messagebox.showinfo(
                "Success",
                f"Extracted content from {result.metadata['successful']}/{result.metadata['total']} conversations!"
            )
        else:
            self._update_status("Content extraction failed", result.error)
            messagebox.showerror("Content Extraction Failed", result.error)
    
    def _update_results_tree(self):
        """Update the results treeview with conversation data."""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Clear conversation list
        self.conv_listbox.delete(0, tk.END)
        
        # Update both displays
        for conv in self.conversations:
            # Update treeview
            self.results_tree.insert("", tk.END, values=(
                conv.get('title', 'Untitled'),
                conv.get('message_count', 0),
                conv.get('model', 'Unknown'),
                "Extracted" if conv.get('content') else "Pending",
                conv.get('url', '')
            ))
            
            # Update listbox
            self.conv_listbox.insert(tk.END, conv.get('title', 'Untitled'))
    
    def _update_status(self, status: str, details: str):
        """Update status display."""
        self.status_var.set(status)
        self.status_details.delete(1.0, tk.END)
        self.status_details.insert(1.0, details)
    
    def _is_operation_running(self) -> bool:
        """Check if an operation is currently running."""
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Warning", "Operation already in progress")
            return True
        return False
    
    def _check_prerequisites(self) -> bool:
        """Check if prerequisites are met for operations."""
        if self._is_operation_running():
            return False
        return True
    
    def _disable_controls(self):
        """Disable control buttons during operations."""
        buttons = [
            self.login_button, self.cookie_login_button, self.extract_button,
            self.content_button, self.save_button, self.send_button,
            self.regenerate_button
        ]
        for button in buttons:
            button.config(state="disabled")
    
    def _enable_controls(self):
        """Enable control buttons after operations."""
        buttons = [
            self.login_button, self.cookie_login_button, self.extract_button,
            self.content_button, self.save_button
        ]
        for button in buttons:
            button.config(state="normal")
        
        # Only enable interaction buttons if conversation selected
        if self.conv_listbox.curselection():
            self.send_button.config(state="normal")
            self.regenerate_button.config(state="normal")
        else:
            self.send_button.config(state="disabled")
            self.regenerate_button.config(state="disabled")
    
    def on_destroy(self):
        """Clean up resources when panel is destroyed."""
        if self.worker_thread and self.worker_thread.is_alive():
            # TODO: Implement proper thread cleanup
            pass