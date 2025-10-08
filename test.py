# -------------------------------------------------
# Validation script for Task D
# Save as: scratch_task_d_check.py  (repo root)
# -------------------------------------------------

from solvers.util import generate_actions_from_paths
from solvers.no_clone import no_clone_solver
from solvers.always_clone import always_clone_solver
from solvers.task_d_solver import task_d_solver  # <-- your solver module

from graph.coordinate import Coordinate

# Prefer matrix graph if available; fall back to base Graph.
try:
    from graph.adjacency_matrix import AdjacencyMatrixGraph as Graph
    _HAS_SHAPE = True
except Exception:
    from graph.graph import Graph
    _HAS_SHAPE = False


# ---------- helpers ----------
def assert_paths_legal(graph, all_paths):
    for idx, p in enumerate(all_paths):
        assert p, f"Explorer {idx} has empty path"
        for a, b in zip(p, p[1:]):
            same = (a.getRow() == b.getRow() and a.getCol() == b.getCol())
            assert not same, f"Duplicate step in explorer {idx}: {a.getRow(),a.getCol()}"
            assert graph.hasEdge(a, b), f"Illegal step explorer {idx}: {a.getRow(),a.getCol()} -> {b.getRow(),b.getCol()}"


def assert_full_coverage(graph, all_paths):
    seen = set()
    for p in all_paths:
        for v in p:
            seen.add((v.getRow(), v.getCol()))
    V = graph.getVertices()
    assert len(seen) == len(V), f"Coverage {len(seen)} != |V|={len(V)}"


def assert_clone_paths_well_formed(all_paths):
    for i, p in enumerate(all_paths[1:], 1):
        assert len(p) >= 2, f"Clone {i} path too short: {p}"


def fmt_paths(paths):
    return [[(v.getRow(), v.getCol()) for v in p] for p in paths]


# ---------- tests ----------
def tiny_star_test():
    """Star centered at (1,1) with leaves and weights 2,3,7 (matches your mini-example)."""
    c = lambda r, c: Coordinate(r, c)
    center = c(1, 1)
    leaves = [c(1, 0), c(0, 1), c(2, 1)]

    g = Graph(3, 3) if _HAS_SHAPE else Graph()
    g.addVertices([center] + leaves)
    g.addEdge(center, leaves[0], 2)
    g.addEdge(center, leaves[1], 3)
    g.addEdge(center, leaves[2], 7)

    for clone_cost in (0, 1, 5, 100):
        all_paths, max_cost, clones = task_d_solver(g, center, clone_cost)

        assert_paths_legal(g, all_paths)
        assert_full_coverage(g, all_paths)
        assert_clone_paths_well_formed(all_paths)

        actions = generate_actions_from_paths(g, all_paths, clone_cost)
        assert max_cost == max(sum(a) for a in actions), "Cost mismatch vs recompute"

        print(f"[star] clone_cost={clone_cost}  clones={clones}  max_cost={max_cost}")
        print("paths=", fmt_paths(all_paths))

        # quick sanity vs baselines (not strict optimality)
        _, no_cost, _ = no_clone_solver(g, center, clone_cost)
        _, ac_cost, _ = always_clone_solver(g, center, clone_cost)
        if clone_cost <= 1:
            assert max_cost <= no_cost, "Expected task_d ≤ no_clone when clones are cheap"
        if clone_cost >= 100:
            assert max_cost <= max(no_cost, ac_cost), "Expected task_d not worse than baselines when clones are huge"

    print("✅ OK: tiny_star_test passed")


def straight_line_test():
    """No branching => 0 clones expected."""
    c = lambda r, c: Coordinate(r, c)
    vs = [c(0, i) for i in range(4)]

    g = Graph(1, 4) if _HAS_SHAPE else Graph()
    g.addVertices(vs)
    g.addEdge(vs[0], vs[1], 1)
    g.addEdge(vs[1], vs[2], 2)
    g.addEdge(vs[2], vs[3], 3)

    all_paths, max_cost, clones = task_d_solver(g, vs[0], clone_cost=5)
    assert_paths_legal(g, all_paths)
    assert_full_coverage(g, all_paths)
    assert clones == 0, f"Line should have 0 clones, got {clones}"
    print("✅ OK: straight_line_test passed", fmt_paths(all_paths), "cost=", max_cost)


if __name__ == "__main__":
    tiny_star_test()
    straight_line_test()
    print("\n🎉 All validations passed successfully!")
