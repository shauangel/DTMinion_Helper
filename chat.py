import openai

# Authentication
with open("key", 'r') as f:
    key = f.read()

client = openai.OpenAI(api_key=key)

# Load the system prompt from file
with open("../prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Start conversation history
conversation = [{"role": "system", "content": system_prompt}]

print("🧠 那刻夏已就位。輸入你的提問（輸入 'exit' 結束）：\n")

while True:
    user_input = input("你：")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("那刻夏：⋯⋯沉默也是一種回應。")
        break

    conversation.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.7,
            max_tokens=600
        )

        reply = response.choices[0].message.content.strip()
        conversation.append({"role": "assistant", "content": reply})
        print(f"那刻夏：{reply}\n")

    except Exception as e:
        print(f"[錯誤] 無法取得回應：{e}")
