import os, glob, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from endeavour.utils.cache_validator import validate_cache

def main():
    cache_dir = os.path.join("data","cache")
    files = sorted(glob.glob(os.path.join(cache_dir, "*.csv")))
    if not files:
        print("No cache files found.")
        return
    path = files[0]
    rep = validate_cache(path)
    print(rep)

if __name__ == "__main__":
    main()
