from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS = ["00.md"] + [f"{number:02d}.md" for number in range(1, 27)]
TAIL = [
    "Epilogue.md",
    "Appendix-A.md",
    "Appendix-B.md",
    "Appendix-C.md",
    "Appendix-D.md",
    "Appendix-E.md",
]
EXPECTED = CHAPTERS + TAIL + ["SUMMARY.md", "README.md"]
INCOMPLETE_MARKERS = ("TODO", "TBD", "待补", "待完成", "此处略", "内容略")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def exercise_numbers(text: str) -> set[int]:
    patterns = [
        r"(?m)^\s*(\d{1,2})[.、]\s*",
        r"(?m)^#{2,4}\s*(?:练习|题目|第)?\s*(\d{1,2})(?:\s|[：:.、])",
        r"(?m)^\s*(?:练习|题目)\s*(\d{1,2})(?:\s|[：:.、])",
    ]
    numbers: set[int] = set()
    for pattern in patterns:
        numbers.update(int(value) for value in re.findall(pattern, text))
    return {number for number in numbers if 1 <= number <= 50}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for name in EXPECTED:
        path = ROOT / name
        if not path.is_file():
            fail(errors, f"缺少文件：{name}")
            continue

        text = path.read_text(encoding="utf-8")
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
        if not first_line.startswith("# "):
            fail(errors, f"{name} 的首个非空行不是一级标题")

        minimum = 1_500 if name in CHAPTERS else 500
        if len(text) < minimum:
            fail(errors, f"{name} 内容过短：{len(text)} 字符，最低检查值 {minimum}")

        fence_count = len(re.findall(r"(?m)^```", text))
        if fence_count % 2:
            fail(errors, f"{name} 的代码围栏数量为奇数：{fence_count}")

        for marker in INCOMPLETE_MARKERS:
            if marker in text:
                fail(errors, f"{name} 含未完成标记：{marker}")

    for number in range(4, 27):
        name = f"{number:02d}.md"
        path = ROOT / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "错误博物馆" not in text:
            warnings.append(f"{name} 未出现“错误博物馆”字样，请人工确认是否有等价错误分析")
        if not re.search(r"(?m)^\|.+\|\s*$", text):
            fail(errors, f"{name} 未检测到 Markdown 状态表")
        if not any(word in text for word in ("翻译训练", "本章训练", "训练题", "本章挑战", "练习")):
            warnings.append(f"{name} 未检测到明确的训练/挑战标题")

    summary = ROOT / "SUMMARY.md"
    if summary.is_file():
        links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", summary.read_text(encoding="utf-8"))
        for link in links:
            if not (ROOT / link).is_file():
                fail(errors, f"SUMMARY.md 中的链接不存在：{link}")

    chapter_26 = ROOT / "26.md"
    if chapter_26.is_file() and "int main" not in chapter_26.read_text(encoding="utf-8"):
        warnings.append("26.md 未检测到 int main，请确认综合程序是否完整")

    for name in ("Appendix-C.md", "Appendix-D.md"):
        path = ROOT / name
        if not path.is_file():
            continue
        numbers = exercise_numbers(path.read_text(encoding="utf-8"))
        missing = sorted(set(range(1, 51)) - numbers)
        if missing:
            warnings.append(
                f"{name} 的编号识别为 {len(numbers)}/50；未识别："
                + ", ".join(map(str, missing))
            )

    print(f"检查目录：{ROOT}")
    print(f"预期文件数：{len(EXPECTED)}")
    print(f"错误数：{len(errors)}")
    print(f"警告数：{len(warnings)}")

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARN: {message}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
