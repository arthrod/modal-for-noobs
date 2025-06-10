"""Beautiful Modal-themed Gradio themes and styling.

This module provides Modal-branded themes and CSS styling for Gradio interfaces,
using the official Modal color palette from cli_helpers.common.
"""

import gradio as gr

# Import Modal's official color palette
from modal_for_noobs.cli_helpers.common import MODAL_GREEN, MODAL_LIGHT_GREEN, MODAL_DARK_GREEN, MODAL_BLACK


def create_modal_theme() -> gr.Theme:
    """
    Create a beautiful Modal-themed Gradio theme using official Modal colors.

    Returns:
        gr.Theme: Modal-themed Gradio theme with signature green colors
    """
    # Use Modal's official color palette
    modal_green = MODAL_GREEN  # "#7FEE64"
    modal_light_green = MODAL_LIGHT_GREEN  # "#DDFFDC"
    modal_dark_green = MODAL_DARK_GREEN  # "#323835"
    modal_black = MODAL_BLACK  # "#000000"
    modal_gray = "#f8f9fa"

    try:
        theme = gr.themes.Soft()
    except Exception:
        # Fallback to default theme if soft theme not available
        theme = gr.themes.Default()

    # Customize with Modal colors
    theme = theme.set(
        # Primary button styling
        button_primary_background_fill=modal_green,
        button_primary_background_fill_hover=modal_light_green,
        button_primary_background_fill_dark=modal_dark_green,
        button_primary_text_color=modal_black,
        button_primary_text_color_hover=modal_black,
        button_primary_text_color_dark="white",

        # Secondary button styling
        button_secondary_background_fill=f"rgba(127, 238, 100, 0.1)",  # MODAL_GREEN with alpha
        button_secondary_background_fill_hover=f"rgba(127, 238, 100, 0.2)",
        button_secondary_text_color=modal_dark_green,
        button_secondary_text_color_hover=modal_dark_green,
        button_secondary_border_color=modal_green,
        button_secondary_border_color_hover=modal_light_green,

        # Input and form styling
        input_background_fill="white",
        input_background_fill_focus="white",
        input_border_color=modal_green,
        input_border_color_focus=modal_light_green,
        input_border_width="2px",
        input_border_width_focus="2px",

        # Slider styling
        slider_color=modal_green,
        slider_color_dark=modal_green,

        # Checkbox and radio styling
        checkbox_background_color=modal_green,
        checkbox_background_color_selected=modal_green,
        checkbox_background_color_focus=modal_light_green,

        # General panel styling
        panel_background_fill="white",
        panel_background_fill_dark=modal_gray,
        panel_border_color=f"rgba(127, 238, 100, 0.2)",  # MODAL_GREEN with alpha
        panel_border_width="1px",

        # Body background with subtle Modal green gradient
        body_background_fill=f"linear-gradient(135deg, rgba(127, 238, 100, 0.05) 0%, rgba(221, 255, 220, 0.05) 100%)",
        body_background_fill_dark=f"linear-gradient(135deg, rgba(127, 238, 100, 0.1) 0%, rgba(221, 255, 220, 0.1) 100%)",

        # Text colors
        body_text_color="#1f2937",
        body_text_color_subdued="#6b7280",

        # Link colors
        link_text_color=modal_green,
        link_text_color_hover=modal_light_green,
        link_text_color_visited=modal_dark_green,

        # Block styling
        block_background_fill="white",
        block_border_color=f"rgba(127, 238, 100, 0.15)",  # MODAL_GREEN with alpha
        block_border_width="1px",
        block_radius="12px",
        block_shadow=f"0 2px 8px rgba(127, 238, 100, 0.1)",  # MODAL_GREEN with alpha

        # Font family
        font=("SF Pro Display", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"),
        font_mono=("SF Mono", "Monaco", "Consolas", "Liberation Mono", "Courier New", "monospace"),
    )

    return theme


def get_modal_css() -> str:
    """
    Get additional CSS for enhanced Modal styling using official Modal colors.

    Returns:
        str: CSS string with Modal-specific enhancements
    """
    modal_green = MODAL_GREEN  # "#7FEE64"
    modal_light_green = MODAL_LIGHT_GREEN  # "#DDFFDC"
    modal_dark_green = MODAL_DARK_GREEN  # "#323835"
    modal_black = MODAL_BLACK  # "#000000"

    return f"""
    /* MODAL ENHANCED STYLING */

    /* Custom button hover effects */
    .gr-button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(127, 238, 100, 0.3) !important;
    }}

    /* Enhanced input focus */
    .gr-textbox:focus-within,
    .gr-dropdown:focus-within {{
        box-shadow: 0 0 0 3px rgba(127, 238, 100, 0.2) !important;
    }}

    /* Beautiful tab styling */
    .gr-tab-nav button {{
        border-radius: 8px 8px 0 0 !important;
        border-bottom: none !important;
        font-weight: 600 !important;
    }}

    .gr-tab-nav button.selected {{
        background: {modal_green} !important;
        color: {modal_black} !important;
        border-color: {modal_green} !important;
    }}

    .gr-tab-nav button:not(.selected) {{
        background: rgba(127, 238, 100, 0.05) !important;
        color: {modal_dark_green} !important;
        border-color: rgba(127, 238, 100, 0.2) !important;
    }}

    .gr-tab-nav button:not(.selected):hover {{
        background: rgba(127, 238, 100, 0.1) !important;
        color: {modal_green} !important;
    }}

    /* Code block enhancements */
    .gr-code {{
        border: 1px solid rgba(127, 238, 100, 0.2) !important;
        border-radius: 8px !important;
        background: #f8fffe !important;
    }}

    /* Markdown enhancements */
    .gr-markdown h1,
    .gr-markdown h2,
    .gr-markdown h3 {{
        color: {modal_green} !important;
        font-weight: 700 !important;
    }}

    .gr-markdown code {{
        background: rgba(127, 238, 100, 0.1) !important;
        color: {modal_dark_green} !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
    }}

    .gr-markdown pre {{
        background: #f8fffe !important;
        border: 1px solid rgba(127, 238, 100, 0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(127, 238, 100, 0.1) !important;
    }}

    /* Enhanced progress bars */
    .gr-progress {{
        background: {modal_green} !important;
    }}

    /* Beautiful file upload styling */
    .gr-file-upload {{
        border: 2px dashed rgba(127, 238, 100, 0.4) !important;
        border-radius: 12px !important;
        background: rgba(127, 238, 100, 0.02) !important;
    }}

    .gr-file-upload:hover {{
        border-color: {modal_green} !important;
        background: rgba(127, 238, 100, 0.05) !important;
    }}

    /* Enhanced dropdown styling */
    .gr-dropdown-arrow {{
        color: {modal_green} !important;
    }}

    /* Beautiful checkbox styling */
    .gr-checkbox input[type="checkbox"]:checked {{
        background-color: {modal_green} !important;
        border-color: {modal_green} !important;
    }}

    /* Enhanced radio button styling */
    .gr-radio input[type="radio"]:checked {{
        background-color: {modal_green} !important;
        border-color: {modal_green} !important;
    }}

    /* Slider enhancements */
    .gr-slider input[type="range"]::-webkit-slider-thumb {{
        background: {modal_green} !important;
        border: 2px solid white !important;
        box-shadow: 0 2px 6px rgba(127, 238, 100, 0.3) !important;
    }}

    .gr-slider input[type="range"]::-moz-range-thumb {{
        background: {modal_green} !important;
        border: 2px solid white !important;
        box-shadow: 0 2px 6px rgba(127, 238, 100, 0.3) !important;
    }}

    /* Modal deployment button special styling */
    .modal-deploy-button {{
        background: linear-gradient(135deg, {modal_green} 0%, {modal_light_green} 100%) !important;
        border: none !important;
        color: {modal_black} !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(127, 238, 100, 0.4) !important;
        transition: all 0.3s ease !important;
        font-size: 16px !important;
        padding: 12px 24px !important;
        cursor: pointer !important;
    }}

    .modal-deploy-button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(127, 238, 100, 0.6) !important;
        background: linear-gradient(135deg, {modal_light_green} 0%, {modal_green} 100%) !important;
    }}

    /* Loading spinner in Modal colors */
    .gr-loading {{
        border-top-color: {modal_green} !important;
    }}

    /* Enhanced error styling */
    .gr-error {{
        border-left: 4px solid #ef4444 !important;
        background: rgba(239, 68, 68, 0.1) !important;
    }}

    /* Enhanced success styling */
    .gr-success {{
        border-left: 4px solid {modal_green} !important;
        background: rgba(127, 238, 100, 0.1) !important;
    }}

    /* Beautiful tooltips */
    .gr-tooltip {{
        background: {modal_dark_green} !important;
        color: white !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }}

    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: rgba(127, 238, 100, 0.1);
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb {{
        background: rgba(127, 238, 100, 0.5);
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: {modal_green};
    }}

    /* Gradio container dark mode styling */
    .gradio-container {{
        background-color: {modal_black} !important;
    }}
    
    .dark {{
        --block-background-fill: {modal_dark_green} !important;
    }}
    
    .gr-button-primary {{
        background-color: {modal_green} !important;
        color: {modal_black} !important;
        border: none !important;
    }}
    
    .gr-button-secondary {{
        background-color: transparent !important;
        color: {modal_green} !important;
        border: 1px solid {modal_green} !important;
    }}
    """


# Pre-built themes for quick use
MODAL_THEME = create_modal_theme()
MODAL_CSS = get_modal_css()