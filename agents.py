# Updated agents.py for DIRECT RESPONSE SOCIAL MEDIA ADS

import json
import logging
from typing import List, Optional
from openai import OpenAI
import streamlit as st

from models import AdScriptInput, SceneBeat, BrollPrompt
from config import Config, TONE_GUIDANCE, FORMAT_GUIDANCE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize config
config = Config.from_env()

class BrollAgent:
    """Main agent class for B-roll generation - DIRECT RESPONSE FOCUSED"""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
    
    def _get_system_prompt(self, tone: str, format_type: str) -> str:
        """Generate system prompt optimized for direct response social media ads"""
        base_prompt = """
You are a B-roll specialist for high-converting social media ads.

Create short, simple scene descriptions that:
- Grab attention in first 3 seconds
- Support direct response marketing goals
- Work well for AI video generation (Runway, Pika, Kling)
- Are optimized for mobile viewing

For each moment, output:
- A timestamp (every 3-5 seconds)
- A SIMPLE, clear scene description (under 15 words)
- The marketing emotion it triggers (frustrated, excited, happy, amazed, etc.)
- The script excerpt it supports

KEY SCENE TYPES:
- Problem moments (frustration, struggle)
- Solution reveals (product in action)
- Transformation (before/after)
- Social proof (happy customers)
- Urgency (timers, scarcity)

KEEP DESCRIPTIONS SIMPLE:
✅ GOOD: "Person frustrated with phone"
✅ GOOD: "Happy customer holding product"
✅ GOOD: "Before and after comparison"
❌ BAD: "Close-up of person's disillusioned face as they futilely make cold calls"

Respond only in raw JSON format:

[
  {
    "timestamp": "00:00",
    "scene_description": "Person looking frustrated at phone",
    "emotion": "frustrated",
    "script_excerpt": "Tired of cold calling?"
  }
]
"""
        
        # Add specific tone guidance for direct response (simplified)
        dr_tone_guidance = {
            'hook': "Create simple attention-grabbing moments",
            'problem': "Show clear frustration or struggle", 
            'solution': "Display product solving the problem",
            'social_proof': "Show happy customers or testimonials",
            'urgency': "Include countdown or scarcity elements",
            'transformation': "Before and after moments",
            'curiosity': "Partial reveals or mysterious elements"
        }
        
        # Add format guidance for direct response (simplified)
        dr_format_guidance = {
            'UGC': "Authentic, user-generated style footage",
            'talking_head': "Speaker with engaging gestures",
            'testimonial': "Real customer reactions and success stories"
        }
        
        tone_guide = dr_tone_guidance.get(tone, "")
        format_guide = dr_format_guidance.get(format_type, "")
        
        if tone_guide:
            base_prompt += f"\n\nTONE STRATEGY: {tone_guide}"
        if format_guide:
            base_prompt += f"\nFORMAT STRATEGY: {format_guide}"
            
        # Add platform-specific optimization (simplified)
        base_prompt += """

EXAMPLES OF GOOD SCENE DESCRIPTIONS:
- "Person frustrated with laptop"
- "Product reveal close-up"
- "Happy customer testimonial"
- "Before and after split screen"
- "Countdown timer on phone"
- "Money being saved"
- "Problem being solved"
"""
            
        return base_prompt
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def parse_script(_self, script: str, tone: str, format_type: str) -> Optional[List[dict]]:
        """Parse script into high-converting scene beats (cached version)"""
        try:
            system_prompt = _self._get_system_prompt(tone, format_type)
            user_prompt = f"""
            DIRECT RESPONSE AD SCRIPT: {script}
            TARGET TONE: {tone}
            AD FORMAT: {format_type}
            
            Create B-roll that maximizes clicks and conversions for social media ads.
            """

            response = _self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                timeout=30
            )

            beats_data = json.loads(response.choices[0].message.content)
            
            # Validate the response structure
            validated_beats = []
            for beat_data in beats_data:
                try:
                    beat = SceneBeat(**beat_data)
                    validated_beats.append(beat.dict())
                except Exception as e:
                    logger.warning(f"Skipping invalid beat: {e}")
                    continue
                    
            return validated_beats
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            st.error("Failed to parse the script. The AI response was not in the expected format. Please try again.")
            return None
        except Exception as e:
            logger.error(f"API call failed: {e}")
            st.error(f"Service temporarily unavailable: {str(e)}. Please try again.")
            return None
    
    def _assess_generation_feasibility(self, scene_description: str) -> tuple[bool, float]:
        """Assess whether a scene can be generated by AI video tools - DIRECT RESPONSE FOCUSED"""
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": """You're a direct response video specialist. Judge whether this scene can be created for social media ads using AI video generation or easily found stock footage.

PRIORITIZE scenes that:
- Work great on mobile (9:16 format)
- Grab attention in first 3 seconds
- Are simple enough to read quickly
- Support conversion goals
- Can be generated by current AI tools (Runway, Pika, Kling)

Respond with ONLY a JSON object:
{"feasible": true/false, "confidence": 0.0-1.0, "conversion_potential": 0.0-1.0}

Be practical about what converts vs. what's just pretty."""
                    },
                    {"role": "user", "content": scene_description}
                ],
                timeout=15
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("feasible", False), result.get("confidence", 0.0)
            
        except Exception as e:
            logger.warning(f"Failed to assess feasibility: {e}")
            return True, 0.7  # Default to feasible with good confidence for DR content
    
    def generate_prompts(self, beats_data: List[dict], duration: int = None, aspect_ratio: str = None) -> List[BrollPrompt]:
        """Convert scene beats into direct response video generation prompts"""
        if duration is None:
            duration = 3  # Shorter clips for social media
        if aspect_ratio is None:
            aspect_ratio = "9:16"  # Mobile-first
            
        prompts = []
        
        for beat_data in beats_data:
            try:
                beat = SceneBeat(**beat_data)
                
                # Assess generation feasibility
                is_feasible, confidence = self._assess_generation_feasibility(beat.scene_description)
                
                if is_feasible and confidence > 0.4:  # Lower threshold for DR content
                    # Clean, natural prompt for AI generation
                    emotion_map = {
                        'problem_hook': 'frustrated',
                        'solution': 'satisfied', 
                        'social_proof': 'happy',
                        'urgency': 'excited',
                        'transformation': 'amazed',
                        'curiosity': 'intrigued'
                    }
                    
                    natural_emotion = emotion_map.get(beat.emotion, beat.emotion)
                    formatted_prompt = f"{beat.scene_description}, {natural_emotion}, cinematic"
                    
                    search_instruction = f"Search for: {beat.scene_description} showing {natural_emotion} emotion"
                    
                    prompt_obj = BrollPrompt(
                        prompt=formatted_prompt,
                        duration=duration,
                        aspect_ratio=aspect_ratio,
                        insert_after=beat.script_excerpt,
                        search_instruction=search_instruction,
                        confidence_score=confidence
                    )
                    prompts.append(prompt_obj)
                else:
                    logger.info(f"Skipping low-conversion scene: {beat.scene_description}")
                    
            except Exception as e:
                logger.warning(f"Failed to process beat: {e}")
                continue
        
        return prompts

def create_agent(openai_client: OpenAI) -> BrollAgent:
    """Factory function to create a BrollAgent instance"""
    return BrollAgent(openai_client)