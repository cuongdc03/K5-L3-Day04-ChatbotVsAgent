"""Tools: "tay chân" của agent (slide 29, 34).

Mỗi tool gồm 2 phần:
  1. Hàm Python làm việc thật.
  2. Schema (name, description, input_schema) để model biết KHI NÀO gọi và gọi với tham số gì.
     Model không đọc code của bạn. Nó chỉ đọc schema.

File này có sẵn 2 tool mẫu (get_current_date, get_weather). Bạn viết tool thứ 3: recommend_outfit.
"""
from __future__ import annotations

import json
import re
from datetime import date as Date, timedelta

CITIES = {"Hà Nội": 0, "TP.HCM": 1, "Đà Nẵng": 2, "Phú Quốc": 3}


# ---------------------------------------------------------------- tool mẫu 1
def get_current_date() -> dict:
    today = Date.today()
    return {"today": today.isoformat(), "tomorrow": (today + timedelta(days=1)).isoformat()}


# ---------------------------------------------------------------- date parsing
def parse_date(value: str) -> Date:
    """Parse 'YYYY-MM-DD' và báo lỗi cụ thể (luôn chứa 'không hợp lệ') để agent biết sửa gì."""
    m = re.fullmatch(r"\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*", str(value))
    if not m:
        raise ValueError(f"Ngày '{value}' không hợp lệ: sai định dạng, cần YYYY-MM-DD (vd. 2026-06-02).")
    y, mo, d = map(int, m.groups())
    if not 1 <= mo <= 12:
        raise ValueError(f"Ngày '{value}' không hợp lệ: không có tháng {mo} (tháng phải từ 1 đến 12).")
    try:
        return Date(y, mo, d)
    except ValueError:
        raise ValueError(f"Ngày '{value}' không hợp lệ: tháng {mo} năm {y} không có ngày {d}.")


# ---------------------------------------------------------------- tool mẫu 2
def get_weather(city: str, date: str) -> dict:
    if city not in CITIES:
        raise ValueError(f"Không hỗ trợ thành phố '{city}'. Chỉ có: {', '.join(CITIES)}.")
    d = parse_date(date)
    # Dữ liệu giả lập: cùng thành phố + cùng ngày luôn ra cùng kết quả
    seed = d.toordinal() * 7 + CITIES[city] * 13
    return {
        "city": city,
        "date": d.isoformat(),
        "temp_high_c": 26 + seed % 9,             # 26..34
        "rain_probability": (seed % 10) / 10,     # 0.0..0.9
    }


# ---------------------------------------------------------------- tool 3
def recommend_outfit(temp_high_c: float, rain_probability: float) -> dict:
    # TODO 1: viết tool gợi ý trang phục (slide 34). Luật:
    #   - rain_probability không nằm trong [0, 1] -> raise ValueError với lời nhắn hướng dẫn sửa
    #     (vd. "rain_probability phải từ 0 đến 1, nhận 70. 70% thì truyền 0.7.")
    #     run_tool() sẽ đổi lỗi này thành "ERROR: ..." để agent đọc và tự gọi lại cho đúng.
    #   - temp_high_c > 30         -> gợi ý "áo thun mỏng, vải cotton"
    #     ngược lại                -> gợi ý "trang phục thoải mái, mang áo khoác nhẹ"
    #   - rain_probability > 0.5   -> thêm "ô gập hoặc áo mưa"
    #   - Trả về dict: {"items": [ ...các gợi ý... ]}
    if not 0 <= rain_probability <= 1:
        raise ValueError(
            f"rain_probability phải từ 0 đến 1, nhận {rain_probability:g}. "
            f"Nếu là phần trăm thì chia cho 100 (vd. 70% thì truyền 0.7)."
        )
    items = ["áo thun mỏng, vải cotton"] if temp_high_c > 30 else ["trang phục thoải mái, mang áo khoác nhẹ"]
    if rain_probability > 0.5:
        items.append("ô gập hoặc áo mưa")
    return {"items": items}


# ---------------------------------------------------------------- schema
TOOLS = [
    {
        "name": "get_current_date",
        "description": "Get today's and tomorrow's date (YYYY-MM-DD). Call this first whenever the user "
                       "says 'hôm nay' or 'ngày mai', because you do not know today's date.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_weather",
        "description": "Get the weather forecast for ONE city on ONE date. "
                       "Supported cities: Hà Nội, TP.HCM, Đà Nẵng, Phú Quốc. "
                       "Returns JSON: city, date, temp_high_c (°C), rain_probability (0.0-1.0).",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "One of: Hà Nội, TP.HCM, Đà Nẵng, Phú Quốc."},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format."},
            },
            "required": ["city", "date"],
        },
    },
    # TODO 2: khai báo schema cho recommend_outfit, cùng dạng với get_weather ở trên.
    #   - "name": "recommend_outfit"
    #   - "description": tool làm gì, KHI NÀO gọi (sau get_weather), trả về gì
    #   - "input_schema": 2 tham số temp_high_c và rain_probability, đều là "number",
    #     mỗi tham số có description ghi rõ đơn vị (°C; 0.0-1.0, KHÔNG phải %), và có "required".
    # Thiếu schema này thì model không biết tool tồn tại, dù hàm đã viết xong.
    {
        "name": "recommend_outfit",
        "description": "Recommend what to wear. Call this AFTER get_weather, using its values. "
                       "Returns JSON: {\"items\": [list of clothing suggestions]}.",
        "input_schema": {
            "type": "object",
            "properties": {
                "temp_high_c": {"type": "number", "description": "Daily high temperature in °C (e.g. 32)."},
                "rain_probability": {"type": "number",
                                     "description": "Chance of rain as a fraction from 0.0 to 1.0, NOT a percent (70% = 0.7)."},
            },
            "required": ["temp_high_c", "rain_probability"],
        },
    },
]

FUNCTIONS = {
    "get_current_date": get_current_date,
    "get_weather": get_weather,
    "recommend_outfit": recommend_outfit,
}


def run_tool(name: str, args: dict) -> str:
    """Chạy 1 tool, luôn trả về chuỗi. Lỗi cũng trả về chuỗi "ERROR: ..." để model đọc và tự sửa."""
    if name not in FUNCTIONS:
        return f"ERROR: tool '{name}' không tồn tại."
    try:
        return json.dumps(FUNCTIONS[name](**args), ensure_ascii=False)
    except Exception as e:  # noqa: BLE001
        return f"ERROR: {e}"
