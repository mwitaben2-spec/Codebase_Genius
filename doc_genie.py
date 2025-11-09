import streamlit as st
import google.generativeai as genai

class DocGenie:
    """
    The agent responsible for all LLM-based generation.
    It summarizes READMEs and synthesizes the final documentation.
    """
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Google API Key not found. Please set it in .streamlit/secrets.toml")
        
        try:
            genai.configure(api_key=api_key)
        
            self.model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            print("DocGenie initialized with Gemini model.")
        except Exception as e:
            raise RuntimeError(f"Failed to configure Gemini model: {e}")

    def _generate_content(self, prompt, is_json=False):
        """Helper function to call the Gemini API."""
        try:
           
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating content from Gemini: {e}")

            return f"Error from LLM: {e}"

    def summarize_readme(self, readme_content):
        """
        Summarizes the README.md content.
        """
        if not readme_content or readme_content.strip() == "":
            return "README content was empty or not provided."
            
        prompt = f"""
        You are a technical writer. Summarize the following README.md file.
        Focus on the project's main purpose, how to install it, and how to run it.
        Keep the summary to one or two paragraphs.

        README Content:
        ---
        {readme_content}
        ---
        """
        
        print("Sending README to Gemini for summarization...")
        summary = self._generate_content(prompt)
        print("README summary received.")
        return summary

    def generate_final_docs(self, repo_name, readme_summary, file_tree, mermaid_graph, api_data=None):
        """
        Generates the complete, final markdown documentation.
        """
        
       
        api_section_prompt = ""
        if api_data:
            api_section_prompt = f"""
        4.  **API Reference:** A list of all functions and classes found in the code. 
            Use this data to write a brief "API Reference" section. 
            **Do not just paste the data**, describe it. 
            For example: "The file `utils.py` contains the helper function `do_thing()`."
        """
        
        api_data_prompt = ""
        if api_data:
            api_data_prompt = f"""
        ---
        **API Reference Data:**
        {api_data}
        """
        
        prompt = f"""
        You are 'Codebase Genius', an AI documentation writer.
        Your job is to generate a complete, well-organized markdown document
        for a software repository.

        You have been given the following pieces of information:
        1.  **Repo Name:** {repo_name}
        2.  **README Summary:** {readme_summary}
        3.  **File Tree:** A map of all files in the repo.
        4.  **Code Context Graph (CCG):** A Mermaid diagram showing files, functions, and classes.

        Please assemble this information into a single, high-quality `docs.md` file.
        Use good markdown formatting. Be clear and professional.
        
        The final document should have these sections:
        1.  **Overview:** Start with the README summary.
        2.  **Repository Map:** Show the complete file tree.
        3.  **Code Context Graph:** Show the Mermaid diagram.
        {api_section_prompt}

        Here is the data:
        
        ---
        **README Summary:**
        {readme_summary}
        
        ---
        **File Tree:**
        ```
        {file_tree}
        ```

        ---
        **Code Context Graph (CCG):**
        ```mermaid
        {mermaid_graph}
        ```
        {api_data_prompt}
        ---
        
        Now, generate the complete markdown document.
        Start with the title `# Documentation for {repo_name}`.
        """
        
        print("Sending all context to Gemini for final documentation...")
        final_doc_content = self._generate_content(prompt)
        print("Final documentation received.")
        return final_doc_content