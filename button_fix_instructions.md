# Fixing Duplicate Button IDs in Streamlit

This guide explains how to fix the "multiple 'button' elements with the same auto-generated ID" error in your Streamlit application.

## The Problem

When Streamlit buttons don't have explicit unique keys, they get auto-generated IDs. If these IDs collide, you'll see this error:

```
There are multiple 'button' elements with the same auto-generated ID.
```

## The Solution

Every button in your Streamlit app needs a unique `key` parameter. For example:

```python
# Before (problematic):
st.button("Submit")

# After (fixed):
st.button("Submit", key="btn_submit")
```

## How to Fix Your App

### Automatic Approach

1. We've provided two helper scripts:
   - `add_button_keys.py`: Analyzes your app and provides instructions on where to add keys
   - `fix_buttons.py`: Attempts to automatically fix simple button cases

2. Run the analysis script first:
   ```
   python add_button_keys.py enhanced_yacht_generator_v3_fixed.py
   ```

3. Follow the provided instructions to manually add keys to your buttons.

### Manual Approach

If you prefer to fix buttons manually:

1. Find all `st.button()` calls in your code
2. Add a unique `key` parameter to each one
3. Use descriptive names or a numbering system like "btn_1", "btn_2", etc.

## Button Key Naming Strategy

For consistency, follow these key naming patterns:

- For action buttons: `btn_action_name` (e.g., `btn_submit_form`)
- For generation buttons: `btn_generate_x` (e.g., `btn_generate_vessel`)
- For display buttons: `btn_show_x` (e.g., `btn_show_examples`)
- For simple numbered buttons: `btn_1`, `btn_2`, etc.

## Testing Your Fix

After adding keys to all buttons, run your Streamlit app and verify that the error no longer appears and all buttons work as expected.

## Prevention Tips

- Always add unique keys to all Streamlit interactive elements (buttons, selectboxes, etc.)
- Use descriptive key names related to the button's function
- When duplicating code sections, remember to update keys to remain unique
