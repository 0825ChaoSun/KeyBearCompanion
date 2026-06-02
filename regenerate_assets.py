from asset_generator import ASSETS_DIR, generate_assets


if __name__ == "__main__":
    generate_assets(ASSETS_DIR, overwrite=True)
    print(f"Regenerated fallback KeyBear assets in {ASSETS_DIR}")
    print("User-owned assets in assets/user/ are preserved and loaded first.")
