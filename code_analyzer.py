import os
from tree_sitter import Parser
from tree_sitter_languages import get_language
import networkx as nx

class CodeAnalyzer:
    """
    Parses all Python files in a repository and builds a 
    Code Context Graph (CCG).
    """
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.parser = Parser()
        
        try:
            self.PYTHON_LANGUAGE = get_language('python')
          
            self.parser.set_language(self.PYTHON_LANGUAGE)
         

        except Exception as e:
            print(f"Error loading tree-sitter Python grammar: {e}")
            print("Please ensure 'tree-sitter-languages' and 'tree-sitter-python' are installed.")
            print(f"Full traceback: {e}")
            raise Exception("Python parser for tree-sitter is not loaded.")

        self.ccg = nx.DiGraph() 
        self.query_cache = {} 

    def _get_query(self, query_str):
        """Compiles and caches a tree-sitter query."""
        if query_str not in self.query_cache:
           
            self.query_cache[query_str] = self.PYTHON_LANGUAGE.query(query_str)
        return self.query_cache[query_str]

    def analyze_repository(self):
        """Walks the repo and analyzes each Python file."""
        print("Starting repository analysis...")
        for root, _, files in os.walk(self.repo_path):
            if '.git' in root or 'venv' in root:
                continue
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.repo_path)
                    
                    file_node_id = f"file:{relative_path}"
                    self.ccg.add_node(file_node_id, type='file')
                    
                    self._parse_file(file_path, file_node_id)
        print("Repository analysis complete.")

    def _parse_file(self, file_path, file_node_id):
        """Parses a single file to find functions, classes, and calls."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                code = f.read()
                tree = self.parser.parse(bytes(code, "utf8"))
                
                func_query_str = "(function_definition name: (identifier) @func.name)"
                func_query = self._get_query(func_query_str)
                for capture, _ in func_query.captures(tree.root_node):
                    func_name = capture.text.decode('utf8')
                    func_node_id = f"func:{file_node_id}:{func_name}"
                    self.ccg.add_node(func_node_id, type='function')
                    self.ccg.add_edge(file_node_id, func_node_id, type='defines')

                class_query_str = "(class_definition name: (identifier) @class.name)"
                class_query = self._get_query(class_query_str)
                for capture, _ in class_query.captures(tree.root_node):
                    class_name = capture.text.decode('utf8')
                    class_node_id = f"class:{file_node_id}:{class_name}"
                    self.ccg.add_node(class_node_id, type='class')
                    self.ccg.add_edge(file_node_id, class_node_id, type='defines')

            except Exception as e:
                print(f"Warning: Could not parse {file_path}. Error: {e}")

    def get_ccg_as_mermaid(self):
        """Converts the NetworkX graph into a Mermaid.js string."""
        mermaid_str = "graph TD;\n"
        for node, data in self.ccg.nodes(data=True):
            node_type = data.get('type')
            
            clean_node_id = node.replace(':', '_').replace('/', '_').replace('.', '_').replace('\\', '_')

            if node_type == 'file':
                label = f"[{os.path.basename(node)}]"
                mermaid_str += f'    {clean_node_id}(("{label}"))\n'
            elif node_type == 'function':
                label = f"{node.split(':')[-1]}()"
                mermaid_str += f'    {clean_node_id}[/"{label}"/]\n'
            elif node_type == 'class':
                label = f"{node.split(':')[-1]}"
                mermaid_str += f'    {clean_node_id}["{label}"]\n'

        for u, v, data in self.ccg.edges(data=True):
            clean_u = u.replace(':', '_').replace('/', '_').replace('.', '_').replace('\\', '_')
            clean_v = v.replace(':', '_').replace('/', '_').replace('.', '_').replace('\\', '_')
            edge_type = data.get('type')
            
            if edge_type == 'defines':
                mermaid_str += f"    {clean_u} -- defines --> {clean_v}\n"
        
        return mermaid_str

    def get_api_reference_data(self):
        """
        Extracts all function and class names from the CCG
        to be used by the LLM for an API reference.
        """
        api_data = {
            "files": {},
            "classes": [],
            "functions": []
        }
    
        for node, data in self.ccg.nodes(data=True):
            node_type = data.get('type')
            
            if node_type == 'function':
               
                parts = node.split(':', 2)
                if len(parts) == 3:
                    file_path = parts[1]
                    func_name = parts[2]
                    if file_path not in api_data["files"]:
                        api_data["files"][file_path] = {"functions": [], "classes": []}
                    api_data["files"][file_path]["functions"].append(f"{func_name}()")
                    
            elif node_type == 'class':
                
                parts = node.split(':', 2)
                if len(parts) == 3:
                    file_path = parts[1]
                    class_name = parts[2]
                    if file_path not in api_data["files"]:
                        api_data["files"][file_path] = {"functions": [], "classes": []}
                    api_data["files"][file_path]["classes"].append(class_name)

        formatted_string = "### API Reference Data\n\n"
        for file_path, contents in api_data["files"].items():
            if contents["classes"] or contents["functions"]:
                formatted_string += f"**File: `{file_path}`**\n"
                if contents["classes"]:
                    formatted_string += "  - Classes: " + ", ".join(contents["classes"]) + "\n"
                if contents["functions"]:
                    formatted_string += "  - Functions: " + ", ".join(contents["functions"]) + "\n"
                formatted_string += "\n"
                
        if not api_data["files"]:
            return "No functions or classes were found by the parser."
            
        return formatted_string