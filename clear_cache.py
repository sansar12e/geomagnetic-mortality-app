"""Clear Streamlit cache to reload fresh data."""
import streamlit as st
import shutil
from pathlib import Path

# Clear Streamlit cache directory
cache_dir = Path.home() / ".streamlit" / "cache"
if cache_dir.exists():
    try:
        shutil.rmtree(cache_dir)
        print(f"✓ Cleared Streamlit cache directory: {cache_dir}")
    except Exception as e:
        print(f"✗ Could not clear cache: {e}")
else:
    print("No cache directory found")

print("\nStreamlit cache cleared!")
print("Now restart the app with: poetry run streamlit run streamlit_app.py")


