import streamlit as st
from repo_mapper import RepoMapper
from code_analyzer import CodeAnalyzer
from doc_genie import DocGenie
import traceback
from datetime import datetime

st.set_page_config(
    page_title="Mwita's Code Genius",
    page_icon="💡",
    layout="wide"
)

if 'page' not in st.session_state:
    st.session_state.page = "🏠 Home"
if 'projects' not in st.session_state:
   
    st.session_state.projects = []


st.markdown("""
<style>
    /* Main app background and text */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        /* FIX: Use Streamlit's theme variable for background */
        background-color: var(--background-color);
        /* Text color will be handled by the theme */
    }
    
    /* Sidebar background */
    [data-testid="stSidebar"] {
        /* FIX: Use Streamlit's theme variable for secondary background */
        background-color: var(--secondary-background-color);
        border-right: 1px solid var(--gray-30); /* Light border for both themes */
    }

    /* Titles and Headers */
    h1, h2 {
        color: #00D1C1; /* Bright Cyan/Teal Accent */
    }

    /* --- New Unique Feature Cards (NOW THEME-AWARE) --- */
        
    /* Base Card Style */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        /* FIX: Use theme variables for card background and border */
        background-color: var(--secondary-background-color);
        border: 1px solid var(--gray-30);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Softer shadow */
        transition: all 0.3s ease;
    }

    /* Card Hover Effect */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:hover {
        border-color: #00D1C1; /* Use main accent color for hover */
        transform: translateY(-5px);
        box-shadow: 0 6px 10px rgba(0, 209, 193, 0.1);
    }
    
    /* Card Title Colors (Kept for uniqueness) */
    .card-title-1 { color: #3B7BBE; } /* Blue */
    .card-title-2 { color: #4CAF50; } /* Green */
    .card-title-3 { color: #9C27B0; } /* Purple */
    
    /* --- End of New Cards --- */

    /* Main "Generate" Button */
    [data-testid="stButton"] button {
        background-color: #00A99D;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    [data-testid="stButton"] button:hover {
        background-color: #00C1B2;
    }

    /* Spinner text */
    .stSpinner .st-emotion-cache-1lba0p {
         color: #00D1C1;
    }
    
    /* Divider */
    .stDivider {
        /* FIX: Use a theme-aware border color */
        background-color: var(--gray-30);
    }
    
    /* Logo in sidebar */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        border-radius: 10px;
        border: 2px solid #00D1C1;
        box-shadow: 0 0 15px rgba(0, 209, 193, 0.3);
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    
    st.image(
        "https://placehold.co/300x100/121212/00D1C1?text=Code+Genius&font=montserrat",
        use_container_width=True
    )

    st.title("💡 Navigation")
    
    page = st.radio(
        "Choose Action",
        ["🏠 Home", "🚀 Generate Documentation", "📈 Recent Projects"],
        label_visibility="collapsed",
        key="page_radio" 
    )
    
    st.divider()

def go_to_generate_docs():
    st.session_state.page_radio = "🚀 Generate Documentation"

if st.session_state.page_radio == "🏠 Home":
    st.title("🚀 Codebase Genius")
    st.subheader("by MWITA-CODE ARCHITECT")
    
    st.divider()
    
    st.header("Welcome to Codebase Genius! 🎉")
    st.write("Select 'Generate Documentation' from the navigation sidebar or click the button below to start.")
    
    st.button("Get Started →", type="primary", on_click=go_to_generate_docs)
    
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<h3 class='card-title-1'>🤖 Intelligent Analysis</h3>", unsafe_allow_html=True)
        st.write("Smart documentation with AI analysis of your code's structure and function.")
    with col2:

        st.markdown("<h3 class='card-title-2'>⚡️ Rapid Generation</h3>", unsafe_allow_html=True)
        st.write("Generate comprehensive docs in just a few minutes, not hours.")
    with col3:
        st.markdown("<h3 class='card-title-3'>🎯 Precise Parsing</h3>", unsafe_allow_html=True)
        st.write("Precise code analysis using `tree-sitter` for a deep, syntactical understanding.")

elif st.session_state.page_radio == "🚀 Generate Documentation":
    st.title("🚀 Generate New Documentation")
    st.write(
        "Enter a public GitHub repository URL. The agents will clone, analyze, and document the code."
    )

    github_url = st.text_input("GitHub Repository URL", placeholder="https.github.com/streamlit/streamlit-example")

    if st.button("Generate Documentation"):
        if "github.com" in github_url:
            with st.spinner("Genius at work... This may take a few minutes..."):
                current_repo_name = github_url.split('/')[-1].replace('.git', '')
                try:
            
                    if "GOOGLE_API_KEY" not in st.secrets:
                        st.error("GOOGLE_API_KEY not found. Please set it in .streamlit/secrets.toml")
                        st.stop()
                        
                    api_key = st.secrets["GOOGLE_API_KEY"]
                    doc_genie = DocGenie(api_key)
                    st.text("Step 1: DocGenie (LLM Agent) initialized.")

                    mapper = RepoMapper(github_url, doc_genie=doc_genie)
                   
                    clone_success = mapper.clone_repo()
                    
                    if clone_success:
                        st.text("Step 2: Repository cloning successful.")
                 
                        file_tree = mapper.build_file_tree()
                        st.text("Step 3: File tree generated.")
                        readme_summary = mapper.get_readme_summary()
                        st.text("Step 4: README summarized by AI.")
                        analyzer = CodeAnalyzer(mapper.local_repo_path)
                        analyzer.analyze_repository()
                        st.text("Step 5: Code analysis complete.")
                        mermaid_graph = analyzer.get_ccg_as_mermaid()
                        st.text("Step 6: Code Context Graph (CCG) generated.")

                        api_data = analyzer.get_api_reference_data()
                        st.text("Step 7: API reference data extracted.")
                        
                        final_docs = doc_genie.generate_final_docs(
                            repo_name=mapper.repo_name,
                            readme_summary=readme_summary,
                            file_tree=file_tree,
                            mermaid_graph=mermaid_graph,
                            api_data=api_data
                        )
                        st.text("Step 8: Final documentation generated by AI.")
                        
                        st.success("Documentation generated successfully!")
    
                        project_data = {
                            "Project Name": mapper.repo_name,
                            "Last Analyzed": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Status": "Success"
                        }
                        st.session_state.projects.insert(0, project_data)
                        st.session_state.projects = st.session_state.projects[:5]

                        st.markdown(final_docs)
                        
                        st.download_button(
                            label="Download docs.md",
                            data=final_docs,
                            file_name=f"{mapper.repo_name}_docs.md",
                            mime="text/markdown"
                        )
                    
                    else:
                        st.error("Error: Failed to clone the repository. Is the URL correct and the repository public?")
                    
                        project_data = {
                            "Project Name": current_repo_name,
                            "Last Analyzed": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Status": "Error (Clone Failed)"
                        }
                        st.session_state.projects.insert(0, project_data)
                        st.session_state.projects = st.session_state.projects[:5]
        
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    print("--- FULL TRACEBACK ---")
                    print(traceback.format_exc())
                    print("----------------------")

                    project_data = {
                        "Project Name": current_repo_name,
                        "Last Analyzed": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Status": f"Error (Runtime)"
                    }
                    st.session_state.projects.insert(0, project_data)
                    st.session_state.projects = st.session_state.projects[:5]
                   
        else:
            st.error("Please enter a valid GitHub URL.")

elif st.session_state.page_radio == "📈 Recent Projects":
    st.title("📈 Recent Projects")
    
    if not st.session_state.projects:
        st.info("You haven't analyzed any projects yet. Go to 'Generate Documentation' to get started!")
    else:
        st.write("Showing the last 5 projects you analyzed.")
        
        import pandas as pd
        df = pd.DataFrame(st.session_state.projects)
        st.dataframe(df, use_container_width=True)