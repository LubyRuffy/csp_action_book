from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "BOOK.md"
ORDER = (
    ["00.md"]
    + [f"{number:02d}.md" for number in range(1, 27)]
    + [
        "Epilogue.md",
        "Appendix-A.md",
        "Appendix-B.md",
        "Appendix-C.md",
        "Appendix-D.md",
        "Appendix-E.md",
    ]
)


def normalize_for_bundle(text: str) -> str:
    """Keep chapter text intact while avoiding accidental extra front matter."""
    text = text.lstrip("\ufeff\n\r")
    return text.rstrip() + "\n"


def main() -> int:
    missing = [name for name in ORDER if not (ROOT / name).is_file()]
    if missing:
        print("缺少文件：" + ", ".join(missing), file=sys.stderr)
        return 1

    parts = [
        "# 《公式是怎么变成代码的》\n",
        "## 从数学关系到程序步骤的思维转换课\n\n",
        "> 本文件由 `tools/build_book.py` 按目录顺序生成。分章阅读请打开 [SUMMARY.md](SUMMARY.md)。\n",
    ]

    for name in ORDER:
        text = normalize_for_bundle((ROOT / name).read_text(encoding="utf-8"))
        parts.extend(["\n<div style=\"page-break-after: always;\"></div>\n\n", text])

    OUTPUT.write_text("".join(parts), encoding="utf-8", newline="\n")

    bundle = OUTPUT.read_text(encoding="utf-8")
    headings = len(re.findall(r"(?m)^#\s+", bundle))
    print(f"已生成：{OUTPUT}")
    print(f"字节数：{OUTPUT.stat().st_size}")
    print(f"一级标题数：{headings}")
    print(f"合并文件数：{len(ORDER)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
