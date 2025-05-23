from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional

class AdScriptInput(BaseModel):
    """Input model for ad script analysis"""
    script: str = Field(..., min_length=10, max_length=5000, description="The ad script content")
    tone: Literal['inspiring', 'urgent', 'calm', 'funny', 'serious', 'emotional', 'uplifting', 'mysterious']
    format: Literal['UGC', 'talking_head', 'testimonial']
    
    @validator('script')
    def validate_script(cls, v):
        if not v or not v.strip():
            raise ValueError('Script cannot be empty')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "script": "Transform your morning routine with our revolutionary coffee maker...",
                "tone": "inspiring",
                "format": "UGC"
            }
        }

class SceneBeat(BaseModel):
    """Represents a single scene beat with emotional context"""
    timestamp: str = Field(..., description="Timestamp in MM:SS format")
    scene_description: str = Field(..., min_length=10, description="Vivid scene description")
    emotion: str = Field(..., description="Core emotion the visual supports")
    script_excerpt: str = Field(..., description="Script excerpt for placement")
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        # Basic validation for timestamp format
        if not v or ':' not in v:
            raise ValueError('Timestamp must be in MM:SS format')
        return v

class BrollPrompt(BaseModel):
    """Complete B-roll prompt with generation parameters"""
    prompt: str = Field(..., description="Formatted prompt for video generation")
    duration: int = Field(default=5, ge=1, le=30, description="Duration in seconds")
    aspect_ratio: str = Field(default="9:16", description="Video aspect ratio")
    insert_after: str = Field(..., description="Script excerpt to insert after")
    search_instruction: str = Field(..., description="Instructions for finding stock footage")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI generation feasibility score")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Morning sunlight streaming through window, cinematic, inspiring mood",
                "duration": 5,
                "aspect_ratio": "9:16",
                "insert_after": "Transform your morning routine...",
                "search_instruction": "Search for morning sunlight window scenes with inspiring vibe"
            }
        }
