import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.db.utils import create_superuser


async def main():
    """Usage: python create_superuser.py <email> <password>"""
    if len(sys.argv) != 3:
        print("Usage: python create_superuser.py <email> <password>")
        return

    email = sys.argv[1]
    password = sys.argv[2]
    await create_superuser(email, password)


if __name__ == "__main__":
    asyncio.run(main())
