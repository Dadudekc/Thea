#!/usr/bin/env python3
"""
Create Personal Knowledge Templates
===================================

Adds a set of templates focused on "based on everything you know about me..."
prompts that leverage the conversation history and personal context.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.memory_manager import MemoryManager


def create_personal_templates():
    """Create templates for personal-knowledge prompts."""
    
    mm = MemoryManager()
    
    templates = [
        {
            "name": "Personal Context Analysis",
            "description": "Analyze what the AI knows about you from conversation history",
            "template_content": """Based on everything you know about me from our conversation history, please provide a comprehensive analysis of:

1. **My Background & Interests**: What fields, topics, or domains do I seem most passionate about?
2. **My Communication Style**: How do I typically approach problems or ask questions?
3. **My Technical Level**: What's my apparent expertise level in various areas?
4. **My Goals & Aspirations**: What objectives or projects have I mentioned?
5. **My Learning Patterns**: How do I prefer to learn or receive information?

Please be specific and reference any patterns or recurring themes you've noticed in our interactions.""",
            "category": "personal-analysis"
        },
        {
            "name": "Personalized Advice",
            "description": "Get advice tailored to your specific situation and history",
            "template_content": """Based on everything you know about me from our conversation history, I'd like your personalized advice on: {{ topic }}

Please consider:
- My background and experience level in this area
- My communication and learning preferences
- Any relevant goals or projects I've mentioned
- My typical approach to similar challenges

Provide specific, actionable advice that takes into account what you've learned about me as an individual.""",
            "category": "personal-advice"
        },
        {
            "name": "Personal Knowledge Summary",
            "description": "Get a summary of what the AI knows about you",
            "template_content": """Based on our conversation history, please provide a concise summary of what you know about me:

**Key Facts & Background:**
- Professional/educational background
- Areas of expertise
- Current projects or goals

**Communication & Learning Style:**
- How I prefer to receive information
- My typical problem-solving approach
- Areas where I seek help most often

**Interests & Patterns:**
- Topics I'm most passionate about
- Recurring themes in our conversations
- Any notable preferences or tendencies

Please be honest about what you do and don't know about me, and note any areas where your knowledge might be limited.""",
            "category": "personal-summary"
        },
        {
            "name": "Personalized Learning Path",
            "description": "Create a learning path tailored to your background and goals",
            "template_content": """Based on everything you know about me from our conversation history, please design a personalized learning path for: {{ subject }}

Consider:
- My current knowledge level in this area
- My learning preferences and communication style
- My available time and resources
- My specific goals or use cases
- How this fits with my broader interests and projects

Provide:
1. A structured learning sequence
2. Recommended resources (books, courses, projects)
3. Milestones to track progress
4. Estimated timeline based on my typical pace
5. How to apply this knowledge to my specific context""",
            "category": "personal-learning"
        },
        {
            "name": "Personal Project Guidance",
            "description": "Get project guidance tailored to your skills and experience",
            "template_content": """Based on everything you know about me from our conversation history, I need guidance on this project: {{ project_description }}

Please provide personalized advice considering:
- My technical background and skill level
- My typical project approach and preferences
- Similar projects or challenges I've worked on
- My learning style and communication preferences
- My available resources and constraints

Include:
1. Recommended approach based on my experience level
2. Potential challenges and how to address them
3. Resources that match my learning style
4. Milestones and success metrics
5. How this project fits with my broader goals""",
            "category": "personal-projects"
        },
        {
            "name": "Personal Knowledge Gap Analysis",
            "description": "Identify knowledge gaps based on your conversation history",
            "template_content": """Based on everything you know about me from our conversation history, please analyze potential knowledge gaps in: {{ domain }}

Consider:
- My stated goals and aspirations
- My current skill level and experience
- Areas where I've struggled or asked for help
- Topics I haven't explored but might benefit from
- How this domain relates to my broader interests

Provide:
1. **Current Strengths**: What I seem to know well
2. **Identified Gaps**: Areas where I might need more knowledge
3. **Priority Recommendations**: Which gaps to address first and why
4. **Learning Resources**: Specific resources that match my style
5. **Integration Opportunities**: How new knowledge connects to existing projects""",
            "category": "personal-analysis"
        },
        {
            "name": "Personalized Problem Solving",
            "description": "Get problem-solving approach tailored to your style",
            "template_content": """Based on everything you know about me from our conversation history, I'm facing this challenge: {{ problem_description }}

Please provide a personalized problem-solving approach that considers:
- My typical problem-solving style and preferences
- My technical background and comfort level
- How I've successfully approached similar challenges
- My communication and learning preferences
- My available time and resources

Include:
1. **Recommended Approach**: Method that matches my style
2. **Step-by-Step Process**: Tailored to my experience level
3. **Potential Obstacles**: Based on my typical challenges
4. **Success Metrics**: How to know if the solution works
5. **Learning Opportunities**: What I can learn from this process""",
            "category": "personal-advice"
        }
    ]
    
    created_count = 0
    for template in templates:
        try:
            template_id = mm.create_template(
                name=template["name"],
                template_content=template["template_content"],
                description=template["description"],
                category=template["category"]
            )
            print(f"✅ Created template: {template['name']} (ID: {template_id})")
            created_count += 1
        except Exception as e:
            print(f"❌ Failed to create template '{template['name']}': {e}")
    
    print(f"\n🎉 Created {created_count}/{len(templates)} personal knowledge templates")
    print("\nCategories created:")
    categories = set(t["category"] for t in templates)
    for cat in sorted(categories):
        count = sum(1 for t in templates if t["category"] == cat)
        print(f"  • {cat}: {count} templates")
    
    mm.close()


if __name__ == "__main__":
    create_personal_templates() 