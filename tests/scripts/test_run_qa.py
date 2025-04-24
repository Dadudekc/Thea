# Placeholder for test file creation
# This edit ensures the directory is created if it doesn't exist 

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import json
import io

# --- Add project root to sys.path ---
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent # Adjust if needed
scripts_dir = project_root / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
# ------------------------------------

# Import the functions to test from run_qa script
try:
    from run_qa import generate_markdown_report, load_checklist, save_checklist, update_item_status, list_items, show_summary, main
except ImportError as e:
    print(f"Failed to import from run_qa.py. Ensure it's in the scripts directory and path is correct: {e}")
    # Define dummy functions if import fails, so tests can be collected
    def generate_markdown_report(data): return "" # type: ignore
    def load_checklist(path): return {}           # type: ignore
    def save_checklist(path, data): pass         # type: ignore
    def update_item_status(data, id, status): return False # type: ignore
    def list_items(data, filter_status=None): pass # type: ignore
    def show_summary(data): pass                  # type: ignore
    def main(): pass                              # type: ignore

class TestRunQAScript(unittest.TestCase):

    def setUp(self):
        """Set up sample data for tests."""
        self.sample_data = {
            "phase": "Sample Phase",
            "categories": {
                "cat_one": {
                    "description": "First category tests.",
                    "items": [
                        {"id": "T1", "label": "Test One", "status": "pass"},
                        {"id": "T2", "label": "Test Two", "status": "pending", "file": "test_file.py"}
                    ]
                },
                "cat_two": {
                    "description": "Second category.",
                    "items": [
                        {"id": "T3", "label": "Test Three", "status": "fail"},
                        {"id": "T4", "label": "Test Four", "status": "pass"}
                    ]
                },
                "empty_cat": {
                     "description": "No items here.",
                     "items": []
                }
            }
        }

    def test_generate_markdown_report_structure(self):
        """Test the basic structure and headers of the markdown report."""
        report = generate_markdown_report(self.sample_data)

        self.assertIn("# Sample Phase - QA Report", report)
        self.assertIn("_Last generated:", report)
        self.assertIn("## Cat One", report)
        self.assertIn("> First category tests.", report)
        self.assertIn("## Cat Two", report)
        self.assertIn("> Second category.", report)
        self.assertIn("## Empty Cat", report)
        self.assertIn("_(No items in this category)_", report)
        self.assertIn("## Overall Summary", report)

    def test_generate_markdown_report_cat_one_table(self):
        """Test the content of the first category's table."""
        report = generate_markdown_report(self.sample_data)
        # Check table header
        self.assertIn("| Status | ID   | Label                     | File/Notes |", report)
        # Check item T1 (Pass)
        self.assertIn("| ✅  | T1 | Test One |  |", report)
        # Check item T2 (Pending, with file)
        self.assertIn("| ❓  | T2 | Test Two | `test_file.py` |", report)

    def test_generate_markdown_report_cat_two_table(self):
        """Test the content of the second category's table."""
        report = generate_markdown_report(self.sample_data)
        # Check item T3 (Fail)
        self.assertIn("| ❌  | T3 | Test Three |  |", report)
        # Check item T4 (Pass)
        self.assertIn("| ✅  | T4 | Test Four |  |", report)

    def test_generate_markdown_report_summary_table(self):
        """Test the content of the overall summary table."""
        report = generate_markdown_report(self.sample_data)

        # Check summary table header
        self.assertIn("| Status    | Count | Percentage |", report)
        # Check Pass count (T1, T4)
        self.assertIn("| ✅ PASS | 2 | 50.0% |", report)
        # Check Fail count (T3)
        self.assertIn("| ❌ FAIL | 1 | 25.0% |", report)
        # Check Pending count (T2)
        self.assertIn("| ❓ PENDING | 1 | 25.0% |", report)
        # Check Total count
        self.assertIn("| **Total** | **4** | **100.0%** |", report)

    def test_generate_markdown_report_empty_checklist(self):
        """Test report generation with no categories or items."""
        empty_data = {"phase": "Empty Phase", "categories": {}}
        report = generate_markdown_report(empty_data)
        self.assertIn("# Empty Phase - QA Report", report)
        self.assertIn("_(No items found in checklist)_", report)
        self.assertNotIn("| Status | ID", report) # No tables should be present

    def test_list_items_default_formatting(self):
        """Test list_items prints all items with correct formatting."""
        buf = io.StringIO()
        with patch('sys.stdout', buf):
            list_items(self.sample_data)
        output = buf.getvalue()
        self.assertIn("--- Sample Phase ---", output)
        self.assertIn("[Cat One] - First category tests.", output)
        self.assertIn("  [T1] Test One - Status: PASS", output)
        self.assertIn("  [T2] Test Two (test_file.py) - Status: PENDING", output)
        self.assertIn("[Cat Two] - Second category.", output)
        self.assertIn("  [T3] Test Three - Status: FAIL", output)
        self.assertIn("  [T4] Test Four - Status: PASS", output)
        self.assertIn("Total items: 4. Items shown: 4.", output)

    def test_list_items_filtering(self):
        """Test list_items with filter_status only prints matching items."""
        buf = io.StringIO()
        with patch('sys.stdout', buf):
            list_items(self.sample_data, filter_status="fail")
        output = buf.getvalue()
        self.assertIn("[Cat One] - First category tests.", output)
        self.assertIn("  (No items match status 'fail')", output)
        self.assertIn("[Cat Two] - Second category.", output)
        self.assertIn("  [T3] Test Three - Status: FAIL", output)
        self.assertIn("Total items: 4. Items shown: 1.", output)

    def test_update_item_status_success(self):
        """Test that update_item_status correctly updates an item's status and returns True."""
        # Ensure initial status is as expected
        self.assertEqual(self.sample_data["categories"]["cat_one"]["items"][1]["status"], "pending")
        # Perform update
        result = update_item_status(self.sample_data, "T2", "pass")
        self.assertTrue(result)
        # Verify the status was updated
        self.assertEqual(self.sample_data["categories"]["cat_one"]["items"][1]["status"], "pass")

    def test_update_item_status_not_found(self):
        """Test that update_item_status returns False when item id is not found."""
        # Attempt to update non-existent item
        result = update_item_status(self.sample_data, "UNKNOWN", "fail")
        self.assertFalse(result)

    # TODO: Add tests for load/save checklist functionality (interaction with file system)
    # TODO: Add tests for main() function argument parsing and command dispatching

if __name__ == '__main__':
    unittest.main() 