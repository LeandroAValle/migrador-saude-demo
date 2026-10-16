from pathlib import Path
from .pipeline import export_snapshot

if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "site" / "data" / "snapshot.json"
    print(f"Snapshot sintético: {export_snapshot(output)}")
