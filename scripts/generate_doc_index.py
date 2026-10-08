from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOC_DIR = ROOT / "doc"
README = DOC_DIR / "README.md"


def format_title(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").strip()


def build_index():
    lines = [
        "# ERP Documentation",
        "",
        "> Automatically generated documentation index.",
        "",
        "## Documentation Index",
        "",
    ]

    directories = sorted(
        path for path in DOC_DIR.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )

    for directory in directories:
        lines.append(f"### {format_title(directory.name)}")
        lines.append("")

        files = sorted(
            path for path in directory.rglob("*.md")
            if path.name.lower() != "readme.md"
        )

        for file in files:
            relative = file.relative_to(DOC_DIR).as_posix()
            title = format_title(file.stem)

            lines.append(f"- [{title}](./{relative})")

        lines.append("")

    lines.extend([
        "---",
        "",
        "## Documentation Roadmap",
        "",
        "The roadmap is maintained separately from the automatically "
        "generated documentation index.",
        "",
        "### Completed",
        "",
        "See the Documentation Index above for currently available documents.",
        "",
        "### In Progress",
        "",
        "- To be maintained according to the current project documentation plan.",
        "",
        "### Planned",
        "",
        "- Future documentation will be added according to project requirements.",
        "",
        "---",
        "",
        "## Documentation Conventions",
        "",
        "- Existing approved decisions must not be contradicted.",
        "- Related documents should be cross-referenced.",
        "- Terminology must remain consistent across the documentation.",
        "- Avoid unnecessary duplication.",
        "- Important constraints and edge cases must not be omitted.",
        "- Business decisions should not be redefined in technical documents.",
        "",
    ])

    README.write_text("\n".join(lines), encoding="utf-8")

    print(f"Generated: {README}")
    print(f"Directories: {len(directories)}")
    print(f"Markdown files: {sum(1 for _ in DOC_DIR.rglob('*.md'))}")


if __name__ == "__main__":
    build_index()