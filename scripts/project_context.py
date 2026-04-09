from pathlib import Path

from mempalace.searcher import search_memories

WING = "sorting_visualizer"
PALACE = Path("~/.mempalace/palace").expanduser()

QUERIES = [
    "heap sort two phase contract T1 T2 T3 T4 ticks",
    "arc swap motion coordinate interpolation dt",
    "decisions locked D-003 D-019 D-030",
    "MVC architecture controller view model",
]

def get_session_context() -> None:
    for query in QUERIES:
        print(f"Query: {query}")
        print(f"\n=== {query} ===")
        response = search_memories(query, palace_path=str(PALACE), wing=WING, n_results=2)

        if "error" in response:
            print(f"Error: {response['error']}")
            print("\n---\n")
            continue

        results = response.get("results", [])
        if not results:
            print("No results found.")
            print("\n---\n")
            continue

        for result in results:
            source_file = result.get("source_file", "unknown")
            room = result.get("room", "unknown")
            similarity = result.get("similarity")
            if similarity is None:
                similarity_text = "n/a"
            else:
                similarity_text = f"{similarity:.3f}"

            print(f"Source: {source_file} [{room}] match={similarity_text}")
            print(result.get("text", "")[:400])
            print("\n---\n")

if __name__ == "__main__":
    get_session_context()


