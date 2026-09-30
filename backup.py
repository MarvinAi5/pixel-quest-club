"""Create a consistent SQLite snapshot outside the public web directory."""
import os, sqlite3, sys
from pathlib import Path
if len(sys.argv) != 2:
    raise SystemExit("Usage: python3 backup.py /private/backup/club.sqlite")
source=Path(os.environ.get("PQC_DATA_DIR",Path(__file__).parent/"data"))/"club.sqlite"
dest=Path(sys.argv[1]).resolve()
if not source.exists(): raise SystemExit("No database to back up.")
if dest == source.resolve() or Path(__file__).parent.joinpath("public").resolve() in dest.parents:
    raise SystemExit("Choose a separate private destination.")
dest.parent.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(source) as a, sqlite3.connect(dest) as b: a.backup(b)
os.chmod(dest,0o600)
print("Snapshot created.")
