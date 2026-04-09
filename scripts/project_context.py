from pathlib import Path
from mempalace.searcher import search_memories

WING = "visual_learning_sorting"  # corrected from sorting_visualizer
PALACE = Path("~/.mempalace/palace").expanduser()

print(f"Palace path: {PALACE}")
print(f"Exists: {PALACE.exists()}")

QUERIES = [
    # Heap Sort tick contract (working)
    "Phase 1 Build Max-Heap Phase 2 Extraction sift-down T1 compare T2 swap T3 tree T4 completion",

    # Animation physics (working)
    "sine curve arc height interpolate x sprite exchange slots",

    # Locked decisions — use D-number format the doc actually uses
    "D-002 D-003 D-004 D-017 D-019 locked decided deferred",

    # Architecture — try the actual directory names and class names
    "models views controllers bubble.py insertion.py heap.py selection.py orchestrator.py sprite.py panel.py",

    # Acceptance tests
    "AT-01 AT-02 AT-03 startup baseline independent queue completion race",

    # Implementation status
    "implementation tracker milestone phase brick checklist",
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