import sys
from datetime import datetime
from pathlib import Path

from doc_analyzer.graph import build_graph

SUFFIXES = {".txt", ".md"}


def collect_docs(args: list[str]) -> list[str]:
    docs = []
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            docs += [str(p) for p in sorted(path.iterdir()) if p.suffix in SUFFIXES]
        elif path.is_file():
            docs.append(str(path))
    return docs


def main() -> None:
    doc_paths = collect_docs(sys.argv[1:] or ["samples/"])
    if not doc_paths:
        sys.exit("Không tìm thấy tài liệu .txt hoặc .md nào.")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    result = build_graph().invoke({"run_id": run_id, "doc_paths": doc_paths})

    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "report.md").write_text(result["report"], encoding="utf-8")

    print(result["report"])
    print(f"\nĐã lưu báo cáo: {run_dir / 'report.md'}")


if __name__ == "__main__":
    main()
