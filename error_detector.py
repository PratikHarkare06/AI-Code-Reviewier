import ast
from collections import defaultdict

class ErrorFinder(ast.NodeVisitor):
    """AST visitor to find unused variables in Python code."""
    
    def __init__(self):
        self.variables = defaultdict(dict)  # {scope: {var_name: line_number}}
        self.used_variables = set()  # Variables that are used
        self.scopes = [0]  # Stack of current scopes, start with global scope
        self.current_scope = 0
        self.unused_vars = []
        
    def visit_FunctionDef(self, node):
        """Visit function definition and create new scope."""
        self.scopes.append(self.current_scope)
        self.current_scope = len(self.scopes) - 1
        
        # Add function parameters to current scope
        for arg in node.args.args:
            self.variables[self.current_scope][arg.arg] = arg.lineno
        
        self.generic_visit(node)
        self.current_scope = self.scopes.pop()
        
    def visit_Name(self, node):
        """Visit variable names and track usage."""
        if isinstance(node.ctx, ast.Load):
            self.used_variables.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.variables[self.current_scope][node.id] = node.lineno
        
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        """Visit class definition and create new scope."""
        self.scopes.append(self.current_scope)
        self.current_scope = len(self.scopes) - 1
        self.generic_visit(node)
        self.current_scope = self.scopes.pop()
        
    def find_unused(self):
        """Find unused variables across all scopes."""
        all_defined = {}
        for scope_vars in self.variables.values():
            all_defined.update(scope_vars)
        
        # Find unused variables with line numbers
        unused_with_lines = []
        for var_name, line_num in all_defined.items():
            if var_name not in self.used_variables:
                # Filter out special variables and built-ins
                special_vars = {'_', '__name__', '__doc__', '__file__', '__package__'}
                if var_name not in special_vars and not var_name.startswith('__'):
                    unused_with_lines.append({
                        'name': var_name,
                        'line': line_num
                    })
        
        return unused_with_lines

class ImportFinder(ast.NodeVisitor):
    """AST visitor to find unused imports in Python code."""
    
    def __init__(self):
        self.imports = {}  # {import_name: {'full_name': str, 'line': int}}
        self.used_names = set()  # Names that are actually used
        self.unused_imports = []
        
    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = {
                'full_name': alias.name,
                'line': node.lineno
            }
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """Visit from-import statements."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            full_name = f"{node.module}.{alias.name}" if node.module else alias.name
            self.imports[name] = {
                'full_name': full_name,
                'line': node.lineno
            }
        self.generic_visit(node)
        
    def visit_Name(self, node):
        """Visit name usage and track used names."""
        if isinstance(node.ctx, ast.Load):
            # Check if this name matches any import
            if node.id in self.imports:
                self.used_names.add(node.id)
        self.generic_visit(node)
        
    def visit_Attribute(self, node):
        """Visit attribute access (e.g., module.function)."""
        if isinstance(node.value, ast.Name):
            module_name = node.value.id
            if module_name in self.imports:
                self.used_names.add(module_name)
        self.generic_visit(node)
        
    def find_unused_imports(self):
        """Find unused imports with line numbers."""
        unused = []
        for import_name, import_info in self.imports.items():
            if import_name not in self.used_names:
                unused.append({
                    'name': import_name,
                    'full_name': import_info['full_name'],
                    'line': import_info['line']
                })
        return unused

def detect_unused_variables(code_string):
    """
    Detect unused variables in Python code.
    
    Args:
        code_string (str): Python code to analyze
        
    Returns:
        list: List of unused variable names
    """
    try:
        tree = ast.parse(code_string)
        finder = ErrorFinder()
        finder.visit(tree)
        return finder.find_unused()
    except SyntaxError as e:
        return [f"Syntax Error: {str(e)}"]
    except Exception as e:
        return [f"Analysis Error: {str(e)}"]

def detect_unused_imports(code_string):
    """
    Detect unused imports in Python code.
    
    Args:
        code_string (str): Python code to analyze
        
    Returns:
        list: List of unused import information
    """
    try:
        tree = ast.parse(code_string)
        finder = ImportFinder()
        finder.visit(tree)
        return finder.find_unused_imports()
    except SyntaxError as e:
        return [{"name": f"Syntax Error", "full_name": str(e)}]
    except Exception as e:
        return [{"name": f"Analysis Error", "full_name": str(e)}]

def get_all_errors(code_string):
    """
    Get all detected errors (unused variables and imports).
    
    Args:
        code_string (str): Python code to analyze
        
    Returns:
        dict: Dictionary containing all detected errors
    """
    return {
        'unused_variables': detect_unused_variables(code_string),
        'unused_imports': detect_unused_imports(code_string)
    }

# Example usage
if __name__ == "__main__":
    test_code = '''
import os
import sys
from datetime import datetime
from collections import defaultdict

def example_function():
    x = 10
    y = 20
    z = 30  # This is unused
    result = x + y
    return result

# os and sys are unused imports
current_time = datetime.now()
my_dict = defaultdict(int)
'''
    
    errors = get_all_errors(test_code)
    print("Unused Variables:", errors['unused_variables'])
    print("Unused Imports:", errors['unused_imports'])
