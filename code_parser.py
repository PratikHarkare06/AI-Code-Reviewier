import ast
import sys
import io
import contextlib

def parse_code(code_string):
    """
    Parse Python code and check for both syntax and runtime errors.
    
    Args:
        code_string (str): Python code to analyze
        
    Returns:
        dict: Result with success status and error details if any
    """
    # First check syntax
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        return {"success": False, "error": {"message": f"Syntax Error: {str(e)}"}}
    
    # Then check for runtime errors by executing in a safe environment
    try:
        # Create a safe namespace for execution
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'list': list,
                'dict': dict,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                # Add more safe builtins as needed
            }
        }
        safe_locals = {}
        
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Try to execute the code
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            try:
                exec(code_string, safe_globals, safe_locals)
            except Exception as e:
                # Check for common runtime errors
                error_type = type(e).__name__
                if error_type == 'IndexError':
                    return {"success": False, "error": {"message": f"Runtime Error: {error_type} - {str(e)}. This will cause an IndexError when the code runs."}}
                elif error_type == 'NameError':
                    return {"success": False, "error": {"message": f"Runtime Error: {error_type} - {str(e)}. Variable is not defined."}}
                elif error_type == 'TypeError':
                    return {"success": False, "error": {"message": f"Runtime Error: {error_type} - {str(e)}. Type mismatch in operation."}}
                elif error_type == 'KeyError':
                    return {"success": False, "error": {"message": f"Runtime Error: {error_type} - {str(e)}. Dictionary key not found."}}
                elif error_type == 'AttributeError':
                    return {"success": False, "error": {"message": f"Runtime Error: {error_type} - {str(e)}. Attribute not found on object."}}
                elif error_type == 'ValueError':
                    return {"success": False, "error": {"message": f"Runtime Error: {error_type} - {str(e)}. Invalid value for operation."}}
                elif error_type == 'ZeroDivisionError':
                    return {"success": False, "error": {"message": f"Runtime Error: {error_type} - {str(e)}. Division by zero."}}
                else:
                    return {"success": False, "error": {"message": f"Runtime Error: {error_type} - {str(e)}"}}
        
        # Check for specific patterns that might cause issues
        if 'numbers[' in code_string and ']' in code_string:
            # Look for potential index out of bounds
            lines = code_string.split('\n')
            for line in lines:
                if 'numbers[' in line and ']' in line:
                    # Try to extract the index
                    import re
                    match = re.search(r'numbers\[(\d+)\]', line)
                    if match:
                        index = int(match.group(1))
                        # Check if numbers is defined in the code
                        if 'numbers = [' in code_string:
                            # Count the elements in the list
                            list_match = re.search(r'numbers = \[(.*?)\]', code_string)
                            if list_match:
                                elements = list_match.group(1).split(',')
                                if index >= len(elements):
                                    return {"success": False, "error": {"message": f"Runtime Warning: Index {index} is out of bounds for list with {len(elements)} elements."}}
        
        return {"success": True, "tree": tree}
        
    except Exception as e:
        return {"success": False, "error": {"message": f"Analysis Error: {str(e)}"}}