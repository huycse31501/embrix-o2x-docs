#!/usr/bin/env python3
"""
Convert Embrix O2X Markdown Documentation to HTML
"""

import re
import os
from pathlib import Path

# CSS template for all HTML pages
CSS_TEMPLATE = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-size: 16px;
        line-height: 1.7;
        color: #1f2937;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
        padding: 20px;
        min-height: 100vh;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: rgba(255, 255, 255, 0.98);
        padding: 40px 50px;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.2), 0 0 100px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }

    .container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 8px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);
    }
    
    .container::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 40%;
        height: 200%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
        transform: rotate(-15deg);
        pointer-events: none;
    }

    .nav-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        padding: 25px 30px;
        border-radius: 20px;
        margin-bottom: 35px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3), inset 0 1px 0 rgba(255,255,255,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .nav-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 40%;
        height: 200%;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        transform: rotate(-15deg);
    }

    .nav-header h1 {
        font-size: 1.5em;
        margin-bottom: 5px;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }

    .nav-links {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }

    .nav-links a {
        color: white;
        text-decoration: none;
        padding: 10px 18px;
        background: rgba(255,255,255,0.15);
        border-radius: 10px;
        transition: all 0.3s ease;
        font-weight: 500;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        font-size: 0.9em;
    }
    
    .nav-links a::after {
        display: none;
    }

    .nav-links a:hover {
        background: white;
        color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    h1 {
        color: white;
        margin: 35px 0 25px 0;
        padding: 20px 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-size: 1.9em;
        font-weight: 700;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3), 0 0 60px rgba(102, 126, 234, 0.1);
        border: 3px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
        transform: translateY(0);
        transition: all 0.3s ease;
    }
    
    h1::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    h1:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4), 0 0 80px rgba(102, 126, 234, 0.15);
    }
    
    h1:hover::before {
        left: 100%;
    }

    h2 {
        color: #764ba2;
        margin: 30px 0 20px 0;
        padding: 16px 20px;
        background: linear-gradient(135deg, rgba(118, 75, 162, 0.08) 0%, rgba(240, 147, 251, 0.08) 100%);
        border-left: 6px solid #764ba2;
        border-radius: 12px;
        font-size: 1.6em;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.15);
        position: relative;
        transition: all 0.3s ease;
    }
    
    h2::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 0;
        height: 3px;
        background: linear-gradient(90deg, #764ba2 0%, #f093fb 100%);
        transition: width 0.4s ease;
    }
    
    h2:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.25);
    }
    
    h2:hover::after {
        width: 100%;
    }

    h3 {
        color: #667eea;
        margin: 25px 0 15px 0;
        padding: 14px 18px;
        background: white;
        border: 2px solid #667eea;
        border-radius: 10px;
        font-size: 1.3em;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    h3:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
        border-color: #764ba2;
        transform: translateX(3px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }

    h4 {
        color: #764ba2;
        margin: 20px 0 12px 0;
        padding: 6px 0 6px 10px;
        border-left: 2px solid #764ba2;
        background: linear-gradient(90deg, rgba(118, 75, 162, 0.03) 0%, transparent 100%);
        font-size: 1.1em;
        font-weight: 600;
        border-radius: 0 4px 4px 0;
    }

    h5 {
        color: #667eea;
        margin: 18px 0 10px 0;
        padding: 4px 0 4px 8px;
        border-left: 2px solid #667eea;
        font-size: 1.05em;
        font-weight: 600;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.02) 0%, transparent 100%);
        border-radius: 0 3px 3px 0;
    }

    h6 {
        color: #764ba2;
        margin: 15px 0 8px 0;
        font-size: 0.95em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    p {
        margin: 16px 0;
        line-height: 1.8;
        font-size: 1em;
        color: #374151;
    }
    
    /* Better spacing for paragraphs after headings */
    h1 + p, h2 + p, h3 + p, h4 + p {
        margin-top: 12px;
    }
    
    /* First paragraph after heading gets special treatment */
    h1 + p, h2 + p {
        font-size: 1.05em;
        color: #4b5563;
        font-weight: 400;
    }

    ul, ol {
        margin: 20px 0;
        padding-left: 15px;
        list-style: none;
    }

    li {
        margin: 12px 0;
        line-height: 1.7;
        font-size: 0.95em;
        position: relative;
        padding: 14px 18px 14px 50px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    ul li::before {
        content: '▸';
        position: absolute;
        left: 18px;
        color: white;
        font-weight: bold;
        font-size: 1.3em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        width: 24px;
        height: 24px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
        box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
    }
    
    ol {
        counter-reset: item;
    }
    
    /* Only number top-level items in ordered lists, not nested bullets */
    ol > li::before {
        content: counter(item);
        counter-increment: item;
        position: absolute;
        left: 18px;
        color: white;
        font-weight: 700;
        font-size: 0.9em;
        background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
        width: 24px;
        height: 24px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(118, 75, 162, 0.3);
    }

    li:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
        border-left-width: 6px;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.03) 0%, white 100%);
    }

    /* Nested lists */
    li ul, li ol {
        margin: 12px 0 8px 0;
        padding-left: 10px;
    }

    /* Nested list items - smaller styling */
    li li {
        font-size: 0.92em;
        margin: 8px 0;
        padding: 10px 14px 10px 40px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        border-left-color: #764ba2;
    }
    
    li li::before {
        width: 20px;
        height: 20px;
        font-size: 0.85em;
        left: 12px;
    }

    li li:hover {
        border-left-color: #f093fb;
    }

    code {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Fira Code', 'Courier New', Consolas, monospace;
        font-size: 0.85em;
        color: #d63384;
        border: 1px solid #dee2e6;
        font-weight: 500;
    }

    /* Inline code with special highlighting */
    p code, li code, td code {
        position: relative;
    }

    p code::before, li code::before, td code::before {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: 5px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        z-index: -1;
        opacity: 0;
        transition: opacity 0.2s;
    }

    p code:hover::before, li code:hover::before, td code:hover::before {
        opacity: 1;
    }

    pre {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #e2e8f0;
        padding: 24px;
        border-radius: 16px;
        overflow-x: auto;
        margin: 25px 0;
        border: 2px solid #334155;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
        font-family: 'Cascadia Code', 'Fira Code', 'SF Mono', 'Consolas', 'Liberation Mono', monospace;
        font-size: 0.88em;
        line-height: 1.7;
        position: relative;
        font-feature-settings: "liga" 0;
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    pre::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 35px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border-radius: 14px 14px 0 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    pre code {
        background: none;
        color: inherit;
        padding: 0;
        border: none;
        font-family: inherit;
        font-weight: normal;
        font-size: 1em;
        display: block;
        padding-top: 35px;
    }
    
    /* Ensure consistent styling for all code content inside pre blocks */
    pre code * {
        font-size: inherit !important;
        line-height: inherit !important;
        color: inherit !important;
        font-family: inherit !important;
    }

    /* Hover effect */
    pre:hover {
        border-color: #667eea;
        box-shadow: 0 12px 35px rgba(0,0,0,0.4), 0 0 0 2px rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    /* Code block header indicator with dots */
    pre::after {
        content: '';
        position: absolute;
        top: 14px;
        left: 16px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #ff5f56;
        box-shadow: 20px 0 0 #ffbd2e, 40px 0 0 #27c93f;
    }

    blockquote {
        border-left: 6px solid #667eea;
        padding: 22px 28px 22px 60px;
        margin: 25px 0;
        color: #555;
        font-style: italic;
        font-size: 1em;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(240, 147, 251, 0.05) 100%);
        border-radius: 16px;
        position: relative;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }

    blockquote::before {
        content: '"';
        position: absolute;
        left: 18px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 3em;
        color: rgba(102, 126, 234, 0.2);
        font-family: Georgia, serif;
        font-weight: 700;
        line-height: 1;
    }
    
    blockquote:hover {
        border-left-color: #764ba2;
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
    }

    table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 25px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-radius: 16px;
        overflow: hidden;
        background: white;
        font-size: 0.9em;
        border: 2px solid rgba(102, 126, 234, 0.1);
    }

    thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        position: relative;
    }
    
    thead::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #f093fb 0%, transparent 50%, #f093fb 100%);
    }

    th {
        color: white;
        padding: 16px 18px;
        text-align: left;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.8em;
        letter-spacing: 0.5px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }

    td {
        padding: 14px 18px;
        border-bottom: 1px solid rgba(102, 126, 234, 0.08);
        vertical-align: top;
        line-height: 1.6;
        transition: all 0.2s ease;
    }

    tbody tr:last-child td {
        border-bottom: none;
    }

    tbody tr {
        transition: all 0.3s ease;
    }

    tbody tr:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.08) 0%, rgba(240, 147, 251, 0.05) 100%);
        transform: scale(1.01);
        box-shadow: inset 4px 0 0 #667eea;
    }

    tbody tr:nth-child(even) {
        background: rgba(102, 126, 234, 0.02);
    }

    tbody tr:nth-child(even):hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.08) 0%, rgba(240, 147, 251, 0.05) 100%);
    }
    
    /* Better code in tables */
    td code {
        font-size: 0.85em;
        padding: 3px 7px;
    }

    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 3px solid #2196f3;
        padding: 24px;
        margin: 30px 0;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.25);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .info-box::before {
        content: 'ℹ️';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 2em;
        opacity: 0.3;
    }
    
    .info-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(33, 150, 243, 0.35);
    }

    .warning-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border: 3px solid #ff9800;
        padding: 24px;
        margin: 30px 0;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(255, 152, 0, 0.25);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .warning-box::before {
        content: '⚠️';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 2em;
        opacity: 0.3;
    }
    
    .warning-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(255, 152, 0, 0.35);
    }

    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border: 3px solid #4caf50;
        padding: 24px;
        margin: 30px 0;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.25);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .success-box::before {
        content: '✅';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 2em;
        opacity: 0.3;
    }
    
    .success-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(76, 175, 80, 0.35);
    }

    /* Better colors for syntax in diagrams */
    pre {
        /* Box drawing characters in nice blue */
        color: #93c5fd;
    }

    /* JSON/code syntax in pre blocks */
    pre {
        white-space: pre;
        word-wrap: normal;
    }

    .toc {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        border-left: 4px solid #667eea;
    }

    .toc h2 {
        color: #667eea;
        border-bottom: none;
        margin-bottom: 15px;
    }

    .toc ul {
        list-style: none;
        padding-left: 0;
    }

    .toc li {
        margin: 8px 0;
    }

    .toc a {
        color: #667eea;
        text-decoration: none;
        transition: color 0.3s;
    }

    .toc a:hover {
        color: #764ba2;
    }

    hr {
        border: none;
        border-top: 2px solid #f0f0f0;
        margin: 30px 0;
    }

    .badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85em;
        margin-left: 10px;
    }

    a {
        color: #667eea;
        text-decoration: none;
        position: relative;
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 2px 0;
    }
    
    a::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        transition: width 0.3s ease;
    }

    a:hover {
        color: #764ba2;
    }
    
    a:hover::after {
        width: 100%;
    }
    
    /* Better display for metadata fields */
    strong {
        color: #374151;
        font-weight: 600;
    }
    
    /* Metadata field styling - each field on its own line */
    .metadata-field {
        margin: 8px 0;
        padding: 8px 14px;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.04) 0%, transparent 100%);
        border-left: 3px solid #667eea;
        border-radius: 0 4px 4px 0;
        line-height: 1.7;
        font-size: 0.95em;
        display: block;
        clear: both;
    }
    
    .metadata-field strong {
        color: #667eea;
        font-weight: 600;
        margin-right: 8px;
        display: inline-block;
        min-width: 100px;
    }
    
    .metadata-field code {
        font-size: 0.88em;
    }

    footer {
        margin-top: 50px;
        padding-top: 30px;
        border-top: 2px solid #f0f0f0;
        text-align: center;
        color: #888;
    }

    @media print {
        body {
            background: white;
        }
        .nav-header, .nav-links {
            display: none;
        }
        pre {
            break-inside: avoid;
        }
    }

    @media (max-width: 768px) {
        .container {
            padding: 20px;
        }
        .nav-header {
            flex-direction: column;
            align-items: flex-start;
        }
        .nav-links {
            margin-top: 15px;
        }
        h1 {
            font-size: 2em;
        }
        h2 {
            font-size: 1.5em;
        }
    }
</style>
"""

def convert_markdown_to_html(markdown_text, title, nav_links=None):
    """Convert markdown text to HTML with styling"""
    
    # STEP 1: Extract and protect code blocks from further processing
    code_blocks = []
    code_block_placeholder = "___CODE_BLOCK_{}_PLACEHOLDER___"
    
    def extract_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        # Escape HTML entities
        code = code.replace('<', '&lt;').replace('>', '&gt;')
        # Store the processed code block
        block_html = f'<pre><code class="language-{lang}">{code}</code></pre>'
        placeholder = code_block_placeholder.format(len(code_blocks))
        code_blocks.append(block_html)
        return placeholder
    
    # Extract all code blocks (```)
    markdown_text = re.sub(r'```(\w+)?\n(.*?)```', 
                          extract_code_block, 
                          markdown_text, flags=re.DOTALL)
    
    # STEP 2: Now process headers (safe because code blocks are protected)
    # Headers (must process from most specific to least specific to avoid conflicts)
    markdown_text = re.sub(r'^###### (.*?)$', r'<h6>\1</h6>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^##### (.*?)$', r'<h5>\1</h5>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', markdown_text, flags=re.MULTILINE)
    
    # CRITICAL: Mark metadata fields BEFORE bold processing
    # This ensures Location:, Artifact:, Purpose: etc. get proper wrapping
    # Pattern matches: **FieldName:** followed by any content until end of line
    # Use [^\r\n]* instead of .* to avoid matching across line boundaries
    metadata_pattern = r'^\*\*(Location|Artifact|Purpose|Port|Technology|Internal Name|Why (?:Important|Critical)|What is|Key (?:Operations|Concepts|Jobs|Features)|GraphQL Operations):\*\*[ \t]*([^\r\n]*)$'
    
    def metadata_replacer(match):
        field_name = match.group(1)
        field_value = match.group(2).strip()
        return f'{{{{METADATA_START}}}}{field_name}{{{{METADATA_MID}}}}{field_value}{{{{METADATA_END}}}}'
    
    markdown_text = re.sub(
        metadata_pattern,
        metadata_replacer,
        markdown_text,
        flags=re.MULTILINE
    )
    
    # Bold and italic
    markdown_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', markdown_text)
    markdown_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', markdown_text)
    
    # Inline code
    markdown_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', markdown_text)
    
    # Links
    markdown_text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', markdown_text)
    
    # Tables and Lists - Process with proper nesting
    lines = markdown_text.split('\n')
    result = []
    in_list = False
    in_ordered_list = False
    in_table = False
    is_header_row = True
    current_list_item = []  # Buffer for multi-line list items
    
    def flush_list_item():
        """Flush buffered list item content"""
        if current_list_item:
            content = '<br>'.join(current_list_item)
            result.append(f'<li>{content}</li>')
            current_list_item.clear()
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        indent_level = len(line) - len(line.lstrip())
        
        # Detect metadata field markers - these should be isolated
        if '{{METADATA_START}}' in line:
            # Close any open lists before metadata field
            if in_list or in_ordered_list:
                flush_list_item()
            if in_list:
                result.append('</ul>')
                in_list = False
            if in_ordered_list:
                result.append('</ol>')
                in_ordered_list = False
            if in_table:
                result.append('</tbody></table>')
                in_table = False
            
            # Add metadata field line as-is
            result.append(line)
            continue
        
        # Table detection
        if stripped.startswith('|') and stripped.endswith('|'):
            # Skip separator rows (e.g., |---|---|)
            if re.match(r'^\s*\|[\s\-:]+\|\s*$', line):
                is_header_row = False
                continue
            
            # Close any open lists
            if in_list or in_ordered_list:
                flush_list_item()
            if in_list:
                result.append('</ul>')
                in_list = False
            if in_ordered_list:
                result.append('</ol>')
                in_ordered_list = False
            
            if not in_table:
                result.append('<table>')
                in_table = True
                is_header_row = True
            
            # Parse table row
            cells = [cell.strip() for cell in stripped.split('|')[1:-1]]
            
            if is_header_row:
                result.append('<thead><tr>')
                for cell in cells:
                    result.append(f'<th>{cell}</th>')
                result.append('</tr></thead><tbody>')
                is_header_row = False
            else:
                result.append('<tr>')
                for cell in cells:
                    result.append(f'<td>{cell}</td>')
                result.append('</tr>')
        
        # Ordered list (not indented)
        elif re.match(r'^\d+\. ', line) and indent_level == 0:
            if in_table:
                result.append('</tbody></table>')
                in_table = False
            
            # Flush previous list item
            if in_ordered_list:
                flush_list_item()
            
            # Close unordered list if switching types
            if in_list:
                result.append('</ul>')
                in_list = False
            
            # Start ordered list if needed
            if not in_ordered_list:
                result.append('<ol>')
                in_ordered_list = True
            
            # Extract list item content
            list_item_text = re.sub(r'^\d+\. ', '', line)
            current_list_item.append(list_item_text)
        
        # Unordered list (not indented)
        elif re.match(r'^- ', line) and indent_level == 0:
            if in_table:
                result.append('</tbody></table>')
                in_table = False
            
            # Flush previous list item
            if in_list:
                flush_list_item()
            
            # Close ordered list if switching types
            if in_ordered_list:
                flush_list_item()
                result.append('</ol>')
                in_ordered_list = False
            
            # Start unordered list if needed
            if not in_list:
                result.append('<ul>')
                in_list = True
            
            current_list_item.append(line[2:])
        
        # Indented content (nested bullets or continuation)
        elif indent_level > 0 and (in_list or in_ordered_list) and stripped:
            # This is nested content of the current list item
            if stripped.startswith('- '):
                # Nested bullet point
                current_list_item.append(f'<ul><li>{stripped[2:]}</li></ul>')
            else:
                # Continuation of list item
                current_list_item.append(stripped)
        
        # Empty line within list - might be separating items
        elif not stripped and (in_list or in_ordered_list):
            # Keep empty lines within lists (don't close yet)
            continue
        
        # Non-list content
        else:
            # Close any open structures
            if in_table:
                result.append('</tbody></table>')
                in_table = False
            if in_list or in_ordered_list:
                flush_list_item()
            if in_list:
                result.append('</ul>')
                in_list = False
            if in_ordered_list:
                result.append('</ol>')
                in_ordered_list = False
            
            if stripped:  # Only add non-empty lines
                result.append(line)
    
    # Close any remaining open structures
    if in_list or in_ordered_list:
        flush_list_item()
    if in_table:
        result.append('</tbody></table>')
    if in_list:
        result.append('</ul>')
    if in_ordered_list:
        result.append('</ol>')
    
    markdown_text = '\n'.join(result)
    
    # Horizontal rules
    markdown_text = re.sub(r'^---+$', '<hr>', markdown_text, flags=re.MULTILINE)
    
    # Paragraphs - split on double newlines but not inside lists/tables
    markdown_text = re.sub(r'\n\n+', '\n</p>\n<p>\n', markdown_text)
    markdown_text = '<p>' + markdown_text + '</p>'
    
    # Clean up empty paragraphs and malformed tags
    markdown_text = re.sub(r'<p>\s*</p>', '', markdown_text)
    markdown_text = re.sub(r'<p>\s*(<h[1-6]>)', r'\n\1', markdown_text)
    markdown_text = re.sub(r'(</h[1-6]>)\s*</p>', r'\1\n', markdown_text)
    markdown_text = re.sub(r'<p>\s*(<pre>)', r'\n\1', markdown_text)
    markdown_text = re.sub(r'(</pre>)\s*</p>', r'\1\n', markdown_text)
    markdown_text = re.sub(r'<p>\s*(<ul>|<ol>|<hr>|<table>)', r'\n\1', markdown_text)
    markdown_text = re.sub(r'(</ul>|</ol>|<hr>|</table>)\s*</p>', r'\1\n', markdown_text)
    markdown_text = re.sub(r'<p>\s*(<thead>|<tbody>)', r'\1', markdown_text)
    markdown_text = re.sub(r'(</thead>|</tbody>)\s*</p>', r'\1', markdown_text)
    
    # CRITICAL: Convert metadata markers to proper div wrappers AFTER paragraph processing
    # Handle cases with paragraph wrapper
    markdown_text = re.sub(
        r'<p>\s*{{METADATA_START}}([^{]+){{METADATA_MID}}([^{]*){{METADATA_END}}\s*</p>',
        r'<div class="metadata-field"><strong>\1:</strong> \2</div>',
        markdown_text
    )
    # Also handle cases without paragraph wrapper
    markdown_text = re.sub(
        r'{{METADATA_START}}([^{]+){{METADATA_MID}}([^{]*){{METADATA_END}}',
        r'<div class="metadata-field"><strong>\1:</strong> \2</div>',
        markdown_text
    )
    # Clean up any remaining paragraph tags around metadata fields
    markdown_text = re.sub(r'<p>\s*(<div class="metadata-field">)', r'\1', markdown_text)
    markdown_text = re.sub(r'(</div>)\s*</p>', r'\1', markdown_text)
    
    
    # Add spacing after headers
    markdown_text = re.sub(r'(</h[1-6]>)', r'\1\n', markdown_text)
    
    # Add spacing around hr
    markdown_text = re.sub(r'<hr>', r'\n<hr>\n', markdown_text)
    
    # STEP 3: Restore code blocks (protected content)
    for i, code_block in enumerate(code_blocks):
        placeholder = code_block_placeholder.format(i)
        markdown_text = markdown_text.replace(placeholder, code_block)
    
    # Build navigation
    nav_html = ""
    if nav_links:
        nav_html = '<div class="nav-header">'
        nav_html += '<div><h1>Embrix O2X Documentation</h1><small>Navigate between guides</small></div>'
        nav_html += '<div class="nav-links">'
        for link_title, link_url in nav_links:
            nav_html += f'<a href="{link_url}">{link_title}</a>'
        nav_html += '</div></div>'
    
    # Build full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Embrix O2X</title>
    {CSS_TEMPLATE}
</head>
<body>
    <div class="container">
        {nav_html}
        {markdown_text}
        <footer>
            <p><strong>Embrix O2X Platform Documentation</strong></p>
            <p>Version 3.1.9-SNAPSHOT • Last Updated: February 2026</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html

def main():
    """Convert all markdown guides to HTML"""
    
    # Navigation links for all pages - will be at top of every page
    nav_links = [
        ("Home", "index.html"),
        ("Guide Index", "guide-index.html"),
        ("Part 1-5", "guide-index.html"),
        ("Quick Start", "quick-start.html"),
        ("Quick Ref", "quick-reference.html"),
        ("Architecture", "complete-system-overview.html"),
        ("API Reference", "api-reference.html"),
        ("Troubleshooting", "troubleshooting-guide.html"),
    ]
    
    # Files to convert - Knowledge Hub content only (no deployment docs)
    files_to_convert = [
        # Newcomer Guide Parts (from root and docs/newcomer-4/)
        ("docs/newcomer-4/NEWCOMER_GUIDE_INDEX.md", "guide-index.html", "📚 Complete Newcomer's Guide Index"),
        ("docs/newcomer-4/NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md", "part1-business-architecture.html", "Part 1: Business & Architecture"),
        ("docs/newcomer-4/NEWCOMER_GUIDE_PART2_TECHNICAL_DEEP_DIVE.md", "part2-technical-deep-dive.html", "Part 2: Technical Deep Dive"),
        ("NEWCOMER_GUIDE_PART3_SERVICES_AND_DEVELOPMENT.md", "part3-services-development.html", "Part 3: Services & Development"),
        ("docs/newcomer-4/NEWCOMER_GUIDE_PART4_FRONTEND_AND_UI.md", "part4-frontend-ui.html", "Part 4: Frontend Applications & User Interfaces"),
        ("docs/newcomer-4/NEWCOMER_GUIDE_PART5_MESSAGE_QUEUES_AND_INTEGRATION.md", "part5-message-queues.html", "Part 5: Message Queue Architecture & Integration"),
        
        # Quick Start and Reference Guides
        ("docs/newcomer-4/QUICK_START.md", "quick-start.html", "🎯 Quick Start Guide"),
        ("docs/newcomer-4/QUICK_REFERENCE_GUIDE.md", "quick-reference.html", "📖 Quick Reference Guide"),
        
        # Business and Workflow Guides
        ("docs/newcomer-4/BUSINESS_SCENARIOS_AND_WORKFLOWS.md", "business-scenarios.html", "💼 Business Scenarios & Workflows"),
        
        # Architecture Documentation
        ("docs/newcomer-4/MULTI_TENANT_ARCHITECTURE.md", "multi-tenant-architecture.html", "🏢 Multi-Tenant Architecture"),
        ("docs/newcomer-4/DATABASE_ARCHITECTURE_COMPLETE.md", "database-architecture.html", "🗄️ Database Architecture - Complete Guide"),
        ("docs/newcomer-4/FRONTEND_UI_ARCHITECTURE.md", "frontend-ui-architecture.html", "🎨 Frontend & UI Architecture"),
        
        # System Documentation
        ("docs/newcomer-4/COMPLETE_SYSTEM_OVERVIEW.md", "complete-system-overview.html", "🌐 Complete System Overview"),
        ("docs/newcomer-4/COMPLETE_SYSTEM_DOCUMENTATION.md", "complete-system-documentation.html", "📋 Complete System Documentation"),
        ("docs/newcomer-4/COMPLETE_SYSTEM_INVENTORY.md", "complete-system-inventory.html", "📦 Complete System Inventory"),
        ("docs/newcomer-4/COMPLETE_SERVICES_CATALOG.md", "complete-services-catalog.html", "⚙️ Complete Services Catalog"),
        
        # Development Guides
        ("docs/newcomer-4/API_REFERENCE.md", "api-reference.html", "🔌 API Reference"),
        ("docs/newcomer-4/FRONTEND_GUIDE.md", "frontend-guide.html", "💻 Frontend Development Guide"),
        ("docs/newcomer-4/CONTRIBUTING.md", "contributing.html", "🤝 Contributing Guide"),
        
        # Troubleshooting and Reference
        ("docs/newcomer-4/TROUBLESHOOTING_GUIDE.md", "troubleshooting-guide.html", "🔧 Troubleshooting Guide"),
        ("docs/newcomer-4/GLOSSARY.md", "glossary.html", "📖 Glossary of Terms"),
    ]
    
    # Output directory - docs/newcomer (primary HTML docs location)
    output_dir = Path("docs/newcomer")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    converted_count = 0
    skipped_count = 0
    
    for md_file, html_file, title in files_to_convert:
        md_path = Path(md_file)
        if not md_path.exists():
            print(f"Warning: {md_file} not found, skipping...")
            skipped_count += 1
            continue
        
        print(f"Converting {md_file} -> {html_file}...")
        
        with open(md_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        html_content = convert_markdown_to_html(markdown_content, title, nav_links)
        
        output_path = output_dir / html_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] Created {output_path}")
        converted_count += 1
    
    # Create index.html with beautiful landing page
    print("\nCreating index page...")
    index_content = """# Embrix O2X Knowledge Hub

Welcome to the **Embrix O2X Platform Knowledge Hub** - your comprehensive guide to mastering our enterprise-grade Order-to-Cash management system.

---

## Getting Started

New to Embrix O2X? Start with this:

- [Business Scenarios & Workflows](business-scenarios.html) - Real-world use cases and examples

---

## Learning Path

Follow this recommended sequence to master the platform:

1. [Part 1: Business & Architecture](part1-business-architecture.html) - Understand the business domain and high-level architecture
2. [Part 2: Technical Deep Dive](part2-technical-deep-dive.html) - Explore technical architecture and design patterns
3. [Part 3: Services & Development](part3-services-development.html) - Master microservices and backend development
4. [Part 4: Frontend Applications & User Interfaces](part4-frontend-ui.html) - Learn UI architecture and frontend patterns
5. [Part 5: Message Queue Architecture & Integration](part5-message-queues.html) - Understand async messaging and integration

---

## Architecture Documentation

Deep dive into system architecture and design:

- [Complete System Overview](complete-system-overview.html) - High-level system architecture and components
- [Multi-Tenant Architecture](multi-tenant-architecture.html) - Multi-tenancy design patterns and implementation
- [Database Architecture](database-architecture.html) - Data modeling, schema design, and database patterns
- [Frontend & UI Architecture](frontend-ui-architecture.html) - UI/UX patterns, components, and design system

---

## System Reference

Comprehensive documentation of all system components:

- [Complete System Documentation](complete-system-documentation.html) - Full system documentation
- [Complete System Inventory](complete-system-inventory.html) - All components, services, and dependencies
- [Complete Services Catalog](complete-services-catalog.html) - Detailed service descriptions and APIs

---

## Development Resources

Essential resources for developers:

- [API Reference](api-reference.html) - Complete REST API documentation
- [Frontend Development Guide](frontend-guide.html) - Frontend development best practices

---

## Troubleshooting & Support

Get help when you need it:

- [Troubleshooting Guide](troubleshooting-guide.html) - Common issues and solutions
- [Glossary of Terms](glossary.html) - Technical terminology and definitions

---

## Key Features

**Key Features:**
- Multi-tenant SaaS platform  
  See: [Complete System Overview](complete-system-overview.html), [Multi-Tenant Architecture](multi-tenant-architecture.html)
- Comprehensive Order-to-Cash workflow  
  See: [Business Scenarios & Workflows](business-scenarios.html)
- Real-time event processing  
  See: [Message Queues & Integration](part5-message-queues.html)
- Advanced pricing and taxation engines  
  See: [Technical Deep Dive](part2-technical-deep-dive.html)
- Self-service portal and admin interfaces  
  See: [Frontend & UI Architecture](frontend-ui-architecture.html)

---

Happy learning! Start your journey with the [Complete Newcomer's Guide Index](guide-index.html).
"""
    
    index_html = convert_markdown_to_html(index_content, "Embrix O2X Documentation Portal", nav_links)
    index_path = output_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"[OK] Created {index_path}")
    
    print("\n" + "="*60)
    print(f"SUCCESS! Converted {converted_count} files")
    if skipped_count > 0:
        print(f"Warning: Skipped {skipped_count} files (not found)")
    print(f"Output directory: {output_dir.absolute()}")
    print(f"Open: {index_path.absolute()}")
    print("="*60)

if __name__ == "__main__":
    main()
