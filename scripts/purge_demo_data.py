#!/usr/bin/env python3
"""
Purge all demo data (storage files + database rows) from the Supabase project.

Health documents must never linger in a demo environment: this script empties
the storage bucket and the documents/analysis tables in FK-safe order.

Usage (from the repo root, with backend/.env configured):
    python scripts/purge_demo_data.py            # dry run: list what would be deleted
    python scripts/purge_demo_data.py --execute  # actually delete
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from supabase import create_client  # noqa: E402
from config.settings import settings  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="Perform the deletion. Without this flag, only lists targets.")
    args = parser.parse_args()

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    bucket = settings.SUPABASE_BUCKET_NAME

    files = supabase.storage.from_(bucket).list()
    documents = supabase.table("documents").select("id, filename, upload_date").execute().data

    print(f"Storage bucket '{bucket}': {len(files)} file(s)")
    for f in files:
        print(f"  - {f['name']}")
    print(f"Table 'documents': {len(documents)} row(s)")
    for d in documents:
        print(f"  - {d['id']}  {d['filename']}  ({d['upload_date']})")

    if not args.execute:
        print("\nDry run only. Re-run with --execute to delete everything listed above.")
        return 0

    if files:
        supabase.storage.from_(bucket).remove([f["name"] for f in files])
        print(f"Deleted {len(files)} storage file(s).")

    # documents cascades to analysis_results, which cascades to health_markers
    if documents:
        supabase.table("documents").delete().in_(
            "id", [d["id"] for d in documents]
        ).execute()
        print(f"Deleted {len(documents)} document row(s) (analysis data cascades).")

    print("Purge complete. Consider switching the bucket to private in the Supabase dashboard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
