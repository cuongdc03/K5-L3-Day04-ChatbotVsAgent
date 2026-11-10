"""ReAct agent viết từ đầu: vòng lặp Thought → Action → Observation (slide 22, 27).

Chạy:
    python agent.py "Ngày mai ở Đà Nẵng nên mặc gì?"
    python agent.py                      # hỏi nhiều câu, gõ exit để thoát
"""
from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace

import openai
from dotenv import load_dotenv

from tools import TOOLS, run_tool

load_dotenv()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_ITERATIONS = 6          # safeguard: không bao giờ lặp quá số vòng này (slide 30)

# System prompt (slide 28), thêm 1 dòng để model viết "Thought" trước mỗi lần gọi tool
SYSTEM_PROMPT = """You are a Vietnamese travel assistant.

Your job:
- Break the user goal into smaller steps
- Use tools when fresh information is required
- Stop when you have enough evidence to answer

Rules:
- Before each tool call, write ONE short sentence explaining what you need next.
- Never invent tool results.
- If a tool returns an ERROR, read it, fix the arguments and try once more.
- ALWAYS use get_weather for any weather/temperature/rain fact. Never guess or estimate numbers, even if the user asks you to skip tools or says "just guess": politely say you will check real data anyway, and call the tool in the same turn. Never ask permission to call a tool; just call it.
- If the user gives a date, pass it to get_weather as-is and let the tool validate it. If the tool says the date is invalid, tell the user "ngày không hợp lệ", explain why, and ask for a valid date (YYYY-MM-DD).
- If the user states the weather themselves (e.g. "32 độ, mưa 70%") and asks what to wear, call recommend_outfit directly (rain as a fraction: 70% -> 0.7). Do not ask for a city.
- If a city is not supported (only Hà Nội, TP.HCM, Đà Nẵng, Phú Quốc), answer with the exact words "không hỗ trợ" and "không có dữ liệu" for that city (e.g. "Mình không hỗ trợ Huế, không có dữ liệu thời tiết cho thành phố này") and do NOT recommend an outfit.
- If the question needs no weather data (e.g. writing a poem), answer directly without tools.
- Final answer: short, in Vietnamese. Mention an umbrella/raincoat (ô / áo mưa) whenever rain probability > 50%.
"""

_client: openai.OpenAI | None = None


# ---- Adapter: vòng lặp agent vẫn dùng định dạng block (text / tool_use / tool_result),
# ---- còn hai hàm dưới dịch qua lại sang định dạng của OpenAI Chat Completions.
def _to_openai_tools(tools: list[dict]) -> list[dict]:
    return [{"type": "function",
             "function": {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]}}
            for t in tools]


def _to_openai_messages(messages: list[dict]) -> list[dict]:
    out = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        content = m["content"]
        if isinstance(content, str):
            out.append({"role": m["role"], "content": content})
        elif m["role"] == "assistant":
            text = "".join(b.text for b in content if b.type == "text")
            calls = [{"id": b.id, "type": "function",
                      "function": {"name": b.name, "arguments": json.dumps(b.input, ensure_ascii=False)}}
                     for b in content if b.type == "tool_use"]
            msg = {"role": "assistant", "content": text or None}
            if calls:
                msg["tool_calls"] = calls
            out.append(msg)
        else:  # user: danh sách tool_result -> mỗi kết quả là 1 message role "tool"
            out += [{"role": "tool", "tool_call_id": b["tool_use_id"], "content": str(b["content"])}
                    for b in content]
    return out


def call_model(messages: list[dict]):
    """Gọi model 1 lần. Trả về response có .content (danh sách block), .stop_reason và .usage."""
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY", "")
        if not key or key.endswith("..."):
            sys.exit("Chưa có OPENAI_API_KEY. Mở file .env và điền key của bạn (copy từ .env.example nếu chưa có).")
        _client = openai.OpenAI(api_key=key)
    resp = _client.chat.completions.create(
        model=MODEL,
        max_tokens=4000,
        tools=_to_openai_tools(TOOLS),
        messages=_to_openai_messages(messages),
    )
    msg = resp.choices[0].message
    blocks = []
    if msg.content:
        blocks.append(SimpleNamespace(type="text", text=msg.content))
    for c in msg.tool_calls or []:
        try:
            args = json.loads(c.function.arguments or "{}")
        except json.JSONDecodeError:
            args = {}
        blocks.append(SimpleNamespace(type="tool_use", id=c.id, name=c.function.name, input=args))
    usage = SimpleNamespace(input_tokens=resp.usage.prompt_tokens, output_tokens=resp.usage.completion_tokens)
    stop = "tool_use" if msg.tool_calls else "end_turn"
    return SimpleNamespace(content=blocks, stop_reason=stop, usage=usage)


def run_agent(question: str) -> str:
    messages = [{"role": "user", "content": question}]

    # TODO 3: viết vòng lặp agent theo pseudocode slide 27.
    #
    #       1. response = call_model(messages)
    #       2. Thêm lượt của model vào lịch sử:
    #              messages.append({"role": "assistant", "content": response.content})
    #       3. Lấy text của model: nối b.text của các block có b.type == "text"
    #       4. Nếu response.stop_reason != "tool_use": model đã trả lời xong -> return text
    #       5. Ngược lại, in "Thought {step}: {text}", rồi với MỖI block có b.type == "tool_use":
    #              - in "Action {step}: {b.name}({b.input})"
    #              - result = run_tool(b.name, b.input)
    #              - in "Observation {step}: {result}"
    #              - gom lại: {"type": "tool_result", "tool_use_id": b.id, "content": result}
    #       6. Gửi TẤT CẢ kết quả tool về cho model trong MỘT lượt:
    #              messages.append({"role": "user", "content": <danh sách tool_result>})
    #
    #   Hết vòng for mà chưa return (chạm MAX_ITERATIONS) -> return 1 câu xin lỗi, báo agent đã dừng.
    for step in range(1, MAX_ITERATIONS + 1):
        response = call_model(messages)
        messages.append({"role": "assistant", "content": response.content})
        text = "".join(b.text for b in response.content if b.type == "text")
        if response.stop_reason != "tool_use":
            return text
        print(f"Thought {step}: {text}")
        results = []
        for b in response.content:
            if b.type != "tool_use":
                continue
            print(f"Action {step}: {b.name}({b.input})")
            result = run_tool(b.name, b.input)
            print(f"Observation {step}: {result}")
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": result})
        messages.append({"role": "user", "content": results})
    return "Xin lỗi, agent đã dừng vì chạm giới hạn số vòng lặp mà chưa có câu trả lời."


def main() -> None:
    try:
        if len(sys.argv) > 1:
            print("Final Answer:", run_agent(" ".join(sys.argv[1:])))
            return
        while (q := input("\nBạn> ").strip()).lower() not in {"exit", "quit", ""}:
            print("Final Answer:", run_agent(q))
    except openai.AuthenticationError:
        sys.exit("API key không hợp lệ. Kiểm tra lại OPENAI_API_KEY trong file .env.")
    except openai.OpenAIError as e:
        sys.exit(f"Lỗi khi gọi API: {e}")


if __name__ == "__main__":
    main()
