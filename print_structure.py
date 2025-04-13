import os

# Полный игнор — ничего не отображать
FULLY_EXCLUDED = {
    '__pycache__',
    '.git',
    'venv',
    'node_modules',
    '.idea',
    '.mypy_cache',
    '.pytest_cache',
    '.vscode',
    '.DS_Store',
    '.env.dev',
    'celerybeat-schedule',
    'celerybeat-schedule-shm',
    'celerybeat-schedule-wal',
}

# Отображать только на первом уровне
TOP_LEVEL_ONLY = {
    'alembic',
    'media',
    'static',
    'logs'
}


def sort_entries(entries, base_path):
    def sort_key(entry):
        full_path = os.path.join(base_path, entry)
        is_dir = os.path.isdir(full_path)
        is_hidden = entry.startswith('.')

        return (
            0 if is_dir else (1 if is_hidden else 2),
            entry.lower()
        )

    return sorted(entries, key=sort_key)


def print_tree(start_path: str, prefix: str = '', level: int = 0):
    try:
        entries = os.listdir(start_path)
    except PermissionError:
        return

    entries = [e for e in entries if e not in FULLY_EXCLUDED]
    entries = sort_entries(entries, start_path)

    for index, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        is_dir = os.path.isdir(path)
        display_name = f"{entry}/" if is_dir else entry
        connector = '└── ' if index == len(entries) - 1 else '├── '
        print(f'{prefix}{connector}{display_name}')

        if is_dir:
            if entry in TOP_LEVEL_ONLY and level >= 0:
                continue
            extension = '    ' if index == len(entries) - 1 else '│   '
            print_tree(path, prefix + extension, level + 1)


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    root_path = os.path.abspath(root)
    print(f'{os.path.basename(root_path)}/')
    print_tree(root_path)
