# Multi-Agent Doc Analyzer

Hệ thống nhiều agent phân tích tài liệu `.txt` / `.md`, xây dựng bằng LangGraph và Gemini. Đưa vào một thư mục tài liệu, nhận lại một báo cáo Markdown tổng hợp.

## Cách hoạt động

```
                    ┌─ task t1: executor ⇄ reviewer ─┐
START → planner ────┼─ task t2: executor ⇄ reviewer ─┼──→ synthesize → END
                    └─ task t3: executor ⇄ reviewer ─┘
                          (chạy song song)
```

| Agent | Việc làm |
|---|---|
| **Planner** | Đọc các tài liệu (gọi tool `read_file`), chọn tài liệu cần phân tích và viết chỉ dẫn (`instruction`) cho từng tài liệu. Sau cùng, `synthesize` tổng hợp kết quả thành báo cáo. |
| **Executor** | Nhận một tài liệu cùng chỉ dẫn của planner, gọi các tool `read_file`, `summarize`, `extract_info`, `classify` để ra tóm tắt, thông tin trích xuất và nhóm phân loại. |
| **Reviewer** | Đối chiếu kết quả với tài liệu gốc, trả `ĐẠT` hoặc `KHÔNG ĐẠT` kèm nhận xét. Không đạt thì executor làm lại, tối đa `MAX_RETRIES` lần. |

Mỗi tài liệu chạy trong một nhánh riêng với state riêng, các nhánh chạy song song (tối đa `MAX_CONCURRENCY` nhánh cùng lúc). Các agent trao đổi qua danh sách `messages` dùng chung, mỗi mục có `sender`, `receiver` và `content`.

## Yêu cầu

- Python 3.11 trở lên và [uv](https://docs.astral.sh/uv/)
- Gemini API key
- Docker (tuỳ chọn, để chạy bằng container hoặc bật PostgreSQL)

## Cài đặt

```bash
uv sync
cp .env.example .env   # rồi điền GEMINI_API_KEY
```

Các biến cấu hình trong `.env`:

| Biến | Ý nghĩa | Mặc định |
|---|---|---|
| `GEMINI_API_KEY` | API key của Gemini | (bắt buộc) |
| `GEMINI_MODEL` | Model dùng cho mọi agent và tool | `gemini-2.5-flash` |
| `MAX_RETRIES` | Số lần executor được làm lại khi reviewer không đạt | `2` |
| `MAX_CONCURRENCY` | Số nhánh tài liệu chạy song song tối đa | `4` |
| `POSTGRES_*`, `DATABASE_URL` | Kết nối PostgreSQL (xem phần Docker) | xem `.env.example` |

## Chạy

```bash
uv run python -m doc_analyzer.main samples/
```

Tham số là thư mục hoặc danh sách file, mặc định là `samples/`. Báo cáo được in ra màn hình và lưu tại `runs/<run_id>/report.md`.

Chạy bằng Docker:

```bash
docker compose run --rm doc-analyzer            # phân tích samples/
docker compose run --rm doc-analyzer path/to/docs
docker compose up -d postgres                   # chỉ bật PostgreSQL
```

## Cấu trúc

```
src/doc_analyzer/
├── main.py        # CLI
├── config.py      # đọc .env, đối tượng settings
├── graph.py       # planner → các nhánh executor/reviewer → synthesize
├── state.py       # state của graph và của từng nhánh (kèm reducer gom kết quả)
├── messages.py    # TaskAssigned, TaskResult, ReviewFeedback
├── llm.py         # get_llm, load_prompt, invoke_with_tools
├── tools.py       # read_file, summarize, extract_info, classify
├── db.py          # kết nối PostgreSQL (SQLAlchemy)
├── agents/        # planner, executor, reviewer
└── prompts/       # prompt của từng agent (.md)
samples/           # tài liệu mẫu để chạy thử
runs/              # kết quả mỗi lần chạy (không đưa vào git)
```

## Lưu ý

- Gói Gemini miễn phí giới hạn rất thấp (ví dụ 5 request mỗi phút với `gemini-2.5-flash`), trong khi mỗi tài liệu cần nhiều lần gọi LLM. Gặp lỗi `429 RESOURCE_EXHAUSTED` thì đổi `GEMINI_MODEL`, giảm `MAX_CONCURRENCY` hoặc dùng key có bật billing.
- PostgreSQL đã được cấu hình sẵn (`db.py`, `docker-compose.yml`) nhưng pipeline hiện chưa ghi dữ liệu vào đó.
- Chưa ghi `trace.jsonl` cho mỗi lần chạy.
