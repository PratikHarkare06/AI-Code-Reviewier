import ast
import sys
import io
import contextlib

def parse_code(code_string, language="Python"):
    """
    Parse code and check for errors. 
    Currently full static/runtime analysis is only supported for Python.
    """
    if language != "Python":
        return {"success": True, "message": f"Syntax check skipped for {language}"}

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
        
        return {"success": True, "tree": tree}
        
    except Exception as e:
        return {"success": False, "error": {"message": f"Analysis Error: {str(e)}"}}