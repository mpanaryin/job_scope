import os
from pathlib import Path


def create_module_structure(module_name: str, base_path: str = "."):
    """Создаёт шаблон модуля с подпапками под clean architecture."""
    module_root = Path(base_path) / module_name
    if module_root.exists():
        raise ValueError(f"Module '{module_name}' already exists")

    subfolders = [
        "application",
        "domain",
        "infrastructure",
        "presentation",
    ]

    # Создаём корневую папку модуля
    os.makedirs(module_root, exist_ok=True)
    (module_root / "__init__.py").touch()

    # Создаём подпапки и __init__.py в них
    for folder in subfolders:
        path = module_root / folder
        os.makedirs(path, exist_ok=True)
        (path / "__init__.py").touch()

    print(f"Module '{module_name}' created")


if __name__ == "__main__":
    import sys
    try:
        module = sys.argv[1]
    except IndexError as e:
        print('Specify the path to the module relative to the root folders')
    else:
        create_module_structure(module)
