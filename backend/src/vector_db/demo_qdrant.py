from qdrant_client import QdrantClient

def main():
    # Connect to local Qdrant
    client = QdrantClient(url="http://localhost:6333", check_compatibility=False)

    # 1️⃣ List all collections
    print("📂 Collections in your Qdrant instance:")
    collections = client.get_collections()

    if not collections.collections:
        print("⚠️ No collections found!")
        return

    for col in collections.collections:
        # Vector info may not be available in this version
        size = getattr(getattr(col, 'vectors', None), 'size', 'unknown')
        distance = getattr(getattr(col, 'vectors', None), 'distance', 'unknown')
        print(f"- {col.name} (vector size: {size}, distance: {distance})")
    print()

    # 2️⃣ Pick first collection
    collection_name = collections.collections[0].name

    # 3️⃣ Count total records
    count = client.count(collection_name)
    print(f"📝 Total records in '{collection_name}': {count.count}\n")

    # 4️⃣ Fetch first 5 records
    print("🔍 Sample records:")
    points, _next_page = client.scroll(collection_name=collection_name, limit=5)
    for pt in points:
        print(pt.payload)
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    main()
