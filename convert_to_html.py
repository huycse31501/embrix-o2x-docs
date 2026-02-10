#!/usr/bin/env python3
"""
Convert Embrix O2X Markdown Documentation to HTML
"""

import re
import os
from pathlib import Path

# CSS template for all HTML pages
CSS_TEMPLATE = """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        background: #f5f5f5;
        padding: 20px;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
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
        font-size: 1.5em;
        margin-bottom: 5px;
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
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #667eea;
        font-size: 2.5em;
    }

    h2 {
        color: #764ba2;
        margin: 25px 0 15px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #f0f0f0;
        font-size: 2em;
    }

    h3 {
        color: #667eea;
        margin: 20px 0 10px 0;
        font-size: 1.5em;
    }

    h4 {
        color: #764ba2;
        margin: 15px 0 10px 0;
        font-size: 1.2em;
    }

    p {
        margin: 15px 0;
        line-height: 1.8;
    }

    ul, ol {
        margin: 15px 0;
        padding-left: 30px;
    }

    li {
        margin: 8px 0;
        line-height: 1.6;
    }

    code {
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9em;
        color: #e83e8c;
    }

    pre {
        background: #2d2d2d;
        color: #f8f8f2;
        padding: 20px;
        border-radius: 8px;
        overflow-x: auto;
        margin: 20px 0;
        border-left: 4px solid #667eea;
    }

    pre code {
        background: none;
        color: #f8f8f2;
        padding: 0;
    }

    blockquote {
        border-left: 4px solid #667eea;
        padding-left: 20px;
        margin: 20px 0;
        color: #666;
        font-style: italic;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-radius: 8px;
        overflow: hidden;
        background: white;
    }

    thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    th {
        color: white;
        padding: 15px 12px;
        text-align: left;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85em;
        letter-spacing: 0.5px;
    }

    td {
        padding: 12px;
        border-bottom: 1px solid #e0e0e0;
        vertical-align: top;
    }

    tbody tr:last-child td {
        border-bottom: none;
    }

    tbody tr:hover {
        background: #f8f9fa;
        transition: background 0.2s ease;
    }

    tbody tr:nth-child(even) {
        background: #fafafa;
    }

    tbody tr:nth-child(even):hover {
        background: #f0f0f0;
    }

    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 20px 0;
        border-radius: 5px;
    }

    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 20px 0;
        border-radius: 5px;
    }

    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 20px 0;
        border-radius: 5px;
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
    
    # Escape HTML in code blocks first
    def escape_code_block(match):
        code = match.group(1)
        code = code.replace('<', '&lt;').replace('>', '&gt;')
        lang = match.group(2) if match.lastindex >= 2 else ''
        if lang:
            return f'<pre><code class="language-{lang}">{code}</code></pre>'
        return f'<pre><code>{code}</code></pre>'
    
    # Process code blocks (```)
    markdown_text = re.sub(r'```(\w+)?\n(.*?)```', 
                          lambda m: f'<pre><code class="language-{m.group(1) or ""}">{m.group(2).replace("<", "&lt;").replace(">", "&gt;")}</code></pre>', 
                          markdown_text, flags=re.DOTALL)
    
    # Headers
    markdown_text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', markdown_text, flags=re.MULTILINE)
    markdown_text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', markdown_text, flags=re.MULTILINE)
    
    # Bold and italic
    markdown_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', markdown_text)
    markdown_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', markdown_text)
    
    # Inline code
    markdown_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', markdown_text)
    
    # Links
    markdown_text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', markdown_text)
    
    # Tables - Process before lists
    lines = markdown_text.split('\n')
    result = []
    in_list = False
    in_ordered_list = False
    in_table = False
    is_header_row = True
    
    for i, line in enumerate(lines):
        # Table detection
        if line.strip().startswith('|') and line.strip().endswith('|'):
            # Skip separator rows (e.g., |---|---|)
            if re.match(r'^\s*\|[\s\-:]+\|\s*$', line):
                is_header_row = False
                continue
            
            if not in_table:
                result.append('<table>')
                in_table = True
                is_header_row = True
            
            # Close any open lists
            if in_list:
                result.append('</ul>')
                in_list = False
            if in_ordered_list:
                result.append('</ol>')
                in_ordered_list = False
            
            # Parse table row
            cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
            
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
        # Unordered list
        elif re.match(r'^- ', line):
            if in_table:
                result.append('</tbody></table>')
                in_table = False
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{line[2:]}</li>')
        # Ordered list
        elif re.match(r'^\d+\. ', line):
            if in_table:
                result.append('</tbody></table>')
                in_table = False
            if not in_ordered_list:
                result.append('<ol>')
                in_ordered_list = True
            list_item_text = re.sub(r'^\d+\. ', '', line)
            result.append(f'<li>{list_item_text}</li>')
        else:
            if in_table:
                result.append('</tbody></table>')
                in_table = False
            if in_list:
                result.append('</ul>')
                in_list = False
            if in_ordered_list:
                result.append('</ol>')
                in_ordered_list = False
            result.append(line)
    
    if in_table:
        result.append('</tbody></table>')
    if in_list:
        result.append('</ul>')
    if in_ordered_list:
        result.append('</ol>')
    
    markdown_text = '\n'.join(result)
    
    # Horizontal rules
    markdown_text = re.sub(r'^---$', '<hr>', markdown_text, flags=re.MULTILINE)
    
    # Paragraphs
    markdown_text = re.sub(r'\n\n+', '</p><p>', markdown_text)
    markdown_text = '<p>' + markdown_text + '</p>'
    
    # Clean up empty paragraphs
    markdown_text = re.sub(r'<p>\s*</p>', '', markdown_text)
    markdown_text = re.sub(r'<p>\s*(<h[1-6]>)', r'\1', markdown_text)
    markdown_text = re.sub(r'(</h[1-6]>)\s*</p>', r'\1', markdown_text)
    markdown_text = re.sub(r'<p>\s*(<pre>)', r'\1', markdown_text)
    markdown_text = re.sub(r'(</pre>)\s*</p>', r'\1', markdown_text)
    markdown_text = re.sub(r'<p>\s*(<ul>|<ol>|<hr>|<table>)', r'\1', markdown_text)
    markdown_text = re.sub(r'(</ul>|</ol>|<hr>|</table>)\s*</p>', r'\1', markdown_text)
    
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
