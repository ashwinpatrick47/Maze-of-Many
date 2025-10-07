# -------------------------------------------------
# Validation script for Task D
# Place this in the root directory (same level as maze_runner.py)
# -------------------------------------------------

from graph.coordinate import Coordinate
from graph.adjacency_matrix import AdjacencyMatrixGraph as Graph
from solvers.task_d_solver import task_d_solver
from solvers.always_clone import always_clone_solver
from solvers.no_clone import no_clone_solver
from solvers.util import generate_actions_from_paths


def assert_paths_legal(graph, all_paths):
    """Check that each path follows valid edges and no consecutive duplicates."""
    for idx, p in enumerate(all_paths):
        assert p, f"Explorer {idx} has empty path"
        for a, b in zip(p, p[1:]):
            assert not (a.getRow() == b.getRow() and a.getCol() == b.getCol()), f"Duplicate step in explorer {idx}: {a}"
            assert graph.hasEdge(a, b), f"Illegal step explorer {idx}: {a} -> {b}"


def assert_full_coverage(graph, all_paths):
    """Ensure all vertices are covered at least once."""
    seen = set()
    for p in all_paths:
        for v in p:
            seen.add((v.getRow(), v.getCol()))
    assert len(seen) == len(graph.getVertices()), f"Coverage {len(seen)} != |V|={len(graph.getVertices())}"


def assert_clone_paths_well_formed(all_paths, start):
    """Check that each clone path begins correctly."""
    for i, p in enumerate(all_paths[1:], 1):
        assert len(p) >= 2, f"Clone {i} path too short"
        a, b = p[0], p[1]
        assert isinstance(a, type(start)) and isinstance(b, type(start)), "Invalid coordinate type in clone path"


def fmt_paths(paths):
    """Format coordinate paths for clean printing."""
    return [[(v.getRow(), v.getCol()) for v in p] for p in paths]


def tiny_star_test():
    """Build a small star-shaped graph to test branching and cloning."""
    g = Graph(3,3)
    c = lambda r, c: Coordinate(r, c)
    center = c(1, 1)
    leaves = [c(1, 0), c(0, 1), c(2, 1)]
    g.addVertices([center] + leaves)
    g.addEdge(center, leaves[0], 2)
    g.addEdge(center, leaves[1], 3)
    g.addEdge(center, leaves[2], 7)

    for clone_cost in (0, 1, 5, 100):
        all_paths, max_cost, clones = task_d_solver(g, center, clone_cost)
        # structural checks
        assert_paths_legal(g, all_paths)
        assert_full_coverage(g, all_paths)
        assert_clone_paths_well_formed(all_paths, center)
        # cost recompute matches
        actions = generate_actions_from_paths(g, all_paths, clone_cost)
        assert max_cost == max(sum(a) for a in actions), "Cost mismatch"
        print(f"[star] clone_cost={clone_cost} clones={clones} max_cost={max_cost}")
        print("paths=", fmt_paths(all_paths))

        # sanity vs baselines
        no_paths, no_cost, _ = no_clone_solver(g, center, clone_cost)
        ac_paths, ac_cost, ac_clones = always_clone_solver(g, center, clone_cost)
        # low cost → expect ≤ no_clone
        if clone_cost <= 1:
            assert max_cost <= no_cost, "Expected task_d ≤ no_clone for cheap clones"
        # very high cost → should be close to no_clone (never worse than always_clone)
        if clone_cost >= 100:
            assert max_cost <= max(no_cost, ac_cost), "Expected task_d not worse than baselines at high cost"

    print("✅ OK: tiny_star_test passed")


def straight_line_test():
    """A simple straight line — no branching, so no clones expected."""
    g = Graph(1,4)
    c = lambda r, c: Coordinate(r, c)
    vs = [c(0, i) for i in range(4)]
    g.addVertices(vs)
    g.addEdge(vs[0], vs[1], 1)
    g.addEdge(vs[1], vs[2], 2)
    g.addEdge(vs[2], vs[3], 3)

    all_paths, max_cost, clones = task_d_solver(g, vs[0], clone_cost=5)
    assert_paths_legal(g, all_paths)
    assert_full_coverage(g, all_paths)
    assert clones == 0, "Line should produce 0 clones"
    print("✅ OK: straight_line_test passed", fmt_paths(all_paths), "cost=", max_cost)


if __name__ == "__main__":
    tiny_star_test()
    straight_line_test()
    print("\n🎉 All validations passed successfully!")
