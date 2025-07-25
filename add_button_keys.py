"""
Button Key Adder for Streamlit

This script helps manually add unique keys to st.button() calls in a Streamlit app.
It doesn't modify the file automatically but creates instructions for how to modify
each button.
"""

import re
import sys

def find_buttons_without_keys(file_path):
    """
    Find all st.button() calls that don't have a key parameter
    and print instructions for adding them.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    button_count = 0
    line_count = 0
    instructions = []
    
    for i, line in enumerate(lines):
        line_count = i + 1
        if 'st.button(' in line and 'key=' not in line:
            button_count += 1
            button_label = re.search(r'st\.button\(([^,)]+)', line)
            if button_label:
                label = button_label.group(1)
                button_key = f"btn_{button_count}"
                
                # Generate instruction
                if line.strip().endswith(')') or line.strip().endswith('):'):
                    # Simple case: closed parenthesis on the same line
                    if ')' in line:
                        instruction = f"Line {line_count}: Replace '{line.strip()}' with '{line.strip()[:-1]}, key=\"{button_key}\")'"
                    else:
                        instruction = f"Line {line_count}: Add key parameter: {line.strip()[:-1]}, key=\"{button_key}\"):"
                else:
                    # Complex case: multiline button call
                    instruction = f"Line {line_count}: Add key parameter after {label} but before any other parameters"
                
                instructions.append(instruction)
    
    return button_count, instructions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_button_keys.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    total_buttons, instructions = find_buttons_without_keys(file_path)
    
    print(f"Found {total_buttons} buttons without keys in {file_path}")
    print("\nInstructions for adding keys:")
    print("----------------------------")
    
    for instruction in instructions:
        print(instruction)
    
    print("\nRecommendation: Add these keys manually to avoid indentation issues.")
    print("Always use unique keys for each button to prevent duplicate ID errors.")
