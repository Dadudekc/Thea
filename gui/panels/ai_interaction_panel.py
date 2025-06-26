"""
AI Interaction Panel for Dream.OS GUI
Handles conversation interaction and AI querying.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
from typing import Optional, List, Dict
import logging
from pathlib import Path

from scrapers.chatgpt_scraper import ChatGPTScraper
from core.chatgpt_dreamscape_agent import ChatGPTDreamscapeAgent

logger = logging.getLogger(__name__)

class AIInteractionPanel(ttk.Frame):
    """Panel for AI interaction and conversation querying."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize state
        self.conversations: List[Dict] = []
        self.current_conversation: Optional[Dict] = None
        self.thread_queue = queue.Queue()
        self.worker_thread: Optional[threading.Thread] = None
        
        # Initialize Dreamscape agent
        self.dreamscape_agent = ChatGPTDreamscapeAgent()
        
        # Setup UI
        self._setup_ui()
        self._setup_threading()
        
        logger.info("AI Interaction Panel initialized with Dreamscape integration")
    
    def _setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        ttk.Label(main_frame, text="AI Interaction", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Split view
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - conversation list
        self._create_conversation_list(paned)
        
        # Right side - interaction area
        self._create_interaction_area(paned)
        
        # Status area
        self._create_status_area(main_frame)
    
    def _create_conversation_list(self, parent):
        """Create the conversation list area."""
        left_frame = ttk.Frame(parent)
        
        # Header
        ttk.Label(left_frame, text="Conversations", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Search
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filter_conversations)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(search_frame, text="🔍", width=3, command=self._filter_conversations).pack(side=tk.LEFT, padx=(5, 0))
        
        # Conversation list
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.conv_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.conv_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.conv_listbox.bind('<<ListboxSelect>>', self._on_conversation_selected)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.conv_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conv_listbox.configure(yscrollcommand=scrollbar.set)
        
        parent.add(left_frame, weight=1)
    
    def _create_interaction_area(self, parent):
        """Create the interaction area."""
        right_frame = ttk.Frame(parent)
        
        # Conversation info
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(info_frame, text="No conversation selected", font=("Arial", 12, "bold"))
        self.title_label.pack(side=tk.LEFT)
        
        self.model_label = ttk.Label(info_frame, text="")
        self.model_label.pack(side=tk.RIGHT)
        
        # Dreamscape status
        status_frame = ttk.LabelFrame(right_frame, text="Dreamscape Status", padding=5)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.tier_label = ttk.Label(status_frame, text="Tier: Unknown")
        self.tier_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_label = ttk.Label(status_frame, text="Progress: 0%")
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        self.skills_label = ttk.Label(status_frame, text="Skills: None")
        self.skills_label.pack(side=tk.LEFT, padx=5)
        
        # Conversation content
        content_frame = ttk.LabelFrame(right_frame, text="Conversation", padding=5)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Prompt area
        prompt_frame = ttk.LabelFrame(right_frame, text="Dreamscape Query", padding=5)
        prompt_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=4, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X)
        
        # Action buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X)
        
        self.send_button = ttk.Button(button_frame, text="Send Query", command=self._send_query)
        self.send_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.process_button = ttk.Button(button_frame, text="Process with Dreamscape", command=self._process_with_dreamscape)
        self.process_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(button_frame, text="Clear", command=lambda: self.prompt_text.delete(1.0, tk.END))
        self.clear_button.pack(side=tk.LEFT)
        
        # Disable interaction buttons initially
        self._set_interaction_state("disabled")
        
        parent.add(right_frame, weight=2)
    
    def _create_status_area(self, parent):
        """Create the status area."""
        status_frame = ttk.LabelFrame(parent, text="Status", padding=5)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
    
    def _setup_threading(self):
        """Setup threading support."""
        def check_queue():
            try:
                while True:
                    result = self.thread_queue.get_nowait()
                    self._handle_thread_result(result)
            except queue.Empty:
                pass
            finally:
                self.after(100, check_queue)
        
        self.after(100, check_queue)
    
    def set_conversations(self, conversations: List[Dict]):
        """Set the conversation list."""
        self.conversations = conversations
        self._update_conversation_list()
    
    def _update_conversation_list(self):
        """Update the conversation listbox."""
        self.conv_listbox.delete(0, tk.END)
        for conv in self.conversations:
            self.conv_listbox.insert(tk.END, conv.get('title', 'Untitled'))
    
    def _filter_conversations(self, *args):
        """Filter conversations based on search text."""
        search_text = self.search_var.get().lower()
        self.conv_listbox.delete(0, tk.END)
        
        for conv in self.conversations:
            title = conv.get('title', '').lower()
            if search_text in title:
                self.conv_listbox.insert(tk.END, conv.get('title', 'Untitled'))
    
    def _on_conversation_selected(self, event):
        """Handle conversation selection."""
        if not self.conv_listbox.curselection():
            return
        
        # Get selected conversation
        idx = self.conv_listbox.curselection()[0]
        title = self.conv_listbox.get(idx)
        self.current_conversation = next(
            (conv for conv in self.conversations if conv.get('title') == title),
            None
        )
        
        if not self.current_conversation:
            return
        
        # Update display
        self.title_label.config(text=self.current_conversation.get('title', 'Untitled'))
        self.model_label.config(text=f"Model: {self.current_conversation.get('model', 'Unknown')}")
        
        self.content_text.delete(1.0, tk.END)
        if content := self.current_conversation.get('content'):
            self.content_text.insert(tk.END, content)
        
        # Enable interaction buttons
        self._set_interaction_state("normal")
    
    def _send_query(self):
        """Send a query to the Dreamscape AI."""
        if not self.current_conversation:
            messagebox.showerror("Error", "No conversation selected")
            return
        
        query = self.prompt_text.get(1.0, tk.END).strip()
        if not query:
            messagebox.showerror("Error", "Please enter a query")
            return
        
        self._update_status("Sending query to Dreamscape AI...", 0)
        self._set_interaction_state("disabled")
        
        self.worker_thread = threading.Thread(
            target=self._send_query_worker,
            args=(self.current_conversation, query)
        )
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def _send_query_worker(self, conversation: Dict, query: str):
        """Worker thread for sending queries."""
        try:
            result = self.dreamscape_agent.query_dreamscape_ai(
                query,
                conversation_id=conversation.get('id')
            )
            
            if result['success']:
                self.thread_queue.put(("query_response", {
                    'success': True,
                    'response': result['ai_response'],
                    'memory_updates': result['memory_updates']
                }))
            else:
                self.thread_queue.put(("query_response", {
                    'success': False,
                    'error': result['error']
                }))
                
        except Exception as e:
            logger.error(f"Query worker error: {e}")
            self.thread_queue.put(("query_response", {
                'success': False,
                'error': str(e)
            }))
    
    def _process_with_dreamscape(self):
        """Process the current conversation with Dreamscape AI."""
        if not self.current_conversation:
            messagebox.showerror("Error", "No conversation selected")
            return
        
        self._update_status("Processing with Dreamscape AI...", 0)
        self._set_interaction_state("disabled")
        
        self.worker_thread = threading.Thread(
            target=self._process_dreamscape_worker,
            args=(self.current_conversation,)
        )
        self.worker_thread.daemon = True
        self.worker_thread.start()
    
    def _process_dreamscape_worker(self, conversation: Dict):
        """Worker thread for Dreamscape processing."""
        try:
            result = self.dreamscape_agent.process_conversation_with_ai(
                conversation.get('id'),
                conversation.get('content', '')
            )
            
            if result['success']:
                self.thread_queue.put(("dreamscape_process", {
                    'success': True,
                    'response': result['ai_response'],
                    'memory_updates': result['memory_updates']
                }))
            else:
                self.thread_queue.put(("dreamscape_process", {
                    'success': False,
                    'error': result['error']
                }))
                
        except Exception as e:
            logger.error(f"Dreamscape process worker error: {e}")
            self.thread_queue.put(("dreamscape_process", {
                'success': False,
                'error': str(e)
            }))
    
    def _handle_thread_result(self, result):
        """Handle thread results."""
        operation, data = result
        
        if operation == "query_response":
            if data['success']:
                self._update_conversation_display(data['response'])
                if data['memory_updates']:
                    self._update_dreamscape_status(data['memory_updates'])
                self._update_status("Query processed successfully", 100)
                messagebox.showinfo("Success", "Query processed successfully!")
            else:
                self._update_status("Failed to process query", 0)
                messagebox.showerror("Error", f"Failed to process query: {data['error']}")
        
        elif operation == "dreamscape_process":
            if data['success']:
                self._update_conversation_display(data['response'])
                if data['memory_updates']:
                    self._update_dreamscape_status(data['memory_updates'])
                self._update_status("Dreamscape processing complete", 100)
                messagebox.showinfo("Success", "Dreamscape processing complete!")
            else:
                self._update_status("Failed to process with Dreamscape", 0)
                messagebox.showerror("Error", f"Failed to process with Dreamscape: {data['error']}")
        
        self._set_interaction_state("normal")
    
    def _update_conversation_display(self, conversation: Dict):
        """Update the conversation display."""
        if not conversation.get('content'):
            return
        
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, conversation['content'])
        
        # Update conversation in list
        idx = next(
            (i for i, conv in enumerate(self.conversations)
             if conv.get('id') == conversation.get('id')),
            None
        )
        if idx is not None:
            self.conversations[idx] = conversation
    
    def _update_status(self, message: str, progress: int):
        """Update status display."""
        self.status_var.set(message)
        self.progress_var.set(progress)
    
    def _set_interaction_state(self, state: str):
        """Set the state of interaction buttons."""
        buttons = [self.send_button, self.process_button, self.clear_button]
        for button in buttons:
            button.config(state=state)
    
    def _update_dreamscape_status(self, memory_updates: Dict):
        """Update the Dreamscape status display."""
        if not memory_updates:
            return
        
        # Update tier info
        tier_info = memory_updates.get('architect_tier_progression', {})
        if tier_info:
            self.tier_label.config(text=f"Tier: {tier_info.get('current_tier', 'Unknown')}")
            self.progress_label.config(text=f"Progress: {tier_info.get('progress_to_next_tier', 0)}%")
        
        # Update skills
        skills = memory_updates.get('skill_level_advancements', {})
        if skills:
            skills_text = ", ".join([f"{skill}: {level}" for skill, level in skills.items()])
            self.skills_label.config(text=f"Skills: {skills_text}")
    
    def close(self):
        """Clean up resources."""
        if self.dreamscape_agent:
            self.dreamscape_agent.close()