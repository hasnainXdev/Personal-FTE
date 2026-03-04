#!/usr/bin/env python3
"""Process approved LinkedIn posts manually."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.services.linkedin_service import LinkedInService


async def process_approved_posts(vault_path: str):
    """Process all approved LinkedIn posts."""
    vault = Path(vault_path)
    approved_folder = vault / 'Approved'
    logs = vault / 'Logs'
    
    if not approved_folder.exists():
        print("❌ Approved folder doesn't exist")
        return
    
    # Get all LinkedIn post files
    linkedin_files = [f for f in approved_folder.glob('LINKEDIN_POST_*.md')]
    
    if not linkedin_files:
        print("ℹ️  No LinkedIn posts in Approved folder")
        return
    
    print(f"📋 Found {len(linkedin_files)} LinkedIn post(s) to process\n")
    
    # Initialize LinkedIn service
    service = LinkedInService(str(vault))
    
    try:
        # Initialize browser
        print("🔌 Initializing browser...")
        await service.initialize()
        
        # Check if logged in
        print("🔐 Checking login status...")
        logged_in = await service.is_logged_in()
        
        if not logged_in:
            print("❌ Not logged into LinkedIn!")
            print("\n📝 Run login first:")
            print("   python3 process_approved_posts.py --login")
            return
        
        print("✅ Logged in successfully\n")
        
        # Process each post
        for file_path in linkedin_files:
            print(f"📝 Processing: {file_path.name}")
            
            # Read post content
            content = file_path.read_text()
            
            # Extract post content from markdown
            post_content = extract_post_content(content)
            if not post_content:
                print(f"  ⚠️  Could not extract post content, skipping")
                continue
            
            # Post to LinkedIn
            print(f"  📤 Posting to LinkedIn...")
            result = await service.post_update(post_content)
            
            if result['success']:
                print(f"  ✅ Posted successfully! ID: {result['post_id']}")
                
                # Move to Done
                done_folder = vault / 'Done' / 'LinkedIn'
                done_folder.mkdir(parents=True, exist_ok=True)
                dest_path = done_folder / file_path.name
                file_path.rename(dest_path)
                print(f"  📁 Moved to Done folder")
            else:
                print(f"  ❌ Failed: {result['error']}")
            
            print()
        
        print("✅ All posts processed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await service.close()


def extract_post_content(markdown_content: str) -> str:
    """Extract the actual post content from the markdown file."""
    lines = markdown_content.split('\n')
    
    in_post_section = False
    post_lines = []
    
    for line in lines:
        if line.strip() == '## Post Content':
            in_post_section = True
            continue
        
        if in_post_section:
            if line.strip().startswith('##'):
                break
            post_lines.append(line)
    
    # Clean up and join
    post_content = '\n'.join(post_lines).strip()
    
    # Remove markdown formatting artifacts
    if post_content.startswith('\n'):
        post_content = post_content[1:]
    
    return post_content


async def login_linkedin(vault_path: str):
    """Login to LinkedIn and save session."""
    vault = Path(vault_path)
    service = LinkedInService(str(vault))
    
    try:
        print("🔌 Initializing browser...")
        await service.initialize()
        
        print("📝 Opening LinkedIn login page...")
        print("⏳ Please log in manually (you have 5 minutes)")
        print("💡 Tip: Use 'Remember me' to save your session")
        
        await service.login(timeout_seconds=300)
        
        print("\n✅ Login complete! Session saved.")
        print(f"📁 Session location: {service.session_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await service.close()


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process approved LinkedIn posts')
    parser.add_argument('--vault', '-v', default='./AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--login', '-l', action='store_true',
                       help='Login to LinkedIn (first time setup)')
    
    args = parser.parse_args()
    
    if args.login:
        await login_linkedin(args.vault)
    else:
        await process_approved_posts(args.vault)


if __name__ == '__main__':
    asyncio.run(main())
