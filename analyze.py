import os
import re
import sys
import subprocess
import ollama

# ==============================
# CONFIG
# ==============================
IGNORE_DIRS = {
    "node_modules",
    "vendor",
    ".git",
    "storage",
    "dist",
    "build",
    "__pycache__",
    ".next"
}

ALLOWED_EXTENSIONS = {
    ".php",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".py",
    ".java",
    ".cs",
    ".go",
    ".rb"
}

MAX_FILE_SIZE = 300000

# ==============================
# GET PROJECT PATH
# ==============================
if len(sys.argv) < 2:
    print("❌ Usage:")
    print("python3 diagram_ai_universal.py /path/to/project")
    sys.exit(1)

PROJECT_PATH = sys.argv[1]

if not os.path.exists(PROJECT_PATH):
    print("❌ Project path not found")
    sys.exit(1)

# ==============================
# FIND SOURCE FILES
# ==============================
def find_source_files(root):
    files = []

    for current_root, dirs, filenames in os.walk(root):

        # ignore folders
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in filenames:
            ext = os.path.splitext(file)[1]

            if ext.lower() not in ALLOWED_EXTENSIONS:
                continue

            path = os.path.join(current_root, file)

            try:
                if os.path.getsize(path) > MAX_FILE_SIZE:
                    continue
            except:
                continue

            files.append(path)

    return files

# ==============================
# READ FILES
# ==============================
def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# ==============================
# BUILD CONTEXT
# ==============================
def build_context(files):
    context = ""

    for path in files:
        try:
            rel = os.path.relpath(path, PROJECT_PATH)

            content = read_file(path)

            if not content.strip():
                continue

            context += f"""
========================
FILE: {rel}
========================
{content}

"""

        except:
            pass

    return context[:120000]

# ==============================
# PROMPT
# ==============================
def build_prompt(context):
    return f"""
Analyze this project source code.

Generate ONE Mermaid flowchart describing:
- authentication flow
- login
- register
- logout
- session
- middleware
- redirect

STRICT:
- first line: flowchart TD

USE SHAPES:
(["Start"])
(["End"])
["Process"]
{{"Decision"}}
[/Input/]

DO NOT:
- generate code
- explain
- use markdown
- use subgraph

ONLY Mermaid flowchart.

Project source:
{context}
"""

# ==============================
# AI
# ==============================
def call_ai(prompt):
    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "system",
                "content": "You are a Mermaid diagram generator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

# ==============================
# SANITIZE
# ==============================
def sanitize(raw):
    lines = raw.split("\n")

    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # remove markdown
        if "```" in line:
            continue

        # remove duplicate flowchart
        if line.lower().startswith("flowchart"):
            continue

        # remove php/js code
        if re.search(r'\b(function|class|public|private|return|if|else)\b', line):
            continue

        # remove dangerous chars
        line = line.replace(";", "")
        line = line.replace("$", "")

        # fix empty node
        line = re.sub(r'(\b\w+)\[\s*\]', r'\1["End"]', line)

        # fix broken arrow
        line = re.sub(r'-->\s*>', '-->', line)

        # normalize labels
        line = re.sub(r'\[([^\"]+?)\]', r'["\1"]', line)
        line = re.sub(r'\{([^"]+?)\}', r'{"\1"}', line)

        # keep only mermaid-like
        if any(x in line for x in ['-->', '[', '{', '(']):
            cleaned.append(line)

    if len(cleaned) < 3:
        return None

    final = ["flowchart TD"]

    final.extend(cleaned)

    return "\n".join(final)

# ==============================
# FALLBACK
# ==============================
def fallback():
    return """flowchart TD

Start(["Start"]) --> Choice{"Login or Register?"}

Choice -->|Login| LoginInput[/Enter credentials/]
Choice -->|Register| RegisterInput[/Enter information/]

LoginInput --> LoginCheck{"Valid?"}
LoginCheck -->|No| Error["Show error"]
LoginCheck -->|Yes| Auth{"Correct?"}

Auth -->|No| Error
Auth -->|Yes| Session["Create session"]

RegisterInput --> RegisterCheck{"Valid?"}
RegisterCheck -->|No| Error
RegisterCheck -->|Yes| Save["Create user"]

Save --> Login["Redirect to login"]

Session --> Home["Homepage"]
Login --> Home

Home --> Logout{"Logout?"}
Logout -->|Yes| End(["End"])
Logout -->|No| Home
"""

# ==============================
# EXPORT
# ==============================
def export(code):
    mmd_file = "project_flow.mmd"
    svg_file = "project_flow.svg"
    png_file = "project_flow.png"

    with open(mmd_file, "w", encoding="utf-8") as f:
        f.write(code)

    subprocess.run(
        ["mmdc", "-i", mmd_file, "-o", svg_file],
        check=True
    )

    subprocess.run(
        ["mmdc", "-i", mmd_file, "-o", png_file],
        check=True
    )

# ==============================
# MAIN
# ==============================
def main():
    print("🔍 Scanning project...")

    files = find_source_files(PROJECT_PATH)

    print(f"📄 Found {len(files)} source files")

    context = build_context(files)

    print("🤖 Asking AI...")

    for i in range(3):
        try:
            raw = call_ai(build_prompt(context))

            clean = sanitize(raw)

            if not clean:
                raise Exception("Sanitize fail")

            print(f"\n--- Attempt {i+1} ---")
            print(clean)

            export(clean)

            print("\n✅ SUCCESS")
            print("🎉 Generated:")
            print("project_flow.svg")
            print("project_flow.png")

            return

        except Exception as e:
            print(f"❌ Attempt {i+1} failed:", e)

    print("⚠️ Using fallback")

    export(fallback())

    print("✅ fallback OK")

# ==============================
if __name__ == "__main__":
    main()