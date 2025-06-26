#!/usr/bin/env python3
"""
Dream.OS Prompt Deployer - Deploy prompt files to specific ChatGPT conversations with model routing.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.prompt_deployer import PromptDeployer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Dream.OS Prompt Deployer")
    parser.add_argument("--list-prompts", action="store_true", help="List all available prompts")
    parser.add_argument("--deploy", help="Deploy a specific prompt")
    parser.add_argument("--target-agent", help="Target agent for deployment")
    parser.add_argument("--conversation-id", help="Specific conversation ID")
    parser.add_argument("--add-prompt", help="Add a new prompt")
    parser.add_argument("--prompt-file", help="Prompt file path for adding new prompt")
    parser.add_argument("--description", help="Description for new prompt")
    
    args = parser.parse_args()
    
    # Create deployer
    deployer = PromptDeployer()
    
    try:
        if args.list_prompts:
            # List all prompts
            prompts = deployer.list_prompts()
            if prompts:
                print("Available prompts:")
                for prompt in prompts:
                    print(f"  - {prompt}")
            else:
                print("No prompts configured")
        
        elif args.add_prompt:
            # Add new prompt
            if not args.prompt_file or not args.target_agent:
                logger.error("--prompt-file and --target-agent required for adding prompts")
                return
            
            deployer.add_prompt(
                name=args.add_prompt,
                prompt_file=args.prompt_file,
                target_agent=args.target_agent,
                description=args.description or ""
            )
            print(f"✅ Added prompt: {args.add_prompt}")
        
        elif args.deploy:
            # Deploy prompt
            success = deployer.deploy_prompt(
                prompt_name=args.deploy,
                target_agent=args.target_agent,
                conversation_id=args.conversation_id
            )
            
            if success:
                print(f"✅ Successfully deployed prompt: {args.deploy}")
            else:
                print(f"❌ Failed to deploy prompt: {args.deploy}")
        
        else:
            # Show help if no action specified
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
    
    finally:
        deployer.close()

if __name__ == "__main__":
    main() 