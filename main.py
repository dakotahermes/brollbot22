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
# Temporarily comment out utils imports until we create the files
# from utils.analytics import AnalyticsUtils, display_script_analysis
# from utils.workflow import WorkflowManager, PromptOptimizer, ProjectManager, TemplateManager

# Load environment variables
load_dotenv()

# Initialize configuration
config = Config.from_env()

def initialize_openai_client() -> OpenAI:
    """Initialize and validate OpenAI client"""
    # Try to get API key from Streamlit secrets first, then environment
    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except (AttributeError, FileNotFoundError):
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        st.error("⚠️ OpenAI API key not found. Please add your API key to Streamlit secrets or environment variables.")
        st.info("For Streamlit Cloud deployment, add your API key in the app settings under 'Secrets'.")
        st.stop()
    
    try:
        client = OpenAI(api_key=api_key)
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
    """Main Streamlit application - AdClass Branded"""
    st.set_page_config(
        page_title="AdClass B-Roll Generator",
        page_icon="🎬",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Simplified CSS for AdClass branding (faster loading)
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #22c55e, #14b8a6);
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .main-title {
            color: white;
            font-size: 2rem;
            font-weight: bold;
            margin: 0;
        }
        .main-subtitle {
            color: white;
            font-size: 1rem;
            margin: 0.5rem 0 0 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state (simplified for now)
    if 'workflow_history' not in st.session_state:
        st.session_state.workflow_history = []
    
    # Initialize OpenAI client
    client = initialize_openai_client()
    agent = create_agent(client)
    
    # Simplified header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎬 AdClass B-Roll Generator</h1>
        <p class="main-subtitle">Transform ad scripts into high-converting B-roll</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with settings and workflow management
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        duration = st.slider("Duration (seconds)", 1, 30, config.DEFAULT_DURATION)
        aspect_ratio = st.selectbox("Aspect Ratio", ["9:16", "16:9", "1:1", "4:5"], index=0)
        
        # Simplified sidebar for now
        # Project management
        # current_project = ProjectManager.create_project_interface()
        
        # Workflow history
        # st.markdown("### 📋 Campaign History")
        # loaded_workflow = WorkflowManager.display_workflow_history()
        
        # Project contents
        # loaded_project_data = ProjectManager.display_project_contents(current_project)
        
        # Export all workflows
        # if st.session_state.workflow_history:
        #     export_data = WorkflowManager.export_all_workflows()
        #     if export_data:
        #         st.download_button(
        #             "📦 Export All Campaigns",
        #             export_data,
        #             "adclass_campaigns.json",
        #             "application/json"
        #         )
        
        st.markdown("### 🎯 About AdClass")
        st.markdown("**Mission:** Amplify businesses through advertising")
        st.markdown("**Track Record:** $323M+ revenue, 3.8x avg ROAS")
        st.markdown("[📞 Book Strategy Call](https://www.adclass.com)")
    
    # Check for loaded workflow data (simplified)
    # if loaded_workflow:
    #     st.info("✅ Loaded campaign from history!")
    
    # if loaded_project_data:
    #     st.info(f"✅ Loaded campaign from project: {current_project}")
    
    # Main input section
    st.markdown("## 📝 Ad Script Input")
    
    # Template selection (simplified for now)
    # template_data = TemplateManager.display_templates()
    template_data = None
    
    # Script input with potential template pre-fill
    default_script = template_data['script'] if template_data else ""
    script_input = st.text_area(
        "Paste your ad script here:",
        value=default_script,
        placeholder="Enter your direct response ad script here (minimum 10 characters)...",
        help="Paste the full script for your social media ad campaign",
        height=150
    )
    
    # Show character count
    if script_input:
        char_count = len(script_input)
        color = "green" if char_count >= config.MIN_SCRIPT_LENGTH else "orange"
        st.markdown(f"<span style='color: {color}'>Characters: {char_count}</span>", unsafe_allow_html=True)
        
        # Display script analysis (simplified for now)
        # if char_count >= config.MIN_SCRIPT_LENGTH:
        #     script_analysis = display_script_analysis(script_input)
    
    # Tone and format selection (using original options for now)
    col1, col2 = st.columns(2)
    
    with col1:
        tone = st.selectbox(
            "Marketing Psychology:",
            ["inspiring", "urgent", "calm", "funny", "serious", "emotional", "uplifting", "mysterious"],
            index=0
        )
    
    with col2:
        format_type = st.selectbox(
            "Ad Format:",
            ["UGC", "talking_head", "testimonial"],
            index=0
        )
    
    # Pro tip (simplified)
    st.info("🎯 **AdClass Pro Tip:** Use 'hook' + 'ugc_style' for maximum conversions")
    
    # Generate button
    if st.button("🚀 Generate High-Converting B-Roll", type="primary", use_container_width=True):
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
            with st.spinner("🔍 Analyzing your script..."):
                # Step 1: Parse script into scene beats
                scene_beats_data = agent.parse_script(ad_input.script, ad_input.tone, ad_input.format)
                
                if scene_beats_data is None:
                    return
                
                if not scene_beats_data:
                    st.warning("No suitable scenes found. Try adjusting your psychology trigger or format.")
                    return
                
                # Step 2: Generate B-roll prompts
                broll_prompts = agent.generate_prompts(scene_beats_data, duration, aspect_ratio)
                
                if not broll_prompts:
                    st.warning("No high-converting B-roll prompts could be generated. Consider simplifying your script for better AI video generation.")
                    return
            
            # Save workflow to history (simplified)
            # analytics = AnalyticsUtils.analyze_prompts(broll_prompts)
            # WorkflowManager.save_workflow(ad_input, broll_prompts, analytics)
            
            # Save to current project (simplified)
            # ProjectManager.save_to_project(current_project, {
            #     'script_input': ad_input.dict(),
            #     'prompts': [p.dict() for p in broll_prompts],
            #     'analytics': analytics
            # })
            
            # Display results
            st.success(f"✅ Generated {len(broll_prompts)} conversion-optimized B-roll suggestions!")
            
            # Generate and display analytics (simplified for now)
            # AnalyticsUtils.display_analytics_dashboard(analytics)
            
            # Display insights (simplified for now)
            # insights = AnalyticsUtils.generate_insights(analytics)
            # if insights:
            #     st.markdown("## 💡 AdClass Expert Insights")
            #     for insight in insights:
            #         st.info(insight)
            
            # Results section
            st.markdown("## 🎥 Your High-Converting B-Roll Prompts")
            
            for i, prompt in enumerate(broll_prompts, 1):
                with st.expander(f"Scene {i}: {prompt.insert_after[:50]}..."):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**📍 Insert After:** _{prompt.insert_after}_")
                        st.markdown(f"**🎬 AI Generation Prompt:**")
                        st.code(prompt.prompt)
                        st.markdown(f"**🔍 Stock Footage Search:** {prompt.search_instruction}")
                    
                    with col2:
                        st.metric("Duration", f"{prompt.duration}s")
                        st.metric("Aspect Ratio", prompt.aspect_ratio)
                        if prompt.confidence_score:
                            confidence_pct = int(prompt.confidence_score * 100)
                            st.metric("AI Feasibility", f"{confidence_pct}%")
            
            # Prompt optimization suggestions (simplified for now)
            # suggestions = PromptOptimizer.suggest_prompt_improvements(broll_prompts)
            # if suggestions:
            #     st.markdown("## 🔧 Optimization Recommendations")
            #     for suggestion in suggestions:
            #         st.info(suggestion)
            
            # Advanced features toggle (simplified for now)
            # show_advanced = st.checkbox("🛠️ Show Advanced Customization", value=False)
            
            # if show_advanced:
            #     # Prompt customization interface
            #     customized_prompts = PromptOptimizer.customize_prompts_interface(broll_prompts)
                
            #     if st.button("📥 Apply Customizations"):
            #         broll_prompts = customized_prompts
            #         st.success("✅ Updated prompts with your customizations!")
            
            # Export section
            st.markdown("## 📥 Export Your Campaign Assets")
            
            csv_data, json_data = create_download_data(broll_prompts)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📊 Download CSV for Spreadsheets",
                    csv_data,
                    "adclass_broll_prompts.csv",
                    "text/csv",
                    help="Perfect for sharing with your video production team"
                )
            
            with col2:
                st.download_button(
                    "📋 Download JSON for Developers",
                    json_data,
                    "adclass_broll_prompts.json",
                    "application/json",
                    help="Structured data for technical integrations"
                )
            
            # Usage tips
            with st.expander("💡 How to Use These AdClass-Optimized Prompts"):
                st.markdown("""
                **For AI Video Generation (Runway, Pika, Kling):**
                - Copy the AI generation prompts directly into your preferred tool
                - Use the confidence score to prioritize which scenes to generate first
                - Start with 9:16 aspect ratio for mobile-first campaigns
                
                **For Stock Footage:**
                - Use the search instructions to find relevant clips on Shutterstock, Getty, etc.
                - Look for footage that matches the specified emotional trigger
                - Prioritize mobile-optimized, high-energy content
                
                **For Video Editing:**
                - Insert B-roll clips after the specified script excerpts
                - Keep clips short (3-5 seconds) for social media
                - Ensure emotional tone aligns with your conversion goals
                
                **AdClass Pro Tips:**
                - Test multiple versions of high-confidence scenes
                - A/B test different emotional triggers for your audience
                - Always optimize for sound-off viewing on mobile
                
                **Need Help Scaling Your Campaigns?**
                [Book a strategy call with AdClass](https://www.adclass.com) to see how we can help you achieve 3.8x+ ROAS.
                """)

if __name__ == "__main__":
    main()