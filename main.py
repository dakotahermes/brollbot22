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
from utils.analytics import AnalyticsUtils, display_script_analysis
from utils.workflow import WorkflowManager, PromptOptimizer, ProjectManager, TemplateManager

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
    
    # Custom CSS for AdClass branding
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #22c55e 0%, #14b8a6 100%);
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
        }
        .main-title {
            color: white;
            font-size: 2.5rem;
            font-weight: bold;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .main-subtitle {
            color: white;
            font-size: 1.2rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        .adclass-badge {
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            color: white;
            font-weight: 600;
            display: inline-block;
            margin-top: 1rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #22c55e;
            margin: 0.5rem 0;
        }
        .conversion-tip {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #f59e0b;
            margin: 1rem 0;
        }
        .stButton > button {
            background: linear-gradient(135deg, #22c55e 0%, #14b8a6 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        .stSelectbox > div > div > div {
            background-color: #f8fafc;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    WorkflowManager.initialize_session_state()
    
    # Initialize OpenAI client
    client = initialize_openai_client()
    agent = create_agent(client)
    
    # Header with AdClass branding
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎬 AdClass B-Roll Generator</h1>
        <p class="main-subtitle">Transform your ad scripts into high-converting B-roll that stops scrolling</p>
        <div class="adclass-badge">Powered by AdClass - Amplifying the World's Greatest Businesses</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with settings and workflow management
    with st.sidebar:
        st.markdown("### ⚙️ Campaign Settings")
        duration = st.slider("Default Duration (seconds)", 1, 30, config.DEFAULT_DURATION, 
                            help="Optimized for social media - shorter clips perform better")
        aspect_ratio = st.selectbox("Aspect Ratio", ["9:16", "16:9", "1:1", "4:5"], index=0,
                                  help="9:16 recommended for mobile-first platforms")
        
        # Project management
        current_project = ProjectManager.create_project_interface()
        
        # Workflow history
        st.markdown("### 📋 Campaign History")
        loaded_workflow = WorkflowManager.display_workflow_history()
        
        # Project contents
        loaded_project_data = ProjectManager.display_project_contents(current_project)
        
        # Export all workflows
        if st.session_state.workflow_history:
            export_data = WorkflowManager.export_all_workflows()
            if export_data:
                st.download_button(
                    "📦 Export All Campaigns",
                    export_data,
                    "adclass_campaigns.json",
                    "application/json"
                )
        
        st.markdown("### 🎯 About AdClass")
        st.markdown("""
        **Our Mission:** To amplify businesses through advertising so that the greatest companies and people in the world can be seen.
        
        **Track Record:**
        - $323M+ revenue generated
        - $85M+ ads managed  
        - 3.8x average ROAS
        
        **This Tool:** Creates B-roll specifically designed for direct response ads that drive clicks and conversions.
        """)
        
        st.markdown("---")
        st.markdown("**Need expert ad management?**")
        st.markdown("[📞 Book a Strategy Call](https://www.adclass.com)")
    
    # Check for loaded workflow data
    if loaded_workflow:
        st.info("✅ Loaded campaign from history!")
    
    if loaded_project_data:
        st.info(f"✅ Loaded campaign from project: {current_project}")
    
    # Main input section
    st.markdown("## 📝 Ad Script Input")
    
    # Template selection
    template_data = TemplateManager.display_templates()
    
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
        
        # Display script analysis
        if char_count >= config.MIN_SCRIPT_LENGTH:
            script_analysis = display_script_analysis(script_input)
    
    # Tone and format selection
    col1, col2 = st.columns(2)
    
    with col1:
        default_tone = template_data['tone'] if template_data else "hook"
        tone = st.selectbox(
            "Select Marketing Psychology:",
            ["hook", "problem", "solution", "social_proof", "urgency", "transformation", "curiosity", "authority"],
            index=["hook", "problem", "solution", "social_proof", "urgency", "transformation", "curiosity", "authority"].index(default_tone),
            help="Choose the psychological trigger that best matches your ad strategy"
        )
    
    with col2:
        default_format = template_data['format'] if template_data else "ugc_style"
        format_type = st.selectbox(
            "Select Ad Format:",
            ["ugc_style", "testimonial", "demo_style", "influencer_style", "news_style", "comparison"],
            index=["ugc_style", "testimonial", "demo_style", "influencer_style", "news_style", "comparison"].index(default_format),
            help="Choose the ad format style for your campaign"
        )
    
    # Conversion tips
    st.markdown("""
    <div class="conversion-tip">
        <strong>🎯 AdClass Pro Tip:</strong> For maximum conversions, use "hook" psychology with "ugc_style" format. 
        This combination creates pattern interrupts that stop scrolling while maintaining authenticity.
    </div>
    """, unsafe_allow_html=True)
    
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
            with st.spinner("🔍 Analyzing your script with AdClass's proven methodology..."):
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
            
            # Save workflow to history
            analytics = AnalyticsUtils.analyze_prompts(broll_prompts)
            WorkflowManager.save_workflow(ad_input, broll_prompts, analytics)
            
            # Save to current project
            ProjectManager.save_to_project(current_project, {
                'script_input': ad_input.dict(),
                'prompts': [p.dict() for p in broll_prompts],
                'analytics': analytics
            })
            
            # Display results
            st.success(f"✅ Generated {len(broll_prompts)} conversion-optimized B-roll suggestions!")
            
            # Generate and display analytics
            AnalyticsUtils.display_analytics_dashboard(analytics)
            
            # Display insights
            insights = AnalyticsUtils.generate_insights(analytics)
            if insights:
                st.markdown("## 💡 AdClass Expert Insights")
                for insight in insights:
                    st.info(insight)
            
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
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("Duration", f"{prompt.duration}s")
                        st.metric("Aspect Ratio", prompt.aspect_ratio)
                        if prompt.confidence_score:
                            confidence_pct = int(prompt.confidence_score * 100)
                            st.metric("AI Feasibility", f"{confidence_pct}%")
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # Prompt optimization suggestions
            suggestions = PromptOptimizer.suggest_prompt_improvements(broll_prompts)
            if suggestions:
                st.markdown("## 🔧 Optimization Recommendations")
                for suggestion in suggestions:
                    st.info(suggestion)
            
            # Advanced features toggle
            show_advanced = st.checkbox("🛠️ Show Advanced Customization", value=False)
            
            if show_advanced:
                # Prompt customization interface
                customized_prompts = PromptOptimizer.customize_prompts_interface(broll_prompts)
                
                if st.button("📥 Apply Customizations"):
                    broll_prompts = customized_prompts
                    st.success("✅ Updated prompts with your customizations!")
            
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