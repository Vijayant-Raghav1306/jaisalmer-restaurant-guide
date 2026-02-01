"""
Quick verification that everything is ready
"""

from pathlib import Path

print("="*60)
print("TICKET #6 VERIFICATION")
print("="*60)

checks = [
    ("Cleaned data", "data/processed/cleaned_dataset.json"),
    ("Documents", "data/processed/documents.json"),
    ("Vector DB", "data/vector_db/chroma_db"),
    ("Build report", "data/vector_db/chroma_db/build_report.json"),
]

all_good = True
for name, path in checks:
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {name}: {path}")
    if not exists:
        all_good = False

print("="*60)

if all_good:
    print("🎉 ALL SYSTEMS GO!")
    print("✅ Ready for Ticket #7: Build RAG Pipeline")
else:
    print("⚠️  Some files missing. Re-run the tools above.")

print("="*60)
