"""Interactive semantic search for cost data."""

import logging
from qdrant_client import QdrantClient
from vector_db.embedding_model import EmbeddingModel
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    Fore = Style = type('obj', (object,), {'RED': '', 'GREEN': '', 'YELLOW': '', 'CYAN': '', 'MAGENTA': '', 'WHITE': '', 'BRIGHT': ''})()

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def show_top_records(client: QdrantClient, collection_name: str, limit: int = 5) -> None:
    """Display top anomalies and spenders from Qdrant."""
    try:
        all_points = client.scroll(collection_name=collection_name, with_payload=True)[0]

        anomalies = [p.payload for p in all_points if p.payload.get("anomaly_flag")]
        top_spenders = sorted(all_points, key=lambda x: x.payload.get("cost", 0), reverse=True)

        print(Fore.YELLOW + Style.BRIGHT + "\nTop Anomalies:")
        if anomalies:
            for i, a in enumerate(anomalies[:limit], 1):
                print(Fore.RED + f"{i}. {a.get('service_name')} | ${a.get('cost')} | {a.get('account_id')}")
        else:
            print(Fore.GREEN + "No anomalies detected!")

        print(Fore.YELLOW + Style.BRIGHT + "\nTop Spenders:")
        for i, s in enumerate(top_spenders[:limit], 1):
            p = s.payload
            print(Fore.CYAN + f"{i}. {p.get('service_name')} | ${p.get('cost')} | {p.get('account_id')}")
        print(Fore.YELLOW + "-" * 60 + "\n")

    except Exception as e:
        logger.error("Failed to fetch records: %s", e)


def main() -> None:
    """Interactive semantic search CLI."""
    try:
        client = QdrantClient(url="http://localhost:6333", check_compatibility=False)
        model = EmbeddingModel()
        collection_name = "cost_data"

        logger.info("Semantic Search CLI started")
        show_top_records(client, collection_name, limit=5)
        print("Type 'exit' or 'quit' to quit\n")

        while True:
            query = input(Fore.WHITE + "Enter search query: ").strip()
            if query.lower() in ['exit', 'quit']:
                break

            try:
                embeddings = model.encode([query])
                query_vector = embeddings[0] if len(embeddings) > 0 else None
                
                if query_vector is None:
                    print(Fore.RED + "Failed to generate embedding")
                    continue
                    
                results = client.search(
                    collection_name=collection_name,
                    query_vector=query_vector.tolist(),
                    limit=5,
                    with_payload=True
                )

                if not results:
                    print(Fore.GREEN + "No matching results found.\n")
                    continue

                print(Fore.MAGENTA + f"\nTop {len(results)} results for: '{query}'\n")
                for i, r in enumerate(results, start=1):
                    payload = r.payload
                    color = Fore.CYAN
                    if payload.get('anomaly_flag'):
                        color = Fore.RED + Style.BRIGHT
                    
                    print(color + f"{i}. {payload.get('service_name')} | ${payload.get('cost')} | {payload.get('region')}")
                    print(color + f"   Account: {payload.get('account_id')} | Usage: {payload.get('usage_quantity')}")
                    if payload.get('anomaly_flag'):
                        print(color + f"   ANOMALY DETECTED")
                    print()

                print(Fore.YELLOW + "-" * 60)

            except Exception as search_err:
                logger.error("Error during search: %s", search_err, exc_info=True)

    except Exception as e:
        logger.error("Semantic search CLI failed to start: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
