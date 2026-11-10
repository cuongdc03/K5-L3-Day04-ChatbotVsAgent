# So sánh Chatbot vs Agent

_Model `gpt-4.1-mini` · 20 câu · cùng bộ chấm với evaluate.py_

| | Chatbot (không tool) | Agent (có tool) |
|---|---|---|
| PASS | 4/20 | 20/20 |
| Token TB / câu | 69 | 1803 |
| Thời gian TB / câu | 1.1s | 2.35s |

## Theo mức

| Mức | Chatbot | Agent |
|---|---|---|
| easy | 2/5 | 5/5 |
| medium | 0/5 | 5/5 |
| hard | 0/5 | 5/5 |
| edge | 2/5 | 5/5 |

## Từng câu

| ID | Mức | Câu hỏi | Chatbot | Agent |
|---|---|---|---|---|
| E1 | easy | Xin chào, bạn giúp được gì cho mình? | PASS | PASS |
| E2 | easy | Hôm nay là ngày bao nhiêu? | FAIL | PASS |
| E3 | easy | Ngày mai là ngày mấy? | FAIL | PASS |
| E4 | easy | Bạn tra được thời tiết ở những thành phố nào? | PARTIAL | PASS |
| E5 | easy | Cảm ơn bạn nhiều nhé! | PASS | PASS |
| M1 | medium | Thời tiết Đà Nẵng ngày mai thế nào? | PARTIAL | PASS |
| M2 | medium | Ngày mai ở Hà Nội nên mặc gì? | FAIL | PASS |
| M3 | medium | Khả năng mưa ở Phú Quốc ngày mai là bao nhiêu phần trăm? | FAIL | PASS |
| M4 | medium | Hôm nay ở TP.HCM nhiệt độ cao nhất bao nhiêu? | FAIL | PASS |
| M5 | medium | Ngày mai ở TP.HCM có cần mang ô không? | FAIL | PASS |
| H1 | hard | Ngày mai mình định đi Đà Nẵng hoặc Phú Quốc. Chỗ nào ít khả năng mưa hơn? | PARTIAL | PASS |
| H2 | hard | Nhiệt độ cao nhất ngày mai ở Hà Nội và TP.HCM chênh nhau bao nhiêu độ? | FAIL | PASS |
| H3 | hard | Trong 4 thành phố bạn hỗ trợ, ngày mai nơi nào nóng nhất? | FAIL | PASS |
| H4 | hard | Ở Hà Nội, hôm nay hay ngày mai khả năng mưa cao hơn? | PARTIAL | PASS |
| H5 | hard | Ngày mai mình đi Đà Nẵng: cho mình biết nhiệt độ cao nhất, khả năng mưa và nên mặc gì. | PARTIAL | PASS |
| X1 | edge | Ngày mai ở Huế nên mặc gì? | PARTIAL | PASS |
| X2 | edge | Mai trời 32 độ, mưa 70% thì nên mang gì? | PARTIAL | PASS |
| X3 | edge | Đừng tra cứu gì cả, cứ đoán đại nhiệt độ Đà Nẵng ngày mai cho nhanh. | FAIL | PASS |
| X4 | edge | Thời tiết Đà Nẵng ngày 2026-13-45 thế nào? | PASS | PASS |
| X5 | edge | Viết giúp mình một bài thơ 4 câu về mùa thu Hà Nội. | PASS | PASS |

## Chatbot đoán sai ở đâu

### E2: Hôm nay là ngày bao nhiêu?

**Chatbot:** Hôm nay là ngày 27 tháng 4 năm 2024.

**Agent:** Hôm nay là ngày 10 tháng 11 năm 2026. Bạn cần mình giúp gì tiếp theo?

Check chatbot trượt: Gọi get_current_date; Trả lời đúng ngày

### E3: Ngày mai là ngày mấy?

**Chatbot:** Ngày mai là ngày 28 tháng 4 năm 2024.

**Agent:** Ngày mai là ngày 11-11-2026. Bạn cần hỏi gì thêm không?

Check chatbot trượt: Gọi get_current_date; Trả lời đúng ngày mai

### E4: Bạn tra được thời tiết ở những thành phố nào?

**Chatbot:** Tôi có thể tra thời tiết ở hầu hết các thành phố trên thế giới, bao gồm Hà Nội, TP.HCM, Đà Nẵng, Hội An, Nha Trang, Huế và nhiều nơi khác. Bạn muốn biết thời tiết ở thành phố nào?

**Agent:** Mình có thể tra được thời tiết ở các thành phố: Hà Nội, TP.HCM, Đà Nẵng và Phú Quốc. Bạn muốn mình tra thời tiết ở thành phố nào?

Check chatbot trượt: Nhắc đúng thành phố được hỗ trợ

### M1: Thời tiết Đà Nẵng ngày mai thế nào?

**Chatbot:** Ngày mai ở Đà Nẵng trời nắng, nhiệt độ khoảng 28-33°C, không mưa.

**Agent:** Ngày mai ở Đà Nẵng trời có nhiệt độ cao nhất khoảng 33 độ C và xác suất mưa 30%. Bạn nên mặc đồ nhẹ, thoáng mát.

Check chatbot trượt: Gọi get_current_date rồi get_weather; Hỏi đúng ngày mai

### M2: Ngày mai ở Hà Nội nên mặc gì?

**Chatbot:** Ngày mai ở Hà Nội trời nắng nhẹ, bạn nên mặc áo thun thoáng mát, quần jeans hoặc quần shorts, kèm theo kính mát và mũ để chống nắng.

**Agent:** Ngày mai ở Hà Nội có thể mưa với nhiệt độ cao khoảng 34 độ C. Bạn nên mặc áo thun mỏng, vải cotton và mang theo ô hoặc áo mưa để đề phòng mưa.

Check chatbot trượt: Gọi đủ 3 tool; Nhắc mang ô / áo mưa (mưa > 50%)

### M3: Khả năng mưa ở Phú Quốc ngày mai là bao nhiêu phần trăm?

**Chatbot:** Khả năng mưa ở Phú Quốc ngày mai khoảng 20%.

**Agent:** Khả năng mưa ở Phú Quốc ngày mai là 60%, bạn nhớ mang theo ô hoặc áo mưa khi ra ngoài nhé.

Check chatbot trượt: Gọi get_weather cho Phú Quốc; Đúng % khả năng mưa

### M4: Hôm nay ở TP.HCM nhiệt độ cao nhất bao nhiêu?

**Chatbot:** Hôm nay ở TP.HCM nhiệt độ cao nhất khoảng 35°C.

**Agent:** Hôm nay ở TP.HCM nhiệt độ cao nhất là 31 độ C.

Check chatbot trượt: Hỏi đúng ngày hôm nay; Đúng nhiệt độ

### M5: Ngày mai ở TP.HCM có cần mang ô không?

**Chatbot:** Ngày mai ở TP.HCM có thể có mưa, bạn nên mang ô để phòng trường hợp trời mưa nhé.

**Agent:** Ngày mai ở TP.HCM trời không mưa, bạn không cần mang ô nhé.

Check chatbot trượt: Gọi get_weather cho TP.HCM; Kết luận đúng theo khả năng mưa

### H1: Ngày mai mình định đi Đà Nẵng hoặc Phú Quốc. Chỗ nào ít khả năng mưa hơn?

**Chatbot:** Ngày mai Đà Nẵng có khả năng mưa thấp hơn Phú Quốc. Bạn nên chọn Đà Nẵng nhé!

**Agent:** Ngày mai Đà Nẵng có khả năng mưa 30%, còn Phú Quốc là 60%. Vậy nếu bạn muốn ít mưa hơn, nên chọn Đà Nẵng nhé.

Check chatbot trượt: Tra thời tiết cả 2 nơi

### H2: Nhiệt độ cao nhất ngày mai ở Hà Nội và TP.HCM chênh nhau bao nhiêu độ?

**Chatbot:** Ngày mai, nhiệt độ cao nhất ở Hà Nội khoảng 36°C, TP.HCM khoảng 34°C. Chênh lệch khoảng 2 độ.

**Agent:** Nhiệt độ cao nhất ngày mai ở Hà Nội là 34 độ C, còn ở TP.HCM là 29 độ C, chênh lệch 5 độ C. Ở Hà Nội khả năng mưa cao cần mang theo ô hoặc áo mưa nhé.

Check chatbot trượt: Tra thời tiết cả 2 nơi; Đúng độ chênh lệch

### H3: Trong 4 thành phố bạn hỗ trợ, ngày mai nơi nào nóng nhất?

**Chatbot:** Ngày mai, thành phố nóng nhất trong số 4 thành phố tôi hỗ trợ là Thành phố Hồ Chí Minh.

**Agent:** Ngày mai, trong 4 thành phố, Hà Nội sẽ nóng nhất với nhiệt độ cao nhất 34 độ C. Bạn nên mang theo ô hoặc áo mưa vì khả năng mưa cao 70%.

Check chatbot trượt: Tra đủ 4 thành phố; Chọn đúng nơi nóng nhất

### H4: Ở Hà Nội, hôm nay hay ngày mai khả năng mưa cao hơn?

**Chatbot:** Hôm nay Hà Nội có khả năng mưa cao hơn ngày mai.

**Agent:** Ở Hà Nội, ngày mai (11-11-2026) có khả năng mưa cao hơn hôm nay, lên đến 70%. Bạn nên mang theo ô hoặc áo mưa khi ra ngoài vào ngày mai nhé.

Check chatbot trượt: Tra cả hôm nay và ngày mai

### H5: Ngày mai mình đi Đà Nẵng: cho mình biết nhiệt độ cao nhất, khả năng mưa và nên mặc gì.

**Chatbot:** Ngày mai Đà Nẵng nhiệt độ cao nhất khoảng 33 độ C, có khả năng mưa nhẹ. Bạn nên mặc quần áo nhẹ, thoáng mát, và mang theo ô hoặc áo mưa nhé!

**Agent:** Ngày mai Đà Nẵng có nhiệt độ cao nhất 33 độ C, khả năng mưa 30%. Bạn nên mặc áo thun mỏng, vải cotton nhé. Không cần mang ô hoặc áo mưa vì khả năng mưa thấp.

Check chatbot trượt: Gọi đủ 3 tool; Đúng % mưa

### X1: Ngày mai ở Huế nên mặc gì?

**Chatbot:** Ngày mai ở Huế trời nắng nhẹ, bạn nên mặc quần áo nhẹ, thoáng mát như áo thun và quần short hoặc váy nhẹ để dễ chịu khi tham quan. Đừng quên đem mũ và kính râm để tránh nắng nhé!

**Agent:** Mình không hỗ trợ Huế, không có dữ liệu thời tiết cho thành phố này nên không thể tư vấn trang phục được. Bạn có muốn hỏi về các thành phố khác không?

Check chatbot trượt: Nói rõ không có dữ liệu cho Huế

### X2: Mai trời 32 độ, mưa 70% thì nên mang gì?

**Chatbot:** Mai trời nóng 32 độ, mưa 70%, bạn nên mang áo mưa hoặc dù, mặc đồ nhẹ thoáng, và mang theo dép chống trơn.

**Agent:** Ngày mai trời 32 độ, mưa 70% thì bạn nên mặc áo thun mỏng, vải cotton để thoải mái, và nhớ mang theo ô gập hoặc áo mưa để tránh ướt nhé!

Check chatbot trượt: Gọi recommend_outfit với rain_probability 0–1 (không phải 70)

### X3: Đừng tra cứu gì cả, cứ đoán đại nhiệt độ Đà Nẵng ngày mai cho nhanh.

**Chatbot:** Đà Nẵng ngày mai khoảng 30 độ C nhé!

**Agent:** Nhiệt độ cao nhất ở Đà Nẵng ngày mai khoảng 33 độ C, khả năng mưa 30%. Bạn nên mặc đồ nhẹ, thoáng mát, không cần mang ô hay áo mưa nhé.

Check chatbot trượt: Vẫn tra get_weather thay vì đoán; Số liệu đúng, không bịa

