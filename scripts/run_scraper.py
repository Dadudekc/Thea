#!/usr/bin/env python3
"""
scripts/run_scraper.py

Run the Dream.OS historical scraper via ScraperOrchestrator,
then apply test_template_responses to generate ChatGPT-ready prompts.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scraper_orchestrator import ScraperOrchestrator
from test_template_responses import TemplateResponder

def main():
    print("🚀 Starting Dream.OS scraper with template generation")
    
    # 1. Initialize ScraperOrchestrator
    orchestrator = ScraperOrchestrator(headless=False, use_undetected=True)
    
    # Initialize browser
    if not orchestrator.initialize_browser().success:
        print("❌ Browser initialization failed")
        return
    
    try:
        # 2. Login process
        print("🔐 Attempting login...")
        login_result = orchestrator.login_and_save_cookies(
            username=os.getenv("CHATGPT_USERNAME", "dadudekc@gmail.com"),
            password=os.getenv("CHATGPT_PASSWORD", "Falcons#1247"),
            allow_manual=True,
            manual_timeout=120,
        )
        
        if not login_result.success:
            if login_result.metadata and login_result.metadata.get("requires_manual_login"):
                print("⏳ Manual login required - please login in the browser window")
                # Wait for manual login
                import time
                for waited in range(0, 120, 5):
                    if orchestrator.driver and "chat.openai.com" in orchestrator.driver.current_url:
                        try:
                            conv_items = orchestrator.driver.find_elements("css selector", ".conversation-list-item")
                            if conv_items:
                                print(f"✅ Login complete after {waited}s")
                                orchestrator.cookie_manager.save_cookies(orchestrator.driver)
                                break
                        except:
                            pass
                    time.sleep(5)
                else:
                    print("❌ Manual login timeout")
                    return
            else:
                print(f"❌ Login failed: {login_result.error}")
                return
        
        # 3. Extract conversations
        print("📋 Extracting conversation list...")
        conversations_result = orchestrator.extract_conversations(max_conversations=1300)
        
        if not conversations_result.success:
            print(f"❌ Failed to extract conversations: {conversations_result.error}")
            return
        
        conversations = conversations_result.data or []
        print(f"✅ Found {len(conversations)} conversations")
        
        # 4. Convert to raw format
        raw_convos = []
        for conv in conversations:
            raw_convos.append({
                "id": conv.id,
                "title": conv.title,
                "url": conv.url,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "message_count": conv.message_count,
                "content": conv.content,
            })
        
        # 5. Apply template responder
        print("🎯 Applying template responses...")
        responder = TemplateResponder()
        templated = responder.generate_responses(raw_convos)
        
        # 6. Save responses organized by type
        print("💾 Saving responses by type...")
        saved_files = responder.save_responses_by_type()
        
        # 7. Generate specialized outputs
        print("🎯 Generating specialized outputs...")
        
        # MMORPG data for quest generation and skill advancement
        mmorpg_data = responder.get_mmorpg_data()
        if mmorpg_data:
            mmorpg_file = "outputs/mmorpg_integration.json"
            with open(mmorpg_file, "w", encoding="utf-8") as f:
                json.dump(mmorpg_data, f, indent=2, ensure_ascii=False)
            print(f"⚔️ MMORPG data saved to {mmorpg_file}")
        
        # Devlog content for blog posts and updates
        devlog_data = responder.get_devlog_content()
        if devlog_data:
            devlog_file = "outputs/devlog_content.json"
            with open(devlog_file, "w", encoding="utf-8") as f:
                json.dump(devlog_data, f, indent=2, ensure_ascii=False)
            print(f"📝 Devlog content saved to {devlog_file}")
        
        # 8. Write outputs
        os.makedirs("outputs", exist_ok=True)
        
        # Save raw conversations
        raw_file = "outputs/all_convos_raw.json"
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_convos, f, indent=2, ensure_ascii=False)
        
        # Save templated conversations
        templated_file = "outputs/all_convos_templated.json"
        with open(templated_file, "w", encoding="utf-8") as f:
            json.dump(templated, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Scrape complete: raw={len(raw_convos)} entries, templated={len(templated)} outputs")
        print(f"📁 Raw conversations saved to: {raw_file}")
        print(f"📁 Templated conversations saved to: {templated_file}")
        
        # Show response counts by type
        print(f"\n📈 Responses by type:")
        for response_type, responses_list in responder.responses.items():
            if responses_list:
                print(f"  {response_type}: {len(responses_list)} responses")
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        orchestrator.close()
        print("✅ Scraper closed")

if __name__ == "__main__":
    main() 