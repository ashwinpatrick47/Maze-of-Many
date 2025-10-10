# validate_taskd.py
from solvers.task_d_solver import task_d_solver
from solvers.util import generate_actions_from_paths
from helpers.helpers import load_maze_from_txt          # loads saved maze .txt
from MST.prims import primMST                           # build MST like maze_runner.py
from graph.coordinate import Coordinate
import json
from typing import Tuple


def parse_entrance(cfg) -> Tuple[int, int]:
    """Parse entrance from config.json in multiple possible formats."""
    ent = cfg.get("entrance", [0, 0])
    if isinstance(ent, (list, tuple)) and len(ent) == 2:
        erow, ecol = int(ent[0]), int(ent[1])
        return erow, ecol
    if isinstance(ent, dict) and "row" in ent and "col" in ent:
        return int(ent["row"]), int(ent["col"])
    if isinstance(ent, str):
        # formats like "5,5" or "5 5"
        for sep in [",", " "]:
            if sep in ent:
                parts = ent.split(sep)
                if len(parts) == 2:
                    return int(parts[0]), int(parts[1])
    # fallback
    return 0, 0


def pick_start_from_mst(mst_graph, erow: int, ecol: int) -> Coordinate:
    """Return the MST's *own* Coordinate for (erow, ecol). If not found, pick the nearest."""
    verts = list(mst_graph.getVertices())
    # exact match by row/col
    exact = [v for v in verts if v.getRow() == erow and v.getCol() == ecol]
    if exact:
        return exact[0]
    # nearest by Manhattan distance
    def manhattan(v): return abs(v.getRow() - erow) + abs(v.getCol() - ecol)
    nearest = min(verts, key=manhattan)
    return nearest


def validate_one(graph, start: Coordinate, clone_cost: int):
    """Run Task D on MST `graph` from `start` and assert core invariants."""
    all_paths, max_total_cost, clone_count = task_d_solver(graph, start, clone_cost)

    # 1) Coverage: visited == all vertices
    seen = {v for path in all_paths for v in path}
    V = set(graph.getVertices())
    assert seen == V, f"Coverage mismatch: visited={len(seen)} / total={len(V)}"

    # 2) Path validity: edges must be real and positive-weight
    for i, path in enumerate(all_paths):
        for a, b in zip(path, path[1:]):
            assert b in graph.neighbours(a), f"Non-neighbor in path {i}: {a}->{b}"
            w = graph.getWeight(a, b)
            assert w > 0, f"Non-positive edge in path {i}: {a}->{b} (w={w})"

    # 3) Clone count consistency
    assert clone_count == len(all_paths) - 1, "clone_count != len(all_paths)-1"

    # 4) Cost recomputation equals reported makespan
    actions = generate_actions_from_paths(graph, all_paths, clone_cost)
    recomputed = max(sum(a) for a in actions)
    assert recomputed == max_total_cost, f"Cost mismatch: {recomputed} vs {max_total_cost}"

    print(f"d={clone_cost:<5} → clones={clone_count:<4} | cost={max_total_cost}")
    return clone_count, max_total_cost


if __name__ == "__main__":
    # 1) Load the same saved maze file you used (full maze, may have cycles)
    full_graph = load_maze_from_txt("mazes/specMaze.txt", graph_type="matrix")
    print("Maze loaded from mazes/specMaze.txt as matrix graph")

    # 2) Build the MST (Task D expects a tree)
    mst_graph = primMST(full_graph)
    print("MST built with Prim's")

    # 3) Read entrance (robust parse)
    try:
        with open("config.json", "r") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}

    erow, ecol = parse_entrance(cfg)
    start = pick_start_from_mst(mst_graph, erow, ecol)
    print(f"Using start ({start.getRow()},{start.getCol()}) | degree={len(mst_graph.neighbours(start))}")

    # 4) Validate across representative clone_cost values
    for d in [1, 5, 10, 100, 1000]:
        validate_one(mst_graph, start, d)

    print("\nTask D validation: All tests passed!")
