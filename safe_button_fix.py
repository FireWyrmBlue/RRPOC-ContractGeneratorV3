import re
import os
import sys

def restore_backup(backup_file, target_file):
    """
    Restore the file from backup
    """
    if os.path.exists(backup_file):
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Restored {target_file} from {backup_file}")
        return True
    else:
        print(f"Backup file {backup_file} not found")
        return False

def fix_button_ids_safe(file_path):
    """
    Adds unique keys to all st.button() calls in a Streamlit file in a safe way.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Pattern to match complete st.button calls on a single line
    pattern = r'st\.button\(([^,]+)(?:, [^=]+=[^,]+)*\)'
    
    # Count for generating unique keys
    count = 0
    # Fixed lines
    fixed_lines = []
    
    for line in lines:
        # Skip if line already has a key parameter
        if 'st.button(' in line and 'key=' not in line:
            # Check if the button call is complete on this line
            if ')' in line.split('st.button(', 1)[1]:
                count += 1
                key_name = f"btn_{count}"
                
                # Replace the button call with one that includes a key
                modified = re.sub(pattern, lambda m: m.group(0).replace(')', f', key="{key_name}")'), line, count=1)
                fixed_lines.append(modified)
                print(f"Fixed button {count} on line: {line.strip()}")
            else:
                # Skip complex multi-line button calls
                fixed_lines.append(line)
                print(f"Skipped complex button on line: {line.strip()}")
        else:
            fixed_lines.append(line)
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed {count} buttons without keys in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python safe_button_fix.py <backup_file> <target_file>")
        sys.exit(1)
        
    backup_file = sys.argv[1]
    target_file = sys.argv[2]
    
    if restore_backup(backup_file, target_file):
        fix_button_ids_safe(target_file)
    else:
        print("Backup restoration failed. Aborting.")
        sys.exit(1)
