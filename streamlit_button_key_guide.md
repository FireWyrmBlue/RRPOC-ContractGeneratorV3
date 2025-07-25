# Resolving Duplicate Button ID Issues in Streamlit

## Summary of the Issue

You've been encountering the error "There are multiple 'button' elements with the same auto-generated ID" in your Streamlit application. This occurs when:

1. Multiple buttons don't have explicit `key` parameters
2. Buttons have duplicate `key` values

## What We've Found

After analyzing your code, we've identified that:

1. Most buttons already have keys (btn_1, btn_2, etc.)
2. There are several buttons with duplicate keys
3. The file has some structural/indentation issues that are making automated fixes difficult

## Recommended Solution

### Step 1: Identify Duplicate Keys

We found these duplicate keys in your code:
- `key="btn_1"` (used for "Generate Random Vessel Name" AND "Add Variable")
- `key="btn_2"` (used for "Generate Another" AND "Preview Clause")
- `key="btn_3"` (used for "Show Examples" AND "Export All Templates")
- `key="btn_4"` (used for another "Add Variable")

### Step 2: Fix Duplicate Keys

We attempted to fix these by replacing the duplicate keys with more descriptive ones:
- `key="btn_1"` → keep for "Generate Random Vessel Name"
- `key="btn_var_1"` → for the first "Add Variable" button
- `key="btn_2"` → keep for "Generate Another" 
- `key="btn_preview_clause"` → for "Preview Clause"
- `key="btn_3"` → keep for "Show Examples"
- `key="btn_export_templates"` → for "Export All Templates"
- `key="btn_var_2"` → for the second "Add Variable" button

### Step 3: Address Structural Issues

Your file has some indentation/structural issues that are causing syntax errors. The most effective approach would be to:

1. Start with your last working version (before adding duplicate key fixes)
2. Manually identify and fix each duplicate key
3. Test each change incrementally

## Specific Steps to Fix

1. Open your file in VS Code
2. Use the Search function (Ctrl+F) to find all instances of `st.button(`
3. Ensure each button has a unique key parameter
4. Be especially careful with buttons in different tabs or sections that might have the same label

## Naming Convention for Keys

To avoid future issues, adopt a consistent naming convention:
- Feature-specific keys: `key="btn_generate_vessel"`
- Tab-specific keys: `key="btn_tab1_submit"`
- Section-specific keys: `key="btn_library_add"` 

## Testing Your Fix

After making these changes, run your app and check if:
1. The duplicate ID error is resolved
2. All buttons function as expected

If you continue to experience issues, consider a more structured refactoring of your UI code to ensure all interactive elements have unique identifiers.
