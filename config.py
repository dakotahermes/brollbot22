import os
import streamlit as st
from dataclasses import dataclass
from typing import Dict

@dataclass
class Config:
    """Application configuration settings"""
    OPENAI_MODEL: str = "gpt-4"
    DEFAULT_DURATION: int = 3  # Shorter for social media
    DEFAULT_ASPECT_RATIO: str = "9:16"  # Mobile-first
    CACHE_TTL: int = 3600
    MAX_SCRIPT_LENGTH: int = 5000
    MIN_SCRIPT_LENGTH: int = 10
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables or Streamlit secrets"""
        # Try to get API key from Streamlit secrets first, then environment
        try:
            openai_key = st.secrets.get("OPENAI_API_KEY")
        except (AttributeError, FileNotFoundError):
            openai_key = os.getenv("OPENAI_API_KEY")
        
        # Set the environment variable for OpenAI client
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        
        return cls(
            OPENAI_MODEL=os.getenv("OPENAI_MODEL", cls.OPENAI_MODEL),
            DEFAULT_DURATION=int(os.getenv("DEFAULT_DURATION", cls.DEFAULT_DURATION)),
            DEFAULT_ASPECT_RATIO=os.getenv("DEFAULT_ASPECT_RATIO", cls.DEFAULT_ASPECT_RATIO),
            CACHE_TTL=int(os.getenv("CACHE_TTL", cls.CACHE_TTL)),
            MAX_SCRIPT_LENGTH=int(os.getenv("MAX_SCRIPT_LENGTH", cls.MAX_SCRIPT_LENGTH)),
            MIN_SCRIPT_LENGTH=int(os.getenv("MIN_SCRIPT_LENGTH", cls.MIN_SCRIPT_LENGTH)),
        )

# DIRECT RESPONSE TONE GUIDANCE
TONE_GUIDANCE: Dict[str, str] = {
    'hook': "Create pattern interrupts, shocking moments, 'wait what?' visuals that stop scrolling immediately",
    'problem_agitation': "Show clear pain points, frustrations, struggles that your audience relates to",
    'solution_reveal': "Display dramatic transformations, product reveals, 'aha moments' that build desire",
    'social_proof': "Include crowds, testimonials, success stories, authority figures, trust signals",
    'urgency': "Show countdown timers, limited quantities, people rushing, FOMO triggers, scarcity",
    'desire': "Feature aspirational lifestyle, success moments, transformations, dream outcomes",
    'curiosity': "Create knowledge gaps, partial reveals, 'secret' moments, mysterious elements",
    'authority': "Display credentials, expert endorsements, scientific proof, media mentions"
}

# DIRECT RESPONSE FORMAT GUIDANCE
FORMAT_GUIDANCE: Dict[str, str] = {
    'ugc_style': "Raw, authentic footage that looks like real user-generated content, genuine reactions, selfie-style",
    'testimonial': "Real customer transformations, before/after reveals, success story moments, emotional reactions",
    'demo_style': "Product in action, step-by-step process, how-it-works moments, clear demonstrations",
    'influencer_style': "Polished but authentic, aspirational lifestyle, authority positioning, trend-aware",
    'news_style': "Breaking news feel, urgent updates, expert interviews, credible presentation",
    'comparison': "Side-by-side comparisons, before/after, competitor analysis, clear differentiation"
}

# CONVERSION-FOCUSED SCENE TYPES
SCENE_TYPES: Dict[str, str] = {
    'hook_opener': "First 3 seconds - pattern interrupt, shocking visual, unexpected moment",
    'problem_reveal': "Show the pain/struggle your audience faces daily",
    'agitation': "Make the problem feel urgent and costly to ignore",
    'solution_intro': "First glimpse of your product/service solving the problem",
    'transformation': "Before/after moments, dramatic changes, success stories",
    'social_proof': "Others using/loving your solution, testimonials, crowds",
    'authority_building': "Credentials, expert endorsements, media coverage",
    'urgency_creation': "Limited time/quantity, countdown timers, scarcity",
    'benefit_stacking': "Multiple value propositions, feature highlights",
    'objection_handling': "Address common concerns, show proof points",
    'cta_support': "Arrows pointing, hands clicking, mobile interactions"
}

# PLATFORM-SPECIFIC OPTIMIZATIONS
PLATFORM_SPECS: Dict[str, Dict[str, str]] = {
    'facebook': {
        'aspect_ratio': '1:1',
        'duration': '15-30 seconds',
        'focus': 'Lifestyle transformations, social moments, family/friends content'
    },
    'instagram_feed': {
        'aspect_ratio': '1:1',
        'duration': '15-60 seconds', 
        'focus': 'Aesthetic appeal, lifestyle upgrade, influencer-style content'
    },
    'instagram_stories': {
        'aspect_ratio': '9:16',
        'duration': '5-15 seconds',
        'focus': 'Quick hooks, swipe-up CTAs, personal/intimate feel'
    },
    'tiktok': {
        'aspect_ratio': '9:16',
        'duration': '15-30 seconds',
        'focus': 'Trending styles, quick cuts, younger demographic, viral potential'
    },
    'youtube_shorts': {
        'aspect_ratio': '9:16', 
        'duration': '15-60 seconds',
        'focus': 'Educational content, how-to reveals, authority building'
    },
    'snapchat': {
        'aspect_ratio': '9:16',
        'duration': '3-10 seconds',
        'focus': 'Ultra-quick hooks, instant gratification, mobile-native'
    }
}