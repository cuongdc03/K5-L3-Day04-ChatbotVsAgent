"""So sánh Chatbot (không tool) với Agent (có tool) trên cùng bộ câu hỏi, cùng bộ chấm.

    python compare.py                  # cả 20 câu
    python compare.py --level hard     # 1 mức: easy | medium | hard | edge
    python compare.py --ids E1,M2      # vài câu

Xuất compare.md. Chatbot không gọi tool nên mọi check "calls" đều trượt, và các số liệu
thời tiết nó nói ra là đoán, không khớp dữ liệu thật.
"""
from __future__ import annotations

import argparse
import sys
import time

import chatbot
import evaluate
from dataset import build_cases


def run_chatbot_case(case: dict) -> dict:
    t0 = time.perf_counter()
    try:
        r = chatbot.ask(case["question"])
        answer, error, usage = r.text, "", r.usage
    except Exception as e:  # noqa: BLE001
        answer, error, usage = "", f"{type(e).__name__}: {e}", None
    results = [(d, evaluate.check(k, v, answer, [])) for d, k, v in case["checks"]]
    passed = sum(ok for _, ok in results)
    verdict = "PASS" if passed == len(results) and not error else ("PARTIAL" if passed and not error else "FAIL")
    tokens = (usage.input_tokens + usage.output_tokens) if usage else 0
    return {"id": case["id"], "level": case["level"], "question": case["question"], "verdict": verdict,
            "answer": answer, "error": error, "tokens": tokens, "latency_s": round(time.perf_counter() - t0, 2),
            "failed": [d for d, ok in results if not ok]}


def main() -> None:
    ap = argparse.ArgumentParser(description="So sánh chatbot và agent")
    ap.add_argument("--level", choices=evaluate.LEVELS)
    ap.add_argument("--ids", default="")
    args = ap.parse_args()
    ids = {i.strip().upper() for i in args.ids.split(",") if i.strip()}
    cases = [c for c in build_cases() if (not args.level or c["level"] == args.level) and (not ids or c["id"] in ids)]
    if not cases:
        sys.exit("Không có câu hỏi nào khớp bộ lọc.")

    rows = []
    print(f"{'ID':<3} {'Mức':<6} {'Chatbot':<8} {'Agent':<8} Câu hỏi")
    for c in cases:
        cb = run_chatbot_case(c)
        ag = evaluate.run_case(c)
        if ag["error"].startswith(("AuthenticationError", "SystemExit")) or cb["error"].startswith("AuthenticationError"):
            sys.exit("\nKhông gọi được model: kiểm tra OPENAI_API_KEY trong .env.")
        print(f"{c['id']:<3} {c['level']:<6} {cb['verdict']:<8} {ag['verdict']:<8} {c['question'][:55]}")
        rows.append((c, cb, ag))

    n = len(rows)
    cb_pass = sum(cb["verdict"] == "PASS" for _, cb, _ in rows)
    ag_pass = sum(ag["verdict"] == "PASS" for _, _, ag in rows)
    cb_tok = sum(cb["tokens"] for _, cb, _ in rows) // n
    ag_tok = sum(ag["input_tokens"] + ag["output_tokens"] for _, _, ag in rows) // n
    cb_lat = round(sum(cb["latency_s"] for _, cb, _ in rows) / n, 2)
    ag_lat = round(sum(ag["latency_s"] for _, _, ag in rows) / n, 2)
    print(f"\nChatbot {cb_pass}/{n} PASS · Agent {ag_pass}/{n} PASS")

    L = ["# So sánh Chatbot vs Agent", "",
         f"_Model `{chatbot.MODEL}` · {n} câu · cùng bộ chấm với evaluate.py_", "",
         "| | Chatbot (không tool) | Agent (có tool) |", "|---|---|---|",
         f"| PASS | {cb_pass}/{n} | {ag_pass}/{n} |",
         f"| Token TB / câu | {cb_tok} | {ag_tok} |",
         f"| Thời gian TB / câu | {cb_lat}s | {ag_lat}s |", "",
         "## Theo mức", "", "| Mức | Chatbot | Agent |", "|---|---|---|"]
    for lv in evaluate.LEVELS:
        sub = [(cb, ag) for c, cb, ag in rows if c["level"] == lv]
        if sub:
            L.append(f"| {lv} | {sum(cb['verdict'] == 'PASS' for cb, _ in sub)}/{len(sub)} "
                     f"| {sum(ag['verdict'] == 'PASS' for _, ag in sub)}/{len(sub)} |")
    L += ["", "## Từng câu", "", "| ID | Mức | Câu hỏi | Chatbot | Agent |", "|---|---|---|---|---|"]
    for c, cb, ag in rows:
        L.append(f"| {c['id']} | {c['level']} | {c['question']} | {cb['verdict']} | {ag['verdict']} |")
    L += ["", "## Chatbot đoán sai ở đâu", ""]
    shown = 0
    for c, cb, ag in rows:
        if cb["verdict"] != "PASS" and ag["verdict"] == "PASS":
            L += [f"### {c['id']}: {c['question']}", "",
                  "**Chatbot:** " + (cb["answer"] or "(trống)").replace("\n", " "), "",
                  "**Agent:** " + (ag["answer"] or "(trống)").replace("\n", " "), "",
                  "Check chatbot trượt: " + "; ".join(cb["failed"]), ""]
            shown += 1
    if not shown:
        L.append("(Không có câu nào chatbot trượt mà agent đạt.)")
    with open("compare.md", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("Chi tiết: compare.md")


if __name__ == "__main__":
    main()
