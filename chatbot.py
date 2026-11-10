"""Chatbot thường: gọi model MỘT lần, KHÔNG có tool. Dùng làm đối chứng với agent.

    python chatbot.py "Ngày mai ở Đà Nẵng nên mặc gì?"

Không có tool nên chatbot không biết hôm nay là ngày nào và không có dữ liệu thời tiết,
nó chỉ có thể đoán. So sánh với agent bằng: python compare.py
"""
from __future__ import annotations

import os
import sys
from types import SimpleNamespace

import openai
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# Cùng vai trò với agent, nhưng KHÔNG nhắc tới tool.
SYSTEM_PROMPT = "You are a Vietnamese travel assistant. Final answer: short, in Vietnamese."

_client: openai.OpenAI | None = None


def ask(question: str):
    """Trả về SimpleNamespace(text, usage). Đúng 1 lần gọi model, không tool, không vòng lặp."""
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY", "")
        if not key or key.endswith("..."):
            sys.exit("Chưa có OPENAI_API_KEY trong file .env.")
        _client = openai.OpenAI(api_key=key)
    resp = _client.chat.completions.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}],
    )
    usage = SimpleNamespace(input_tokens=resp.usage.prompt_tokens, output_tokens=resp.usage.completion_tokens)
    return SimpleNamespace(text=resp.choices[0].message.content or "", usage=usage)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Cách dùng: python chatbot.py "câu hỏi"')
    print("Chatbot:", ask(" ".join(sys.argv[1:])).text)
