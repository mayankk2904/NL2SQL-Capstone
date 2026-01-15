import os
import sys
import webbrowser
import subprocess
from datetime import datetime

def create_pdf_from_browser():
    """Create PDF by printing HTML page to PDF"""
    
    print("Generating coverage report...")
    

    if not os.path.exists("htmlcov") or not os.path.exists("htmlcov/index.html"):
        print("No coverage data found. Running tests...")
        subprocess.run([sys.executable, "-m", "pytest", "--cov=app", "--cov-report=html"])
    

    html_file = "coverage_for_pdf.html"
    
    with open("htmlcov/index.html", 'r', encoding='utf-8') as f:
        html_content = f.read()
    

    enhanced_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>NL2SQL Coverage Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; }}
        .meta {{ color: #7f8c8d; font-size: 14px; margin-bottom: 30px; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .print-button {{ 
            background: #3498db; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer;
            margin-bottom: 20px;
            font-size: 16px;
        }}
        .print-button:hover {{ background: #2980b9; }}
        @media print {{
            .print-button {{ display: none; }}
            body {{ margin: 0; }}
            .summary {{ display: none; }}
        }}
        .coverage-section {{ 
            background: white; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            padding: 15px; 
            margin: 20px 0;
        }}
        .coverage-high {{ color: #27ae60; font-weight: bold; }}
        .coverage-medium {{ color: #f39c12; font-weight: bold; }}
        .coverage-low {{ color: #e74c3c; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NL2SQL Project - Test Coverage Report</h1>
        <div class="meta">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Project: Natural Language to SQL API
        </div>
    </div>
    
    <button class="print-button" onclick="window.print()">Save as PDF</button>
    
    <div class="summary">
        <h3>How to Save as PDF:</h3>
        <ol>
            <li>Click the "Save as PDF" button above</li>
            <li>In print dialog, choose "Save as PDF" as destination</li>
            <li>Set margins to "None" or "Minimum" for best results</li>
            <li>Uncheck headers/footers if desired</li>
            <li>Click Save</li>
        </ol>
        <p><strong>Tip:</strong> For best results, use Chrome or Edge browser.</p>
    </div>
    
    {html_content}
    
    <script>
        // Add print functionality
        document.addEventListener('DOMContentLoaded', function() {{
            // Add page break before coverage details for better PDF
            var coverageHeader = document.querySelector('h1:contains("Coverage report")');
            if (coverageHeader) {{
                coverageHeader.style.pageBreakBefore = 'always';
            }}
        }});
    </script>
</body>
</html>"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_html)
    
    print(f"Report generated: {html_file}")
    print("\nTo create PDF:")
    print("   1. Open the HTML file in Chrome/Edge")
    print("   2. Press Ctrl+P (Windows) or Cmd+P (Mac)")
    print("   3. Choose 'Save as PDF' as destination")
    print("   4. Click Save")
    
    try:
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
    except:
        print(f"Could not open browser. Please manually open: {os.path.abspath(html_file)}")
    
    return html_file

if __name__ == "__main__":
    create_pdf_from_browser()