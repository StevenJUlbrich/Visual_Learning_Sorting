from pathlib import Path
from mempalace.searcher import search_memories

WING = "visual_learning_sorting"  # corrected from sorting_visualizer
PALACE = Path("~/.mempalace/palace").expanduser()

print(f"Palace path: {PALACE}")
print(f"Exists: {PALACE.exists()}")

QUERIES = [
    "Phase 1 Build Max-Heap Phase 2 Extraction sift-down T1 compare T2 swap T3 tree T4 completion",
    "sine curve arc height interpolate x sprite exchange slots",
    "Locked algorithm set Bubble Selection Insertion Heap orange accent color",
    "strict MVC src visualizer controller model view SortResult",
]

def get_session_context() -> None:
    for query in QUERIES:
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
            similarity_text = "n/a" if similarity is None else f"{similarity:.3f}"

            print(f"Source: {source_file} [{room}] match={similarity_text}")
            print(result.get("text", "")[:400])
            print("\n---\n")

if __name__ == "__main__":
    get_session_context()