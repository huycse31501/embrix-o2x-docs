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
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        background-attachment: fixed;
        padding: 20px;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        padding: 40px 50px;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }

    .container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    .nav-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }

    .nav-header h1 {
        font-size: 1.4em;
        margin-bottom: 5px;
        font-weight: 600;
    }

    .nav-links {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
    }

    .nav-links a {
        color: white;
        text-decoration: none;
        padding: 8px 16px;
        background: rgba(255,255,255,0.2);
        border-radius: 5px;
        transition: background 0.3s;
    }

    .nav-links a:hover {
        background: rgba(255,255,255,0.3);
    }

    h1 {
        color: #667eea;
        margin: 35px 0 20px 0;
        padding: 12px 0 12px 18px;
        border-left: 5px solid #667eea;
        border-bottom: 2px solid #667eea;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, rgba(255,255,255,0) 100%);
        font-size: 1.8em;
        font-weight: 700;
        border-radius: 0 8px 0 0;
    }

    h2 {
        color: #764ba2;
        margin: 30px 0 18px 0;
        padding: 10px 0 10px 15px;
        border-left: 4px solid #764ba2;
        border-bottom: 2px solid #f0f0f0;
        background: linear-gradient(90deg, rgba(118, 75, 162, 0.03) 0%, rgba(255,255,255,0) 100%);
        font-size: 1.5em;
        font-weight: 700;
        border-radius: 0 6px 0 0;
    }

    h3 {
        color: #667eea;
        margin: 25px 0 15px 0;
        padding: 8px 0 8px 12px;
        border-left: 3px solid #667eea;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.04) 0%, transparent 100%);
        font-size: 1.25em;
        font-weight: 600;
        border-radius: 0 6px 6px 0;
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
        margin: 12px 0;
        line-height: 1.7;
        font-size: 0.95em;
        color: #374151;
    }
    
    /* Better spacing for paragraphs after headings */
    h1 + p, h2 + p, h3 + p, h4 + p {
        margin-top: 10px;
    }

    ul, ol {
        margin: 20px 0;
        padding-left: 35px;
    }

    li {
        margin: 10px 0;
        line-height: 1.7;
        font-size: 0.95em;
        position: relative;
        padding-left: 8px;
    }

    ul li::marker {
        color: #667eea;
        font-weight: bold;
        font-size: 1.1em;
    }

    ol li::marker {
        color: #764ba2;
        font-weight: bold;
        font-size: 1em;
    }

    /* Better list item styling */
    li {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.02) 0%, transparent 100%);
        border-left: 2px solid transparent;
        padding: 8px 8px 8px 12px;
        border-radius: 0 4px 4px 0;
        transition: all 0.2s ease;
    }

    li:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
        border-left-color: #667eea;
        padding-left: 16px;
    }

    /* Nested lists */
    li ul, li ol {
        margin: 8px 0 8px 10px;
    }

    /* Nested list items - smaller styling */
    li li {
        font-size: 0.92em;
        margin: 6px 0;
        background: linear-gradient(90deg, rgba(118, 75, 162, 0.02) 0%, transparent 100%);
    }

    li li:hover {
        background: linear-gradient(90deg, rgba(118, 75, 162, 0.05) 0%, transparent 100%);
        border-left-color: #764ba2;
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
        background: #1e293b;
        color: #e2e8f0;
        padding: 16px 18px;
        border-radius: 8px;
        overflow-x: auto;
        margin: 18px 0;
        border: 1px solid #334155;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        font-family: 'Cascadia Code', 'Fira Code', 'SF Mono', 'Consolas', 'Liberation Mono', monospace;
        font-size: 0.85em;
        line-height: 1.6;
        position: relative;
        font-feature-settings: "liga" 0;
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
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
        border-color: #475569;
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
        transition: all 0.3s ease;
    }

    /* Code block header indicator */
    pre::after {
        content: 'CODE';
        position: absolute;
        top: 8px;
        right: 12px;
        font-size: 0.65em;
        color: #64748b;
        font-weight: 600;
        letter-spacing: 0.05em;
        opacity: 0.5;
    }

    blockquote {
        border-left: 4px solid #667eea;
        padding: 15px 20px;
        margin: 20px 0;
        color: #555;
        font-style: italic;
        font-size: 0.95em;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, rgba(255,255,255,0) 100%);
        border-radius: 0 6px 6px 0;
        position: relative;
    }

    blockquote::before {
        content: '"';
        position: absolute;
        left: -10px;
        top: -10px;
        font-size: 4em;
        color: rgba(102, 126, 234, 0.1);
        font-family: Georgia, serif;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        border-radius: 8px;
        overflow: hidden;
        background: white;
        font-size: 0.9em;
    }

    thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    th {
        color: white;
        padding: 12px 15px;
        text-align: left;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.82em;
        letter-spacing: 0.3px;
    }

    td {
        padding: 10px 15px;
        border-bottom: 1px solid #e5e7eb;
        vertical-align: top;
        line-height: 1.6;
    }

    tbody tr:last-child td {
        border-bottom: none;
    }

    tbody tr:hover {
        background: rgba(102, 126, 234, 0.04);
        transition: background 0.2s ease;
    }

    tbody tr:nth-child(even) {
        background: rgba(102, 126, 234, 0.02);
    }

    tbody tr:nth-child(even):hover {
        background: rgba(102, 126, 234, 0.05);
    }
    
    /* Better code in tables */
    td code {
        font-size: 0.85em;
        padding: 2px 6px;
    }

    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 5px solid #2196f3;
        padding: 20px;
        margin: 25px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
    }

    .warning-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 5px solid #ff9800;
        padding: 20px;
        margin: 25px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(255, 152, 0, 0.2);
    }

    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 5px solid #4caf50;
        padding: 20px;
        margin: 25px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
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
        transition: color 0.3s;
    }

    a:hover {
        color: #764ba2;
        text-decoration: underline;
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
    
    # Navigation links for all pages
    nav_links = [
        ("Home", "index.html"),
        ("Guide Index", "guide-index.html"),
        ("Part 1", "part1-business-architecture.html"),
        ("Part 2", "part2-technical-deep-dive.html"),
        ("Part 3", "part3-services-development.html"),
        ("Scenarios", "business-scenarios.html"),
        ("Multi-Tenant", "multi-tenant-complete-guide.html"),
        ("Quick Ref", "quick-reference.html")
    ]
    
    # Files to convert
    files_to_convert = [
        ("NEWCOMER_GUIDE_INDEX.md", "guide-index.html", "Complete Newcomer's Guide Index"),
        ("NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md", "part1-business-architecture.html", "Part 1: Business & Architecture"),
        ("NEWCOMER_GUIDE_PART2_TECHNICAL_DEEP_DIVE.md", "part2-technical-deep-dive.html", "Part 2: Technical Deep Dive"),
        ("NEWCOMER_GUIDE_PART3_SERVICES_AND_DEVELOPMENT.md", "part3-services-development.html", "Part 3: Services & Development"),
        ("BUSINESS_SCENARIOS_AND_WORKFLOWS.md", "business-scenarios.html", "Business Scenarios & Workflows"),
        ("QUICK_REFERENCE_GUIDE.md", "quick-reference.html", "Quick Reference Guide"),
        ("docs/MULTI_TENANT_COMPLETE_GUIDE.md", "multi-tenant-complete-guide.html", "Multi-Tenant Architecture - Complete Guide")
    ]
    
    output_dir = Path("docs/newcomer")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for md_file, html_file, title in files_to_convert:
        md_path = Path(md_file)
        if not md_path.exists():
            print(f"Warning: {md_file} not found, skipping...")
            continue
        
        print(f"Converting {md_file} to {html_file}...")
        
        with open(md_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        html_content = convert_markdown_to_html(markdown_content, title, nav_links)
        
        output_path = output_dir / html_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] Created {output_path}")
    
    print("\n[SUCCESS] All files converted successfully!")
    print(f"Output directory: {output_dir.absolute()}")
    print(f"Open: {(output_dir / 'index.html').absolute()}")

if __name__ == "__main__":
    main()
