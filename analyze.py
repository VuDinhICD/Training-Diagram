
import os
import re
import subprocess
import ollama

FILES = [
    "/Users/dhv06/develop/datn/DATN/routes/web.php",
    "/Users/dhv06/develop/datn/DATN/app/Http/Controllers/UserController.php"
]

# ==============================
# READ FILE
# ==============================
def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def build_context():
    return "\n".join(read_file(p) for p in FILES)

# ==============================
# PROMPT
# ==============================
def build_prompt(ctx):
    return f"""
Generate ONE Mermaid flowchart for LOGIN + REGISTER.

RULES:
- First line: flowchart TD
- Use shapes:
  (["Start"]), (["End"])
  ["Process"]
  {{"Decision"}}
  [/Input/]

Flow:
Start → Login/Register → Validate → Success/Error → Home → End

ONLY business logic. No code.

Code:
{ctx}
"""

# ==============================
# CALL AI
# ==============================
def call_ai(prompt):
    res = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": "Only return Mermaid code"},
            {"role": "user", "content": prompt}
        ]
    )
    return res["message"]["content"]

# ==============================
# SANITIZE (FIX CHUẨN)
# ==============================
def sanitize(raw):
    lines = raw.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # ❌ bỏ dòng flowchart lặp
        if line.lower().startswith("flowchart"):
            continue

        # ❌ bỏ code
        if re.search(r'\b(if|else|function|return|class|public|private)\b', line):
            continue

        # ❌ bỏ ký tự nguy hiểm
        if ";" in line or "$" in line:
            continue

        # fix node rỗng
        line = re.sub(r'(\b\w+)\[\s*\]', r'\1["End"]', line)

        # fix arrow
        line = re.sub(r'-->\s*>', '-->', line)

        # normalize label
        line = re.sub(r'\[([^\"]+?)\]', r'["\1"]', line)
        line = re.sub(r'\{([^"]+?)\}', r'{"\1"}', line)

        # ❌ bỏ rác
        if any(x in line.lower() for x in ["exam", "sample", "question"]):
            continue

        # giữ cả node và edge
        if any(x in line for x in ['-->', '[', '{', '(']):
            cleaned.append(line)

    if len(cleaned) < 3:
        return None

    # ==============================
    # BUILD FINAL
    # ==============================
    final = ["flowchart TD"]

    # đảm bảo start
    final.append('Start(["Start"]) --> Choice{"Login or Register?"}')

    final.extend(cleaned)

    # đảm bảo end
    final.append('Home["Homepage"] --> End(["End"])')

    return "\n".join(final)

# ==============================
# EXPORT
# ==============================
def export(code, name):
    mmd = f"{name}.mmd"
    svg = f"{name}.svg"

    with open(mmd, "w", encoding="utf-8") as f:
        f.write(code)

    subprocess.run(["mmdc", "-i", mmd, "-o", svg], check=True)

    if not os.path.exists(svg) or os.path.getsize(svg) < 500:
        raise Exception("SVG lỗi")

# ==============================
# FALLBACK
# ==============================
def fallback():
    return """flowchart TD

Start(["Start"]) --> Choice{"Login or Register?"}

Choice -->|Login| LoginInput[/Enter email & password/]
Choice -->|Register| RegisterInput[/Enter info/]

LoginInput --> LoginCheck{"Valid?"}
LoginCheck -->|No| Error["Error"]
LoginCheck -->|Yes| Auth{"Correct?"}
Auth -->|No| Error
Auth -->|Yes| LoginSuccess["Login success"]

RegisterInput --> RegisterCheck{"Valid?"}
RegisterCheck -->|No| Error
RegisterCheck -->|Yes| Save["Create user"]
Save --> RegisterSuccess["Register success"]

LoginSuccess --> Home["Homepage"]
RegisterSuccess --> Home

Home --> End(["End"])
"""

# ==============================
# MAIN
# ==============================
def main():
    print("🚀 Generating...")

    ctx = build_context()

    for i in range(3):
        try:
            raw = call_ai(build_prompt(ctx))
            clean = sanitize(raw)

            if not clean:
                raise Exception("Sanitize fail")

            print(f"\n--- Attempt {i+1} ---")
            print(clean)

            export(clean, "auth_flow")
            print("✅ SUCCESS")
            return

        except Exception as e:
            print("❌ attempt failed:", e)

    print("⚠️ fallback")
    export(fallback(), "auth_flow")
    print("✅ fallback OK")

# ==============================
if __name__ == "__main__":
    main()