from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

BASE_DIR: Path = Path(__file__).parent.parent
SOURCE_DIR: Path = BASE_DIR / "bozupy"
if not SOURCE_DIR.is_dir():
    raise FileNotFoundError(f"Source directory not found: {SOURCE_DIR}")


def _path_str(filepath: Path) -> str:
    return str(filepath)[str(filepath).find("bozupy/bozupy/") + len("bozupy/"):]


@dataclass
class Error:
    filepath: Path
    line: int
    message: str

    def __str__(self) -> str:
        return f"{_path_str(self.filepath)}:{self.line}: {self.message}"


def _read_files_recursive(excluded: set[str], path: Path = SOURCE_DIR) -> Iterator[Path]:
    for item in path.iterdir():
        if item.is_dir():
            if item.name not in excluded:
                yield from _read_files_recursive(excluded, item)
        elif item.suffix == ".py":
            yield item


def check_import_format(excluded: set[str]) -> Iterator[Error]:
    for file_ in _read_files_recursive(excluded):
        with file_.open(mode="r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if "from bozupy" in line or "import bozupy" in line:
                    yield Error(file_, i + 1, "Import from bozupy is not allowed.")


def check_publish_modules(path: Path = SOURCE_DIR, excluded: set[str] | None = None) -> Iterator[Error]:
    excluded = excluded or set([])
    published: set[str] = set([])
    init_py: Path = path / "__init__.py"
    if not init_py.exists():
        raise FileNotFoundError(f"{init_py} not found")
    with init_py.open(mode="r", encoding="utf-8") as f:
        for line in f:
            if ".__name__" in line:
                published.add(line.split(".")[0].strip())
    for item in path.iterdir():
        if not item.is_dir():
            continue
        elif item.name.startswith("_"):
            continue
        elif item.name in excluded:
            continue
        if item.name not in published:
            yield Error(init_py, 0, f"Module {item.name} is not published at {_path_str(init_py)}.")


def check_publish_members(path: Path = SOURCE_DIR, excluded: set[str] | None = None) -> Iterator[Error]:
    excluded = excluded or set([])
    published: set[str] = set([])
    init_py: Path = path / "__init__.py"
    if not init_py.exists():
        raise FileNotFoundError(f"{init_py} not found")
    with init_py.open(mode="r", encoding="utf-8") as f:
        for line in f:
            if ".__name__" in line:
                published.add(line.split(".")[0].strip())
    parent_init_py: Path = path.parent / "__init__.py"
    if parent_init_py.exists():
        with parent_init_py.open(mode="r", encoding="utf-8") as f:
            for line in f:
                if ".__name__" in line:
                    published.add(line.split(".")[0].strip())
    for item in path.iterdir():
        if item.is_dir():
            if item.name not in ["__pycache__"] and item.name not in excluded:
                yield from check_publish_members(item, excluded)
            continue
        elif item.name == "__init__.py" or item.suffix != ".py" or item.name in excluded:
            continue

        with item.open(mode="r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.startswith("def ") or line.startswith("class "):
                    if line.startswith("def _") or line.startswith("class _"):
                        continue
                    if "(" in line:
                        name: str = line.split(" ")[1].split("(")[0]
                    else:
                        name = line.split(" ")[1].split(":")[0]
                    if name not in published:
                        yield Error(item, i + 1, f"function/class {name} is not published at {_path_str(init_py)}.")


if __name__ == "__main__":
    errors: list[Error] = [e for e in check_import_format(excluded={"cli"})]
    errors.extend([e for e in check_publish_modules(excluded={"cybozu"})])
    errors.extend([e for e in check_publish_modules(path=(SOURCE_DIR / "kintone"), excluded={"user"})])
    errors.extend([e for e in check_publish_modules(path=(SOURCE_DIR / "garoon"), excluded={"base"})])
    errors.extend([e for e in check_publish_modules(path=(SOURCE_DIR / "slash"), excluded={""})])
    errors.extend([e for e in check_publish_members(excluded={"user", "exception.py", "dxo.py", "util.py", "setting.py"})])
    if errors:
        for error in errors:
            print(error)
        exit(1)
    print("No errors found.")
    exit(0)
