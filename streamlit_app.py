"""
Geomagnetic Storms & Self-Harm Mortality Explorer
Main landing page for the Streamlit application
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import base64
from pathlib import Path
from utils.data_loader import load_preprocessed_data
from components.charts import create_comparison_bar_chart, create_multi_outcome_comparison
from components.explanations import show_caveat_banner, explain_correlation, explain_outcome_types, explain_mixed_results


# Page configuration
st.set_page_config(
    page_title="Geomagnetic Storms & Mental Health",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cinematic Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Dark cosmic background for entire app - matching hero */
    .stApp {
        background: linear-gradient(180deg,
            #000000 0%,
            #0a0a0f 15%,
            #0f0f14 40%,
            #14141f 70%,
            #1a1a28 100%) !important;
    }

    /* Header bar - make it dark */
    header[data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        border-bottom: 1px solid rgba(255, 160, 80, 0.2) !important;
    }

    /* Header toolbar buttons */
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] svg {
        color: #e0e0e8 !important;
        fill: #e0e0e8 !important;
    }

    header[data-testid="stHeader"] button:hover {
        background-color: rgba(255, 160, 80, 0.1) !important;
    }

    /* Main content area */
    section[data-testid="stAppViewContainer"] {
        background: transparent !important;
    }

    .main {
        background: transparent !important;
    }

    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        background: transparent !important;
    }

    /* Ensure background applies to all sections */
    section[data-testid="stMain"] {
        background: transparent !important;
    }
    
    /* All text elements in dark theme */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
    }
    
    .stApp p, .stApp li, .stApp span, .stApp div, .stApp label,
    .main p, .main li, .main span, .main div, .main label {
        color: #e0e0e8 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stApp a, .main a {
        color: #ffb366 !important;
    }
    
    .stApp a:hover, .main a:hover {
        color: #ffd699 !important;
    }
    
    /* Markdown text */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] div {
        color: #e0e0e8 !important;
    }
    
    /* Metrics styling - cosmic cards */
    [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"],
    [data-testid="stMetric"] label {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #ffb366 !important;
    }
    
    [data-testid="metric-container"],
    [data-testid="stMetric"] {
        background: rgba(30, 30, 45, 0.6) !important;
        border: 1px solid rgba(255, 160, 80, 0.3) !important;
        border-radius: 8px !important;
        padding: 1.2rem !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Metric value styling */
    div[data-testid="stMetric"] > div {
        color: #ffffff !important;
    }
    
    /* Selectbox and inputs */
    .stSelectbox label, .stMultiSelect label, .stSlider label,
    label[data-testid="stWidgetLabel"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {
        background-color: rgba(30, 30, 45, 0.8) !important;
        border: 1px solid rgba(255, 160, 80, 0.4) !important;
        color: #ffffff !important;
    }

    /* Selectbox selected value text - make it more visible */
    .stSelectbox div[data-baseweb="select"] div[role="button"],
    div[data-baseweb="select"] div[role="button"] {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    .stSelectbox div[data-baseweb="select"] div[role="button"] > div,
    div[data-baseweb="select"] div[role="button"] > div {
        color: #ffffff !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div:hover,
    div[data-baseweb="select"] > div:hover {
        border-color: rgba(255, 160, 80, 0.6) !important;
        background-color: rgba(40, 40, 60, 0.9) !important;
    }
    
    /* Dropdown menu */
    div[data-baseweb="popover"] {
        background-color: rgba(240, 240, 245, 0.98) !important;
    }

    ul[role="listbox"] {
        background-color: rgba(240, 240, 245, 0.98) !important;
        border: 1px solid rgba(255, 160, 80, 0.3) !important;
    }

    li[role="option"] {
        color: #1a1a1a !important;
        font-weight: 500 !important;
        background-color: transparent !important;
    }

    li[role="option"]:hover {
        background-color: rgba(255, 140, 60, 0.2) !important;
        color: #000000 !important;
    }

    /* Dropdown menu item text */
    li[role="option"] div {
        color: #1a1a1a !important;
    }

    li[role="option"] span {
        color: #1a1a1a !important;
    }
    
    /* Dividers */
    hr, [data-testid="stHorizontalBlock"] hr {
        border: none !important;
        border-top: 2px solid rgba(255, 160, 80, 0.3) !important;
        margin: 2rem 0 !important;
        opacity: 1 !important;
    }
    
    /* Info, warning, success boxes */
    .stAlert, [data-testid="stAlert"],
    div[data-baseweb="notification"] {
        background-color: rgba(30, 30, 45, 0.7) !important;
        border: 1px solid rgba(255, 160, 80, 0.4) !important;
        border-left: 4px solid #ff8c3c !important;
        border-radius: 8px !important;
        color: #e0e0e8 !important;
    }
    
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    div[data-baseweb="notification"] p,
    div[data-baseweb="notification"] span {
        color: #e0e0e8 !important;
    }
    
    [data-testid="stMarkdownContainer"] > div[data-testid="stMarkdown"] > div[style*="background-color"] {
        background-color: rgba(30, 30, 45, 0.7) !important;
        border-left: 4px solid #ff8c3c !important;
        border-radius: 4px !important;
        padding: 1rem !important;
    }
    
    /* Code blocks */
    code {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffb366 !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 3px !important;
    }
    
    pre {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 160, 80, 0.2) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 160, 80, 0.2) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: rgba(255, 140, 60, 0.08) !important;
        border-color: rgba(255, 160, 80, 0.4) !important;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 160, 80, 0.15) !important;
        border-top: none !important;
        color: #e0e0e8 !important;
    }
    
    /* Ensure horizontal blocks work correctly for columns */
    [data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }

    /* Column containers styling - DON'T override display/flex */
    [data-testid="column"] {
        background: rgba(30, 30, 45, 0.3) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        padding-bottom: 2rem !important;
        border: 1px solid rgba(255, 160, 80, 0.15) !important;
        min-height: 0 !important;
        height: auto !important;
        overflow: visible !important;
    }

    [data-testid="column"] > div {
        color: #e0e0e8 !important;
        overflow: visible !important;
        height: auto !important;
        padding-bottom: 1rem !important;
    }

    /* Ensure column content is fully visible */
    [data-testid="column"] [data-testid="stMarkdownContainer"],
    [data-testid="column"] p {
        overflow: visible !important;
        height: auto !important;
        max-height: none !important;
        color: #e0e0e8 !important;
        opacity: 1 !important;
    }

    /* Ensure all text in columns is visible */
    [data-testid="column"] * {
        visibility: visible !important;
    }

    /* Aggressively prevent text clipping in columns */
    [data-testid="column"],
    [data-testid="column"] > *,
    [data-testid="column"] [data-testid="element-container"] {
        overflow: visible !important;
        height: auto !important;
        max-height: none !important;
        min-height: 0 !important;
    }

    /* Ensure stElement containers don't clip */
    [data-testid="stVerticalBlock"] [data-testid="element-container"] {
        overflow: visible !important;
        height: auto !important;
    }
    
    /* Markdown container styling */
    [data-testid="stMarkdownContainer"] {
        color: #e0e0e8 !important;
    }
    
    /* Strong/bold text */
    strong {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Lists */
    ul, ol {
        color: #e0e0e8 !important;
    }
    
    li {
        color: #e0e0e8 !important;
        margin-bottom: 0.5rem;
    }
    
    /* Tables */
    table {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 160, 80, 0.2) !important;
    }
    
    thead tr {
        background-color: rgba(255, 140, 60, 0.15) !important;
        color: #ffffff !important;
    }
    
    tbody tr {
        border-bottom: 1px solid rgba(255, 160, 80, 0.1) !important;
    }
    
    tbody tr:hover {
        background-color: rgba(255, 140, 60, 0.05) !important;
    }
    
    th, td {
        color: #e0e0e8 !important;
        padding: 0.75rem !important;
    }
    
    /* Plotly charts - dark theme */
    .js-plotly-plot {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 160, 80, 0.2) !important;
    }
    
    /* Footer styling */
    footer {
        background: transparent !important;
    }
    
    footer p, footer a {
        color: #888 !important;
    }
    
    /* Custom metric container class */
    .metric-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 160, 80, 0.2);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .big-font {
        font-size: 30px !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }
    
    /* VISIBLE starfield across entire page - matching hero section */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #000000;
        background-image:
            radial-gradient(circle 2px at 5% 10%, white, transparent),
            radial-gradient(circle 1px at 12% 25%, white, transparent),
            radial-gradient(circle 2px at 18% 8%, white, transparent),
            radial-gradient(circle 1px at 25% 35%, white, transparent),
            radial-gradient(circle 3px at 32% 18%, white, transparent),
            radial-gradient(circle 1px at 38% 42%, white, transparent),
            radial-gradient(circle 2px at 45% 12%, white, transparent),
            radial-gradient(circle 1px at 52% 55%, white, transparent),
            radial-gradient(circle 2px at 58% 28%, white, transparent),
            radial-gradient(circle 1px at 65% 65%, white, transparent),
            radial-gradient(circle 3px at 72% 15%, white, transparent),
            radial-gradient(circle 1px at 78% 48%, white, transparent),
            radial-gradient(circle 2px at 85% 35%, white, transparent),
            radial-gradient(circle 1px at 92% 72%, white, transparent),
            radial-gradient(circle 2px at 8% 58%, white, transparent),
            radial-gradient(circle 1px at 15% 78%, white, transparent),
            radial-gradient(circle 2px at 22% 88%, white, transparent),
            radial-gradient(circle 1px at 35% 92%, white, transparent),
            radial-gradient(circle 3px at 48% 82%, white, transparent),
            radial-gradient(circle 1px at 55% 68%, white, transparent),
            radial-gradient(circle 2px at 68% 95%, white, transparent),
            radial-gradient(circle 1px at 75% 85%, white, transparent),
            radial-gradient(circle 2px at 88% 90%, white, transparent),
            radial-gradient(circle 1px at 95% 58%, white, transparent),
            radial-gradient(circle 2px at 40% 5%, white, transparent),
            radial-gradient(circle 1px at 60% 22%, white, transparent),
            radial-gradient(circle 2px at 28% 48%, white, transparent),
            radial-gradient(circle 1px at 82% 38%, white, transparent);
        background-size: 100% 100%;
        background-position: 0 0;
        opacity: 1;
        pointer-events: none;
        z-index: 0;
    }

    /* Extended sunlight glow - STAYS AT TOP where sun is located */
    .stApp::after {
        content: '';
        position: absolute;
        top: 400px;
        left: -10%;
        width: 1400px;
        height: 1400px;
        background: radial-gradient(
            ellipse at center,
            rgba(255, 240, 180, 0.3) 0%,
            rgba(255, 220, 140, 0.22) 15%,
            rgba(255, 180, 100, 0.15) 30%,
            rgba(255, 140, 60, 0.1) 45%,
            rgba(255, 100, 40, 0.05) 60%,
            rgba(45, 24, 16, 0.02) 75%,
            transparent 90%
        );
        pointer-events: none;
        z-index: 0;
        filter: blur(120px);
        opacity: 1;
    }

    /* Additional atmospheric layer - ALSO stays at top */
    section[data-testid="stMain"]::before {
        content: '';
        position: absolute;
        top: 450px;
        left: -5%;
        width: 1100px;
        height: 1100px;
        background: radial-gradient(
            ellipse at center,
            rgba(255, 200, 120, 0.18) 0%,
            rgba(255, 160, 80, 0.1) 40%,
            rgba(80, 50, 30, 0.03) 70%,
            transparent 85%
        );
        pointer-events: none;
        z-index: 0;
        filter: blur(140px);
    }
    
    /* Ensure content stays above background effects */
    .main, .main > div, section[data-testid="stMain"] {
        position: relative;
        z-index: 1;
    }

    /* Sidebar styling for better legibility */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            rgba(10, 10, 15, 0.98) 0%,
            rgba(15, 15, 20, 0.98) 50%,
            rgba(20, 20, 30, 0.98) 100%) !important;
        border-right: 1px solid rgba(255, 160, 80, 0.2) !important;
    }

    /* Sidebar content */
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }

    /* Sidebar text - high contrast */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] li {
        color: #f0f0f0 !important;
        font-weight: 500 !important;
    }

    /* Sidebar navigation links */
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-decoration: none !important;
    }

    section[data-testid="stSidebar"] a:hover,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        color: #ffb366 !important;
        background-color: rgba(255, 140, 60, 0.15) !important;
    }

    /* Sidebar navigation items */
    [data-testid="stSidebarNav"] li {
        color: #ffffff !important;
    }

    [data-testid="stSidebarNav"] li > div {
        color: #ffffff !important;
    }

    /* Active/selected page in sidebar */
    [data-testid="stSidebarNav"] li[aria-selected="true"],
    [data-testid="stSidebarNav"] li[aria-selected="true"] a {
        background-color: rgba(255, 140, 60, 0.25) !important;
        color: #ffb366 !important;
        font-weight: 700 !important;
    }

    /* Sidebar widgets */
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stSlider label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] button {
        color: #ffffff !important;
        background-color: rgba(255, 140, 60, 0.2) !important;
        border: 1px solid rgba(255, 160, 80, 0.4) !important;
    }

    section[data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 140, 60, 0.35) !important;
        border-color: rgba(255, 160, 80, 0.6) !important;
    }
    
    /* COMPLETELY remove iframe borders and gaps */
    iframe, iframe[title] {
        margin: 0 !important;
        padding: 0 !important;
        display: block !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Ensure NO spacing around hero component */
    [data-testid="stVerticalBlock"] > div:first-child {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Remove any gaps around the hero iframe - ONLY target first child */
    [data-testid="stVerticalBlock"] > div:first-child > div > iframe {
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        display: block !important;
    }

    /* Ensure main block container has minimal top padding */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
    }
    
    /* Navigation section styling */
    .main h2:contains("Additional Pages") {
        margin-top: 3rem !important;
    }
    
    /* Prevent text overflow and ensure full visibility */
    [data-testid="stMarkdownContainer"] {
        overflow: visible !important;
    }

    /* Basic heading spacing - maintain normal alignment */
    h1, h2, h3 {
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        clear: both !important;
    }

    h4, h5, h6 {
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        clear: both !important;
    }

    /* Paragraphs with proper spacing and visibility */
    p {
        margin-bottom: 1rem !important;
        line-height: 1.6 !important;
    }

    /* Ensure content is fully visible - no clipping */
    .main .block-container > div,
    [data-testid="stVerticalBlock"],
    [data-testid="element-container"] {
        overflow: visible !important;
        height: auto !important;
        max-height: none !important;
    }

    /* Ensure block containers expand to fit content */
    .main .block-container,
    .main .block-container > div > div {
        overflow: visible !important;
        height: auto !important;
    }

    /* Hide Material Icons text fallback that shows as "keyboard_arrow_right" etc */
    .material-icons-text,
    span[class*="material-icons"]:not([class*="material-icons-"]):empty::before,
    [data-testid="stExpanderToggleIcon"]::before {
        font-size: 0 !important;
        content: '' !important;
    }

    /* Fix expander arrows showing text instead of icons */
    details summary::before,
    [data-testid="stExpander"] summary::before,
    .streamlit-expanderHeader::before {
        content: '▶' !important;
        display: inline-block !important;
        margin-right: 0.5rem !important;
        font-size: 0.8em !important;
        transition: transform 0.2s !important;
    }

    details[open] summary::before,
    [data-testid="stExpander"][open] summary::before,
    .streamlit-expanderHeader[aria-expanded="true"]::before {
        transform: rotate(90deg) !important;
    }

    /* Hide any text that says "keyboard_arrow_right" or similar */
    *:not(code):not(pre) {
        text-indent: 0 !important;
    }

    /* Specifically target and hide icon font text fallbacks */
    span:empty::after,
    span:empty::before {
        content: none !important;
    }

    /* Hide text nodes containing icon names */
    [class*="icon"]::before,
    [class*="icon"]::after {
        font-family: 'Inter', sans-serif !important;
    }

    /* Ensure expander icons work properly */
    button[kind="header"] span,
    [data-testid="stExpanderToggleIcon"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* Aggressively hide icon text fallbacks */
    span[data-testid*="Icon"],
    span[class*="icon"],
    [class*="material-icons"],
    button span:empty,
    a span:empty {
        font-size: 0 !important;
        width: 0 !important;
        height: 0 !important;
        display: inline-block !important;
        overflow: hidden !important;
        text-indent: -9999px !important;
    }

    /* Hide any span that only contains icon text */
    span:only-child {
        color: transparent !important;
    }

    /* Target navigation arrows specifically */
    [data-testid="stSidebarNav"] span,
    [data-testid="stSidebarNavLink"] span,
    button[kind="header"] span {
        font-family: 'Inter', sans-serif !important;
    }
</style>

<script>
// Aggressively remove icon text fallbacks
(function() {
    function removeIconText() {
        const iconTexts = [
            'keyboard_arrow_right', 'keyboard_arrow_down', 'keyboard_arrow_left', 'keyboard_arrow_up',
            'expand_more', 'expand_less', 'arrow_forward', 'arrow_back', 'arrow_downward', 'arrow_upward',
            'chevron_right', 'chevron_left', 'navigate_next', 'navigate_before'
        ];

        // Find all text nodes
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const nodesToRemove = [];
        while(walker.nextNode()) {
            const node = walker.currentNode;
            const text = node.textContent.trim();

            if (iconTexts.includes(text)) {
                nodesToRemove.push(node);
            }
        }

        // Remove the text nodes
        nodesToRemove.forEach(node => {
            if (node.parentElement) {
                // Hide the parent element
                const parent = node.parentElement;
                parent.style.cssText = 'font-size: 0 !important; width: 0 !important; height: 0 !important; overflow: hidden !important; position: absolute !important; left: -9999px !important;';
                // Or just remove the text
                node.textContent = '';
            }
        });

        // Also find spans with only icon text and hide them
        document.querySelectorAll('span').forEach(span => {
            if (iconTexts.includes(span.textContent.trim())) {
                span.style.cssText = 'display: none !important;';
                span.textContent = '';
            }
        });
    }

    // Run immediately
    removeIconText();

    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', removeIconText);
    }

    // Run periodically
    setInterval(removeIconText, 100);

    // Watch for DOM changes
    const observer = new MutationObserver(function(mutations) {
        removeIconText();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true,
        characterDataOldValue: false
    });
})();
</script>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    return load_preprocessed_data()

# Function to encode image to base64
@st.cache_data
def get_base64_image(image_path):
    """Convert image to base64 for embedding in HTML."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return ""

data = load_data()
summary_stats = data['summary_stats']
weekly_df = data['weekly']

# Get base64 encoded sun image
sun_image_path = Path(__file__).parent / "assets/images/fiery-celestial-orb-glowing-lunar-display/sun.png"
sun_image_base64 = get_base64_image(sun_image_path)

# Hero Section with Space Theme
hero_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;600;800&display=swap');
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        background: transparent;
    }}
    
    /* Hero Container - pure black with fade-out at bottom */
    .hero-container {{
        position: relative;
        width: 100%;
        height: 650px;
        background: #000000;
        overflow: hidden;
    }}

    /* Fade out bottom edge of hero to blend seamlessly */
    .hero-container::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 80px;
        background: linear-gradient(to bottom, transparent 0%, #000000 100%);
        z-index: 200;
        pointer-events: none;
    }}
    
    /* Dark cosmic gradient overlay */
    .hero-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(ellipse at 20% 50%, rgba(45, 24, 16, 0.6) 0%, rgba(26, 15, 45, 0.4) 35%, transparent 65%);
        z-index: 1;
        pointer-events: none;
    }}
    
    /* Starfield */
    .stars {{
        position: absolute;
        width: 100%;
        height: 100%;
        z-index: 2;
    }}
    
    .star {{
        position: absolute;
        background: white;
        border-radius: 50%;
        animation: twinkle linear infinite;
    }}
    
    @keyframes twinkle {{
        0%, 100% {{ opacity: 0.3; }}
        50% {{ opacity: 1; }}
    }}
    
    /* Nebula/Gas Cloud Effect */
    .nebula {{
        position: absolute;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(ellipse at 20% 50%, rgba(255, 140, 60, 0.12) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 40%, rgba(60, 100, 200, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(120, 80, 180, 0.06) 0%, transparent 50%);
        z-index: 3;
        filter: blur(80px);
        animation: nebula-drift 50s ease-in-out infinite;
    }}
    
    @keyframes nebula-drift {{
        0%, 100% {{ transform: translate(0, 0) scale(1); }}
        50% {{ transform: translate(30px, -30px) scale(1.08); }}
    }}
    
    /* Photorealistic Sun */
    .sun-container {{
        position: absolute;
        bottom: -15%;
        left: -8%;
        width: 750px;
        height: 750px;
        z-index: 4;
        animation: sun-float 12s ease-in-out infinite;
    }}
    
    .sun-image {{
        position: relative;
        width: 100%;
        height: 100%;
        animation: sun-rotate 120s linear infinite;
    }}
    
    .sun-image img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        filter: contrast(1.15) saturate(1.2) brightness(1.05);
    }}
    
    /* Enhanced Glow/Corona */
    .sun-glow {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 120%;
        height: 120%;
        background: radial-gradient(circle, 
            rgba(255, 240, 180, 0.4) 0%,
            rgba(255, 220, 140, 0.3) 20%,
            rgba(255, 180, 100, 0.2) 40%,
            rgba(255, 140, 60, 0.1) 60%,
            transparent 80%);
        filter: blur(40px);
        animation: glow-pulse 8s ease-in-out infinite;
        pointer-events: none;
    }}
    
    /* Outer atmospheric glow */
    .sun-atmosphere {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 150%;
        height: 150%;
        background: radial-gradient(circle, 
            rgba(255, 220, 120, 0.25) 0%,
            rgba(255, 180, 80, 0.15) 30%,
            rgba(255, 140, 50, 0.08) 50%,
            transparent 70%);
        filter: blur(60px);
        animation: atmosphere-pulse 10s ease-in-out infinite;
        pointer-events: none;
    }}
    
    @keyframes sun-float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-20px); }}
    }}
    
    @keyframes sun-rotate {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    
    @keyframes glow-pulse {{
        0%, 100% {{ opacity: 0.8; transform: translate(-50%, -50%) scale(1); }}
        50% {{ opacity: 1; transform: translate(-50%, -50%) scale(1.05); }}
    }}
    
    @keyframes atmosphere-pulse {{
        0%, 100% {{ opacity: 0.6; transform: translate(-50%, -50%) scale(1); }}
        50% {{ opacity: 0.8; transform: translate(-50%, -50%) scale(1.08); }}
    }}
    
    /* Light rays/solar flares */
    .solar-rays {{
        position: absolute;
        top: 50%;
        left: 50%;
        width: 200%;
        height: 200%;
        transform: translate(-50%, -50%);
        pointer-events: none;
        z-index: 1;
    }}
    
    .ray {{
        position: absolute;
        top: 50%;
        left: 50%;
        width: 150%;
        height: 2px;
        background: linear-gradient(90deg, 
            transparent 0%,
            rgba(255, 240, 200, 0.3) 20%,
            rgba(255, 200, 150, 0.2) 40%,
            transparent 60%);
        transform-origin: 0% 50%;
        filter: blur(3px);
        animation: ray-rotate 30s linear infinite;
    }}
    
    .ray:nth-child(2) {{
        animation-duration: 25s;
        animation-delay: -8s;
        opacity: 0.6;
    }}
    
    .ray:nth-child(3) {{
        animation-duration: 35s;
        animation-delay: -15s;
        opacity: 0.4;
    }}
    
    @keyframes ray-rotate {{
        from {{ transform: translate(-50%, -50%) rotate(0deg); }}
        to {{ transform: translate(-50%, -50%) rotate(360deg); }}
    }}
    
    /* Hero Content - Positioned on right to avoid sun */
    .hero-content {{
        position: relative;
        z-index: 100;
        padding: 60px 50px;
        max-width: 55%;
        margin-left: auto;
        margin-right: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }}

    .hero-title {{
        font-family: 'Inter', sans-serif;
        font-size: 4.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 1.5rem;
        text-shadow:
            2px 2px 20px rgba(0, 0, 0, 0.9),
            0 0 40px rgba(255, 140, 60, 0.3);
        letter-spacing: -0.02em;
        line-height: 1.15;
        word-wrap: break-word;
    }}

    .hero-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 300;
        color: #f0e5d8;
        line-height: 1.8;
        text-shadow: 2px 2px 15px rgba(0, 0, 0, 1);
        max-width: 95%;
        margin-bottom: 1.5rem;
        word-wrap: break-word;
    }}
    
    .storm-indicator {{
        display: inline-block;
        margin-top: 2rem;
        padding: 1rem 2rem;
        background: rgba(255, 140, 60, 0.12);
        border: 2px solid rgba(255, 160, 80, 0.4);
        border-radius: 0;
        color: #ffb366;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        backdrop-filter: blur(10px);
        box-shadow: 
            0 0 20px rgba(255, 140, 60, 0.2),
            inset 0 0 20px rgba(255, 140, 60, 0.05);
        animation: indicator-pulse 2s ease-in-out infinite;
    }}
    
    @keyframes indicator-pulse {{
        0%, 100% {{ 
            border-color: rgba(255, 160, 80, 0.4);
            box-shadow: 
                0 0 20px rgba(255, 140, 60, 0.2),
                inset 0 0 20px rgba(255, 140, 60, 0.05);
        }}
        50% {{ 
            border-color: rgba(255, 160, 80, 0.6);
            box-shadow: 
                0 0 30px rgba(255, 140, 60, 0.4),
                inset 0 0 20px rgba(255, 140, 60, 0.1);
        }}
    }}
    
    /* Responsive adjustments */
    @media (max-width: 1200px) {{
        .hero-title {{
            font-size: 3.5rem;
            line-height: 1.2;
        }}
        .hero-subtitle {{
            font-size: 1.3rem;
            line-height: 1.7;
        }}
        .hero-content {{
            padding: 50px 40px;
            max-width: 60%;
        }}
        .sun-container {{
            width: 600px;
            height: 600px;
        }}
    }}

    @media (max-width: 768px) {{
        .hero-container {{
            height: 550px;
        }}
        .hero-title {{
            font-size: 2.5rem;
            line-height: 1.25;
            margin-bottom: 1rem;
        }}
        .hero-subtitle {{
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }}
        .hero-content {{
            padding: 30px 25px;
            max-width: 100%;
        }}
        .storm-indicator {{
            margin-top: 1rem;
            padding: 0.8rem 1.5rem;
            font-size: 0.75rem;
        }}
        .sun-container {{
            width: 400px;
            height: 400px;
            bottom: -20%;
            left: -15%;
        }}
    }}
</style>
</head>
<body>
<div class="hero-container" id="heroContainer">
    <!-- Starfield -->
    <div class="stars" id="starfield"></div>
    
    <!-- Nebula Background -->
    <div class="nebula"></div>
    
    <!-- Photorealistic Sun with Image -->
    <div class="sun-container">
        <div class="sun-atmosphere"></div>
        <div class="sun-glow"></div>
        <div class="solar-rays">
            <div class="ray"></div>
            <div class="ray"></div>
            <div class="ray"></div>
        </div>
        <div class="sun-image">
            <img src="data:image/png;base64,{sun_image_base64}" alt="Photorealistic Sun">
        </div>
    </div>
    
    <!-- Hero Text Content - Positioned on right to avoid sun -->
    <div class="hero-content">
        <h1 class="hero-title">
            Do Magnetic Storms<br>
            Affect Health?
        </h1>
        <p class="hero-subtitle">
            Exploring statistical relationships between solar geomagnetic storms and 
            human health outcomes across the United States.
        </p>
        <div class="storm-indicator">⚡ ANALYZING {summary_stats['n_weeks']:,}+ WEEKS OF DATA</div>
    </div>
</div>

<script>
    // Create realistic starfield
    const starfield = document.getElementById('starfield');
    if (starfield) {{
        const starCount = 200;
        
        for (let i = 0; i < starCount; i++) {{
            const star = document.createElement('div');
            star.className = 'star';
            
            // Random position
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            
            // Varied sizes
            const size = Math.random() < 0.9 ? (1 + Math.random() * 1.5) : (2 + Math.random() * 2);
            star.style.width = size + 'px';
            star.style.height = size + 'px';
            
            // Varied brightness
            star.style.opacity = 0.3 + Math.random() * 0.7;
            
            // Varied twinkle speed
            star.style.animationDuration = (3 + Math.random() * 4) + 's';
            star.style.animationDelay = Math.random() * 5 + 's';
            
            starfield.appendChild(star);
        }}
        
        // Subtle parallax on mouse move
        document.addEventListener('mousemove', (e) => {{
            const moveX = (e.clientX / window.innerWidth - 0.5) * 20;
            const moveY = (e.clientY / window.innerHeight - 0.5) * 20;
            
            const sun = document.querySelector('.sun-container');
            const starfieldEl = document.getElementById('starfield');
            
            if (sun) {{
                sun.style.transform = 'translate(' + (moveX * 0.8) + 'px, ' + (moveY * 0.8) + 'px)';
            }}
            
            if (starfieldEl) {{
                starfieldEl.style.transform = 'translate(' + (moveX * 0.3) + 'px, ' + (moveY * 0.3) + 'px)';
            }}
        }});
    }}
</script>
</body>
</html>
"""

# Render the hero section using components.html for proper rendering
components.html(hero_html, height=650, scrolling=False)

# Outcome selector - NO divider to maintain seamless space transition
outcome_map = {
    'Suicide': 'suicide',
    'Violence/Assault': 'violence',
    'Overdose': 'overdose',
    'Cardiovascular': 'cardiovascular'
}

selected_outcome_label = st.selectbox(
    "Select outcome to explore:",
    options=list(outcome_map.keys()),
    index=0,
    help="Suicide is the primary behavioral outcome. Other outcomes test specificity."
)

selected_outcome = outcome_map[selected_outcome_label]
st.markdown("---")

# Animated metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Weeks Analyzed",
        value=f"{summary_stats['n_weeks']}",
        help="Weekly data from 2018 to 2025"
    )

with col2:
    st.metric(
        label=f"Average Weekly Deaths ({selected_outcome_label})",
        value=f"{summary_stats['outcomes'][selected_outcome]['mean']:.0f}",
        help="US national weekly average"
    )

with col3:
    st.metric(
        label="Average Storm Index",
        value=f"{summary_stats['geomagnetic']['mean_Kp']:.1f}",
        help="Mean Kp index across all measurements"
    )

st.divider()

# Key Finding Card
st.markdown("## Key Finding")

col1, col2 = st.columns([2, 1])

with col1:
    # Get the strongest correlation for selected outcome
    if selected_outcome in summary_stats['strongest_correlations']:
        corr_overall = summary_stats['strongest_correlations'][selected_outcome]['overall']
        corr_same_week = summary_stats['strongest_correlations'][selected_outcome].get('same_week')
        corr_lag1 = summary_stats['strongest_correlations'][selected_outcome].get('lag1')
        
        # Use overall strongest for main display
        corr_data = corr_overall
        
        # Determine direction of correlation
        if corr_data['pearson_r'] > 0:
            direction = "positive"
            explanation = "higher during storm weeks"
        else:
            direction = "negative"
            explanation = "**lower** during storm weeks (inverse correlation)"
        
        sig_text = "statistically significant" if corr_data['pearson_p'] < 0.05 else "not statistically significant"
        
        st.metric(
            label=f"Correlation ({selected_outcome_label})",
        value=f"r = {corr_data['pearson_r']:.3f}",
            delta=f"{sig_text}",
            help=f"Strongest: {corr_data['metric']} [{corr_data['lag']}]"
        )
        
        # Get comparison data for this outcome
        comp_data = summary_stats['outcome_comparisons'][selected_outcome]
        diff = comp_data['difference']
        
        # Outcome-specific language
        outcome_specific_text = {
            'suicide': 'Deaths by self-harm',
            'violence': 'Deaths from assault/violence',
            'overdose': 'Deaths from overdose',
            'cardiovascular': 'Cardiovascular deaths'
        }
        outcome_text = outcome_specific_text.get(selected_outcome, 'Deaths')
        
        lag_explanation = ""
        if corr_data['lag'] == 'lag-1':
            lag_explanation = "\n\n**Timing note:** The strongest correlation appears with storm activity from 1 week prior, rather than same-week storms."
        
        # Show both same-week and lag-1 if different
        comparison_text = ""
        if corr_same_week and corr_lag1:
            comparison_text = f"\n\n**Timing comparison:**\n- Same week: r = {corr_same_week['pearson_r']:.3f}\n- 1 week prior: r = {corr_lag1['pearson_r']:.3f}"
        
        st.markdown(f"""
This outcome shows a **{direction} correlation** with magnetic storm activity.
{outcome_text} were {explanation} — approximately **{abs(diff):.0f} {'more' if diff > 0 else 'fewer'} per week**
compared to quiet weeks.{lag_explanation}{comparison_text}

The effect is small, explaining ~{corr_data['r_squared']*100:.1f}% of variation.
Other factors likely account for most of the observed patterns.
""")
    else:
        st.warning(f"No significant correlation data available for {selected_outcome_label}")

with col2:
    st.info("""
    **Correlation vs Causation**
    
    Ice cream sales and drowning deaths both increase in summer, but ice cream doesn't 
    cause drowning — heat causes both.
    
    Similarly, a third factor could explain these correlations.
    """)

# Show caveat banner (full version on landing page only)
show_caveat_banner(mode='full')

st.divider()

# Visual: Simple Bar Comparison for selected outcome
st.markdown(f"## 📊 Visual Summary: {selected_outcome_label}")

comp_data = summary_stats['outcome_comparisons'][selected_outcome]
if comp_data['storm_weeks_mean'] and comp_data['no_storm_weeks_mean']:
    fig = create_comparison_bar_chart(
        comp_data['storm_weeks_mean'],
        comp_data['no_storm_weeks_mean'],
        outcome=selected_outcome
    )
    st.plotly_chart(fig, use_container_width=True)
    
    diff = comp_data['difference']
    pct_change = (abs(diff) / comp_data['no_storm_weeks_mean'] * 100) if comp_data['no_storm_weeks_mean'] > 0 else 0
    
    st.markdown(f"""
**What this shows:** On average, weeks with geomagnetic storms (Kp ≥ 5) had
**{comp_data['storm_weeks_mean']:.0f} deaths**,
compared to **{comp_data['no_storm_weeks_mean']:.0f} deaths**
during quiet weeks. That's a difference of about
**{abs(diff):.0f} deaths** (~{pct_change:.1f}% {'increase' if diff > 0 else 'decrease'}).
""")

st.divider()

# Add multi-outcome comparison
st.markdown("## Quick Comparison Across All Outcomes")

st.markdown("""
Four outcomes tested to assess specificity of magnetic-health correlations.
""")

explain_outcome_types()
explain_mixed_results()

fig_multi = create_multi_outcome_comparison(summary_stats)
st.plotly_chart(fig_multi, use_container_width=True)

st.markdown("""
**Observed patterns:**
- **Suicide**: Positive correlation (r ≈ 0.23)
- **Violence**: Negative correlation (r ≈ -0.16)
- **Overdose**: No significant correlation
- **Cardiovascular**: Negative correlation (r ≈ -0.16)

**Interpretation:**

Mixed results are informative. If all outcomes showed identical patterns, confounding or 
measurement artifact would be likely.

**Possible mechanisms:**
- **Suicide (positive)**: Circadian/melatonin pathway - storms may disrupt sleep cycles, 
  worsening mood in vulnerable individuals
  
- **Violence (negative)**: Behavioral - storms may cause lethargy or keep people indoors, 
  reducing interpersonal violence opportunities
  
- **Cardiovascular (negative)**: Weather confounding - storms often bring cooler temperatures
  
- **Overdose (none)**: Primarily driven by substance use disorders, less sensitive to 
  acute environmental changes

Outcome specificity suggests different biological or environmental pathways rather than 
simple universal effect.
""")

# Explanation expander
st.divider()
explain_correlation()

# Navigation
st.markdown("---")
st.markdown("## Additional Pages")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Overview Dashboard**
    
    Detailed statistics and correlation tables
    """)

with col2:
    st.markdown("""
    **Deep Dive**
    
    Time series, scatter plots, seasonal patterns
    """)

with col3:
    st.markdown("""
    **Interactive Explorer**
    
    Customize parameters and filters
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 14px;">
    <p>Data Sources: <a href="https://wonder.cdc.gov/controller/datarequest/D176">CDC WONDER</a> |
       <a href="https://kp.gfz.de/app/files/Kp_ap_since_1932.txt">GFZ Potsdam</a></p>
    <p>Study Period: January 2018 - June 2025 | 4 Outcomes Analyzed</p>
    <p><a href="https://www.freepik.com/free-psd/fiery-celestial-orb-glowing-lunar-display_408655936.htm#fromView=keyword&page=1&position=0&uuid=2121f2e0-bcdc-489b-8d37-0005eadeaf38&query=Orange+sun">Image by tohamina on Freepik</a></p>
</div>
""", unsafe_allow_html=True)

