"""Debug quiz.html for JS issues"""
import re

with open(r'c:\Users\Zhai\Desktop\热处理复习资料\quiz.html', 'r', encoding='utf-8') as f:
    html = f.read()

print(f"File size: {len(html)} chars")

# Check HTML structure
print(f"Doctype: {html[:50]}")
print(f"Ends with: {html[-50:]}")

# Find script blocks
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"Script blocks: {len(scripts)}")

main_js = scripts[-1] if scripts else ''

# Check for issues
# 1. Check backtick balance in main JS
bt_count = main_js.count('`')
print(f"Backtick count: {bt_count} (mod 2 = {bt_count % 2})")

# 2. Check for common template literal issues
# Look for lines with single backtick
lines = main_js.split('\n')
for i, line in enumerate(lines):
    cnt = line.count('`')
    if cnt % 2 != 0 and '`' in line:
        print(f"  Odd backtick line {i+1}: {line.strip()[:120]}")

# 3. Check for nested template issues in build script output
# The build script inserted JS template literals into Python strings
# Check for messed up escapes
problematic = [
    'optM = dq.match',
    'renderReviewQuestion',
    'getKPHint',
]
for p in problematic:
    if p in main_js:
        # Find the line
        for i, line in enumerate(lines):
            if p in line:
                print(f"\n--- {p} (line {i+1}) ---")
                # Print surrounding lines
                start = max(0, i-2)
                end = min(len(lines), i+5)
                for j in range(start, end):
                    marker = '>>>' if j == i else '   '
                    print(f"{marker} {j+1}: {lines[j][:150]}")
                break
    else:
        print(f"\nMISSING: {p}")

# 4. Check if the HTML has proper closing tags
if '</html>' in html:
    print("\nOK: </html> present")
else:
    print("\nERROR: Missing </html>")

if '</body>' in html:
    print("OK: </body> present")
else:
    print("ERROR: Missing </body>")

# 5. Check for the init block
if 'QUESTIONS.length === 0' in html:
    print("OK: Init block present")
else:
    print("ERROR: Init block missing")

if 'render();' in main_js:
    print("OK: render() call present")
else:
    print("ERROR: render() call missing")

# 6. Check for syntax error patterns
# Look for escaped characters that shouldn't be there
for pattern in [r'\\\\`', r'\\`', r'\\${']:
    matches = re.findall(pattern, main_js)
    if matches:
        print(f"WARNING: Found {len(matches)} occurrences of {pattern}")

print("\nDone.")
