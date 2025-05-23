import os
import json
import pandas as pd
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

from models import AdScriptInput, BrollPrompt
from agents import create_agent
from config import Config

# Load environment variables
load_dotenv()

# Initialize configuration
config = Config.from_env()

def initialize_openai_client() -> OpenAI:
    """Initialize and validate OpenAI client"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("⚠️ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        st.stop()
    
    try:
        client = OpenAI(api_key=api_key)
        # Test the connection
        client.models.list()
        return client
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {str(e)}")
        st.stop()

def validate_input(script: str) -> tuple[bool, str]:
    """Validate user input"""
    if not script or not script.strip():
        return False, "Please enter a script."
    
    if len(script) < config.MIN_SCRIPT_LENGTH:
        return False, f"Script must be at least {config.MIN_SCRIPT_LENGTH} characters long."
    
    if len(script) > config.MAX_SCRIPT_LENGTH:
        return False, f"Script must be less than {config.MAX_SCRIPT_LENGTH} characters long."
    
    return True, ""

def create_download_data(prompts: List[BrollPrompt]) -> tuple[str, str]:
    """Create downloadable data in CSV and JSON formats"""
    # Prepare data for export
    export_data = []
    for i, prompt in enumerate(prompts, 1):
        export_data.append({
            "sequence": i,
            "insert_after": prompt.insert_after,
            "prompt": prompt.prompt,
            "duration": prompt.duration,
            "aspect_ratio": prompt.aspect_ratio,
            "search_instruction": prompt.search_instruction,
            "confidence_score": prompt.confidence_score
        })
    
    # Create CSV
    df = pd.DataFrame(export_data)
    csv_data = df.to_csv(index=False)
    
    # Create JSON
    json_data = json.dumps(export_data, indent=2)
    
    return csv_data, json_data

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="B-Roll Bot - AI Video Assistant",
        page_icon="🎬",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Header
    st.title("🎬 B-Roll Bot")
    st.markdown("Transform your video scripts into professional B-roll suggestions using AI")
    
    # Initialize OpenAI client
    client = initialize_openai_client()
    agent = create_agent(client)
    
    # Sidebar with settings
    with st.sidebar:
        st.header("⚙️ Settings")
        duration = st.slider("Default Duration (seconds)", 1, 30, config.DEFAULT_DURATION)
        aspect_ratio = st.selectbox("Aspect Ratio", ["9:16", "16:9", "1:1", "4:5"], index=0)
        
        st.header("ℹ️ About")
        st.markdown("""
        This tool analyzes your video script and suggests B-roll footage that matches the tone and emotion of your content.
        
        **Features:**
        - Emotional scene analysis
        - AI-generated prompts
        - Stock footage search tips
        - Export to CSV/JSON
        """)
    
    # Main input section
    st.header("📝 Script Input")
    
    script_input = st.text_area(
        "Paste your ad script here:",
        placeholder="Enter your video script here (minimum 10 characters)...",
        help="Paste the full script you want to generate B-roll suggestions for",
        height=150
    )
    
    # Show character count
    if script_input:
        char_count = len(script_input)
        color = "green" if char_count >= config.MIN_SCRIPT_LENGTH else "orange"
        st.markdown(f"<span style='color: {color}'>Characters: {char_count}</span>", unsafe_allow_html=True)
    
    # Tone and format selection
    col1, col2 = st.columns(2)
    
    with col1:
        tone = st.selectbox(
            "Select Tone:",
            ["inspiring", "urgent", "calm", "funny", "serious", "emotional", "uplifting", "mysterious"],
            help="Choose the emotional tone that best matches your script"
        )
    
    with col2:
        format_type = st.selectbox(
            "Select Format:",
            ["UGC", "talking_head", "testimonial"],
            help="Choose the video format style"
        )
    
    # Generate button
    if st.button("🚀 Generate B-Roll Prompts", type="primary", use_container_width=True):
        # Validate input
        is_valid, error_message = validate_input(script_input)
        
        if not is_valid:
            st.error(error_message)
        else:
            # Create input object
            try:
                ad_input = AdScriptInput(script=script_input, tone=tone, format=format_type)
            except Exception as e:
                st.error(f"Input validation failed: {str(e)}")
                return
            
            # Process with loading indicator
            with st.spinner("🔍 Analyzing script and generating B-roll suggestions..."):
                # Step 1: Parse script into scene beats
                scene_beats_data = agent.parse_script(ad_input.script, ad_input.tone, ad_input.format)
                
                if scene_beats_data is None:
                    return
                
                if not scene_beats_data:
                    st.warning("No suitable scenes found in the script. Try a different tone or format.")
                    return
                
                # Step 2: Generate B-roll prompts
                broll_prompts = agent.generate_prompts(scene_beats_data, duration, aspect_ratio)
                
                if not broll_prompts:
                    st.warning("No feasible B-roll prompts could be generated. The script might be too abstract or complex for current AI video generation.")
                    return
            
            # Display results
            st.success(f"✅ Generated {len(broll_prompts)} B-roll suggestions!")
            
            # Results section
            st.header("🎥 Generated B-Roll Prompts")
            
            for i, prompt in enumerate(broll_prompts, 1):
                with st.expander(f"Scene {i}: {prompt.insert_after[:50]}..."):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**📍 Insert After:** _{prompt.insert_after}_")
                        st.markdown(f"**🎬 Generation Prompt:**")
                        st.code(prompt.prompt)
                        st.markdown(f"**🔍 Search Tip:** {prompt.search_instruction}")
                    
                    with col2:
                        st.metric("Duration", f"{prompt.duration}s")
                        st.metric("Aspect Ratio", prompt.aspect_ratio)
                        if prompt.confidence_score:
                            confidence_pct = int(prompt.confidence_score * 100)
                            st.metric("AI Feasibility", f"{confidence_pct}%")
            
            # Export section
            st.header("📥 Export Results")
            
            csv_data, json_data = create_download_data(broll_prompts)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📊 Download CSV",
                    csv_data,
                    "broll_prompts.csv",
                    "text/csv",
                    help="Download as spreadsheet format"
                )
            
            with col2:
                st.download_button(
                    "📋 Download JSON",
                    json_data,
                    "broll_prompts.json",
                    "application/json",
                    help="Download as JSON format"
                )
            
            # Usage tips
            with st.expander("💡 How to Use These Prompts"):
                st.markdown("""
                **For AI Video Generation:**
                - Copy the generation prompts to tools like Runway, Pika, or Kling
                - Adjust duration and aspect ratio as needed
                - Use the confidence score to prioritize which scenes to generate first
                
                **For Stock Footage:**
                - Use the search instructions to find relevant clips
                - Look for footage that matches the emotional tone
                - Consider the timing and placement suggestions
                
                **For Video Editing:**
                - Insert B-roll clips after the specified script excerpts
                - Match the duration to your pacing needs
                - Ensure the emotional tone aligns with your narrative
                """)

if __name__ == "__main__":
    main()
