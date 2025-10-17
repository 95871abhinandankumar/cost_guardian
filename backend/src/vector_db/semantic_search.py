from qdrant_client import QdrantClient
from vector_db.embedding_model import EmbeddingModel
from colorama import init, Fore, Style

init(autoreset=True)

def show_top_records(client, collection_name, limit=5):
    """Show top anomalies and top spenders at startup."""
    all_points = client.scroll(collection_name=collection_name, with_payload=True)[0]

    anomalies = [p.payload for p in all_points if p.payload.get("anomaly_flag")]
    top_spenders = sorted(all_points, key=lambda x: x.payload.get("cost", 0), reverse=True)

    print(Fore.YELLOW + Style.BRIGHT + "\n🚨 Top Anomalies:")
    if anomalies:
        for i, a in enumerate(anomalies[:limit], 1):
            print(Fore.RED + f"{i}. Service: {a.get('service_name')} | Region: {a.get('region')} | Cost: {a.get('cost')} USD | Account: {a.get('account_id')}")
    else:
        print(Fore.GREEN + "No anomalies detected!")

    print(Fore.YELLOW + Style.BRIGHT + "\n💰 Top Spenders:")
    for i, s in enumerate(top_spenders[:limit], 1):
        p = s.payload
        print(Fore.CYAN + f"{i}. Service: {p.get('service_name')} | Region: {p.get('region')} | Cost: {p.get('cost')} USD | Account: {p.get('account_id')}")
    print(Fore.YELLOW + "-" * 60 + "\n")

def main():
    client = QdrantClient(url="http://localhost:6333", check_compatibility=False)
    model = EmbeddingModel()
    collection_name = "cost_data"

    print(Fore.YELLOW + Style.BRIGHT + "📝 Semantic Search Demo (Hackathon Ready)")

    # Show top anomalies and top spenders at startup
    show_top_records(client, collection_name, limit=5)

    print("Type 'exit' to quit\n")

    while True:
        query = input(Fore.WHITE + "Enter your search query: ")
        if query.lower() in ['exit', 'quit']:
            break

        query_vector = model.encode([query])[0]

        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector.tolist(),
            limit=5,
            with_payload=True
        )

        print(Fore.MAGENTA + f"\nTop {len(results)} results for: '{query}'\n")
        for i, r in enumerate(results, start=1):
            payload = r.payload

            if payload.get('anomaly_flag'):
                color = Fore.RED + Style.BRIGHT
            elif payload.get('service_name') == "EC2":
                color = Fore.GREEN
            else:
                color = Fore.CYAN

            print(color + f"{i}. Service: {payload.get('service_name')}")
            print(color + f"   Region: {payload.get('region')}")
            print(color + f"   Cost: {payload.get('cost')} {payload.get('currency')}")
            print(color + f"   Usage: {payload.get('usage_quantity')}")
            print(color + f"   Account: {payload.get('account_id')}")
            print(color + f"   Tags: {payload.get('tags')}")
            print(color + f"   Anomaly: {payload.get('anomaly_flag')}\n")

        print(Fore.YELLOW + "-" * 60)

if __name__ == "__main__":
    main()
