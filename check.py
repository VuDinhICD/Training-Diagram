import google.generativeai as genai

# Dùng đúng key của bạn
genai.configure(api_key="")

print("Danh sách các model bạn có thể dùng:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"👉 {m.name}")