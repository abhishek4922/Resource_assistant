"""
AI Operations Assistant - Main Streamlit Application
Multi-agent system for company intelligence and AI use-case discovery
"""
import streamlit as st
import json
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.verifier_agent import VerifierAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Operations Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar collapsed by default
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.2rem;
    }
    .use-case-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .resource-section {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-card p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .loader-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.85);
        z-index: 9998;
        backdrop-filter: blur(5px);
    }
    .loader-container {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        width: 60%;
        max-width: 800px;
        text-align: center;
        z-index: 9999;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    .loader-spinner {
        width: 60px;
        height: 60px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1.5rem auto;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .progress-message {
        font-size: 1.3rem;
        color: #4a5568;
        font-weight: 500;
        margin: 0.5rem 0;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .info-banner {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'progress_messages' not in st.session_state:
        st.session_state.progress_messages = []
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'result_id' not in st.session_state:
        st.session_state.result_id = 0


def progress_callback(message: str):
    """Callback for progress updates"""
    st.session_state.progress_messages.append(message)
    st.session_state.current_step += 1


def analyze_company(company_name: str):
    """
    Main analysis function that orchestrates all agents
    
    Args:
        company_name: Name of the company to analyze
    """
    st.session_state.processing = True
    st.session_state.progress_messages = []
    st.session_state.current_step = 0
    
    try:
        # Initialize agents
        planner = PlannerAgent()
        executor = ExecutorAgent(progress_callback=progress_callback)
        verifier = VerifierAgent()
        
        # Step 1: Create plan
        progress_callback("📋 Creating execution plan...")
        plan = planner.create_plan(company_name)
        
        # Step 2: Execute plan
        progress_callback("⚙️ Executing plan...")
        results = executor.execute_plan(plan)
        
        # Step 3: Verify and finalize
        progress_callback("✅ Verifying results...")
        final_results = verifier.verify_and_finalize(results)
        
        progress_callback("🎉 Analysis complete!")
        
        st.session_state.results = final_results
        st.session_state.result_id += 1  # Increment to force UI update
        
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        st.exception(e)
    finally:
        st.session_state.processing = False


def display_results(results: dict):
    """
    Display the analysis results in a structured format
    
    Args:
        results: Analysis results from the agents
    """
    # Force a unique key for this entire result display
    result_key = f"{results['company']}_{st.session_state.result_id}"
    
    # Company header
    st.markdown(f"<h1 class='main-header'>{results['company']}</h1>", unsafe_allow_html=True)
    
    # Add a small indicator showing this is fresh data
    st.caption(f"Analysis ID: {st.session_state.result_id} | Company: {results['company']}")
    
    # Company summary
    st.markdown("### 📊 Company Overview")
    st.info(results['company_summary'])
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>{len(results['ai_use_cases'])}</h3>
            <p>AI Use Cases</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_resources = sum(
            len(uc['resources']['arxiv']) + 
            len(uc['resources']['huggingface']) + 
            len(uc['resources']['kaggle']) + 
            len(uc['resources']['github'])
            for uc in results['ai_use_cases']
        )
        st.markdown(f"""
        <div class='metric-card'>
            <h3>{total_resources}</h3>
            <p>Total Resources</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        platforms = 4  # arXiv, HuggingFace, Kaggle, GitHub
        st.markdown(f"""
        <div class='metric-card'>
            <h3>{platforms}</h3>
            <p>Platforms Searched</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # AI Use Cases
    st.markdown("### 💡 AI Use Cases & Resources")
    
    # Add unique identifier for this result set
    company_key = results['company'].replace(" ", "_").lower()
    
    for idx, use_case in enumerate(results['ai_use_cases'], 1):
        # Use unique key based on company and index to force refresh
        expander_key = f"{company_key}_usecase_{idx}_{st.session_state.result_id}"
        with st.expander(f"**{idx}. {use_case['use_case']}**", expanded=idx == 1):
            st.markdown(f"**Description:** {use_case['description']}")
            
            # Resources tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📚 arXiv", "🤗 Hugging Face", "📊 Kaggle", "💻 GitHub"])
            
            with tab1:
                st.markdown("#### Academic Papers")
                if use_case['resources']['arxiv']:
                    for paper in use_case['resources']['arxiv']:
                        st.markdown(f"- [{paper['title']}]({paper['url']})")
                else:
                    st.info("No arXiv papers found")
            
            with tab2:
                st.markdown("#### Models & Datasets")
                if use_case['resources']['huggingface']:
                    for item in use_case['resources']['huggingface']:
                        st.markdown(f"- [{item['name']}]({item['url']})")
                else:
                    st.info("No Hugging Face resources found")
            
            with tab3:
                st.markdown("#### Datasets & Notebooks")
                if use_case['resources']['kaggle']:
                    for item in use_case['resources']['kaggle']:
                        st.markdown(f"- [{item['title']}]({item['url']})")
                else:
                    st.info("No Kaggle resources found")
            
            with tab4:
                st.markdown("#### Repositories")
                if use_case['resources']['github']:
                    for repo in use_case['resources']['github']:
                        stars = f"⭐ {repo['stars']}" if repo['stars'] > 0 else ""
                        st.markdown(f"- [{repo['name']}]({repo['url']}) {stars}")
                else:
                    st.info("No GitHub repositories found")
    
    # Download results
    st.markdown("---")
    st.markdown("### 💾 Export Results")
    
    col1, col2 = st.columns(2)
    with col1:
        json_str = json.dumps(results, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"{results['company']}_ai_analysis.json",
            mime="application/json"
        )
    
    with col2:
        # Create a simple text report
        text_report = f"""AI OPERATIONS ASSISTANT - ANALYSIS REPORT
{'=' * 60}

Company: {results['company']}

Company Summary:
{results['company_summary']}

{'=' * 60}
AI USE CASES
{'=' * 60}

"""
        for idx, uc in enumerate(results['ai_use_cases'], 1):
            text_report += f"\n{idx}. {uc['use_case']}\n"
            text_report += f"   {uc['description']}\n\n"
            text_report += f"   Resources:\n"
            text_report += f"   - arXiv Papers: {len(uc['resources']['arxiv'])}\n"
            text_report += f"   - Hugging Face: {len(uc['resources']['huggingface'])}\n"
            text_report += f"   - Kaggle: {len(uc['resources']['kaggle'])}\n"
            text_report += f"   - GitHub Repos: {len(uc['resources']['github'])}\n"
        
        st.download_button(
            label="📄 Download Report",
            data=text_report,
            file_name=f"{results['company']}_ai_analysis.txt",
            mime="text/plain"
        )


def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown("<h1 class='main-header'>🤖 AI Operations Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Company Intelligence & AI Use-Case Discovery Agent</p>", unsafe_allow_html=True)
    
    # Info banner
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.markdown("""
        <div class='info-banner'>
            <strong>⚠️ Configuration Required:</strong> Please add your GROQ_API_KEY to the .env file. 
            Get your free API key from <a href='https://console.groq.com/' target='_blank'>console.groq.com</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("### 🎯 Analyze a Company")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        company_name = st.text_input(
            "Enter company name:",
            placeholder="e.g., Swiggy, Amazon, Trulymadly, Netflix",
            help="Enter the name of any company to analyze",
            label_visibility="collapsed"
        )
    
    with col2:
        analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    
    # Example companies
    st.markdown("**Quick examples:**")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Swiggy", use_container_width=True):
            st.session_state.results = None  # Clear previous results
            company_name = "Swiggy"
            analyze_button = True
    with col2:
        if st.button("Zomato", use_container_width=True):
            st.session_state.results = None  # Clear previous results
            company_name = "Zomato"
            analyze_button = True
    with col3:
        if st.button("Netflix", use_container_width=True):
            st.session_state.results = None  # Clear previous results
            company_name = "Netflix"
            analyze_button = True
    with col4:
        if st.button("Trulymadly", use_container_width=True):
            st.session_state.results = None  # Clear previous results
            company_name = "Trulymadly"
            analyze_button = True
    with col5:
        if st.button("Amazon", use_container_width=True):
            st.session_state.results = None  # Clear previous results
            company_name = "Amazon"
            analyze_button = True
    
    # Process analysis
    if analyze_button and company_name:
        if not os.getenv("GROQ_API_KEY"):
            st.error("⚠️ Please configure your GROQ_API_KEY in the .env file")
            st.info("1. Copy `.env.example` to `.env`\n2. Add your Groq API key\n3. Restart the application")
        else:
            # Clear previous results before starting new analysis
            st.session_state.results = None
            st.session_state.current_company = company_name
            
            with st.spinner(f"🔍 Analyzing {company_name}..."):
                analyze_company(company_name)
            
            # Force rerun to display new results
            if st.session_state.results and not st.session_state.processing:
                st.rerun()
    
    # Show animated progress loader
    if st.session_state.processing:
        # Let's build the messages HTML
        messages_html = ""
        if st.session_state.progress_messages:
            for msg in st.session_state.progress_messages[-1:]:  # Show only the very latest message for cleaner look
                messages_html += f"<p class='progress-message'>{msg}</p>"
        
        # Render the full modal with updated progress
        total_steps = 15
        progress_pct = int(min(st.session_state.current_step / total_steps, 1.0) * 100)
        
        st.markdown(f"""
            <style>
                /* Force hide the default progress bar inside the main flow if it appears */
                .stProgress {{ display: none; }} 
            </style>
            <script>
                // Optional: Scroll to top
                window.scrollTo(0, 0);
            </script>
            <div class="loader-overlay"></div>
            <div class="loader-container">
                <div class="loader-spinner"></div>
                <h2 style="color: #2d3748; margin-bottom: 1rem;">Analyzing {st.session_state.get('current_company', 'Company')}</h2>
                
                <div style="width: 100%; background-color: #e2e8f0; border-radius: 10px; height: 10px; margin: 1.5rem 0; overflow: hidden;">
                    <div style="width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); transition: width 0.5s ease;"></div>
                </div>
                
                <div style="min-height: 60px;">
                    {messages_html}
                </div>
                
                <p style="color: #a0aec0; font-size: 0.9rem; margin-top: 2rem;">
                    Please wait while our AI agents research, plan, and verify results...
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Auto-refresh while processing
        time.sleep(0.5)
        st.rerun()
    
    
    # Display results
    if st.session_state.results and not st.session_state.processing:
        st.markdown("---")
        
        # Add a "New Analysis" button at the top of results
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 New Analysis", type="secondary", use_container_width=True):
                st.session_state.results = None
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        display_results(st.session_state.results)


if __name__ == "__main__":
    main()
