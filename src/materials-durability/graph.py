"""
graph.py  --  CC0

Load-path graph. Node = stone/brick/timber/soil-volume/footing. Edge = contact/
mortar/friction/tie. Load enters at a SOURCE node (load application) and must
reach a SINK (bedrock support). Redundancy = number of edge-disjoint paths from
source to sink = (Menger's theorem) the min cut = max flow with unit capacities.

When an edge's accumulated damage exceeds its capacity it is removed; load
reroutes through remaining paths. Collapse = no path from source to sink.

stdlib only. Max-flow via BFS augmenting paths (Edmonds-Karp) on unit capacities.
"""

from collections import defaultdict, deque


class LoadGraph:
    def __init__(self):
        self.adj = defaultdict(dict)      # u -> {v: capacity}
        self.edge_meta = {}               # (u,v) -> dict(capacity, damage, rates)
        self.nodes = set()
        self.source = None
        self.sink = None

    def add_edge(self, u, v, capacity=1.0, water_rate=0.0, ft_rate=0.0,
                 shear_cap=1.0):
        self.nodes.add(u); self.nodes.add(v)
        # store as undirected load path: both directions available for rerouting
        self.adj[u][v] = capacity
        self.adj[v][u] = capacity
        key = frozenset((u, v))
        self.edge_meta[key] = {
            "capacity": capacity, "damage": 0.0,
            "water_rate": water_rate, "ft_rate": ft_rate,
            "shear_cap": shear_cap, "alive": True,
        }

    def alive_edges(self):
        return [k for k, m in self.edge_meta.items() if m["alive"]]

    def kill_edge(self, key):
        m = self.edge_meta[key]
        if not m["alive"]:
            return
        m["alive"] = False
        u, v = tuple(key)
        self.adj[u].pop(v, None)
        self.adj[v].pop(u, None)

    # ---- redundancy = edge-disjoint paths = max flow (unit caps) ----
    def redundancy(self):
        if self.source is None or self.sink is None:
            return 0
        if self.source == self.sink:
            return 0
        # build residual with unit capacity per alive edge
        residual = defaultdict(lambda: defaultdict(float))
        for key in self.alive_edges():
            u, v = tuple(key)
            residual[u][v] = 1.0
            residual[v][u] = 1.0
        flow = 0
        while True:
            parent = {self.source: None}
            q = deque([self.source])
            found = False
            while q:
                u = q.popleft()
                if u == self.sink:
                    found = True
                    break
                for v, cap in residual[u].items():
                    if cap > 0 and v not in parent:
                        parent[v] = u
                        q.append(v)
            if not found:
                break
            # augment by 1 along path
            v = self.sink
            while parent[v] is not None:
                u = parent[v]
                residual[u][v] -= 1
                residual[v][u] += 1
                v = u
            flow += 1
        return flow

    def connected(self):
        return self.redundancy() > 0


# ---------------------------------------------------------------------------
# ARCHETYPE TOPOLOGY GENERATORS
# ---------------------------------------------------------------------------
# Each builds a layered graph: load -> structure layers -> soil -> bedrock.
# The structure layer's lateral connectivity sets the redundancy ceiling.
# ---------------------------------------------------------------------------

def _layered(width, depth, lateral, water_rate, ft_rate, shear_cap, name, jitter=0.18):
    """
    width   independent foundation columns (THIS sets path redundancy R0)
    depth   structural layers
    lateral tie density 0..1 -> becomes a LOAD-SHARING factor (slows per-edge
            damage); it does NOT add vertical path redundancy.
    jitter  per-edge capacity heterogeneity (material variance) so collapse
            staggers realistically instead of zippering in one year.
    """
    import random as _r
    rng = _r.Random(hash(name) & 0xffffffff)

    g = LoadGraph()
    g.source = "LOAD"
    g.sink = "BEDROCK"
    g.load_share = 1.0 / (1.0 + 1.5 * lateral)

    def jc(base):
        return base * (1.0 + rng.uniform(-jitter, jitter))

    def nid(layer, i):
        return f"L{layer}_{i}"

    for i in range(width):
        g.add_edge("LOAD", nid(0, i), capacity=jc(2.0), shear_cap=shear_cap)

    stride = max(1, round(1.0 / max(lateral, 1e-6)))
    for layer in range(depth):
        for i in range(width):
            if layer + 1 < depth:
                g.add_edge(nid(layer, i), nid(layer + 1, i), capacity=jc(1.0),
                           water_rate=water_rate, ft_rate=ft_rate, shear_cap=shear_cap)
            if i + 1 < width and (i % stride == 0):
                g.add_edge(nid(layer, i), nid(layer, i + 1), capacity=jc(2.0),
                           water_rate=water_rate * 0.3, ft_rate=ft_rate * 0.3,
                           shear_cap=shear_cap * 0.6)

    for i in range(width):
        g.add_edge(nid(depth - 1, i), f"SOIL_{i}", capacity=jc(1.0),
                   water_rate=water_rate * 1.5, ft_rate=ft_rate, shear_cap=shear_cap)
        g.add_edge(f"SOIL_{i}", "BEDROCK", capacity=jc(2.0), water_rate=water_rate * 1.5,
                   ft_rate=ft_rate * 0.5, shear_cap=shear_cap)
    return g


_TOPOLOGIES = {
    # ── PERMANENT ─────────────────────────────────────────────────────────────
    # width = independent foundation columns → R0 ceiling
    # lateral → load_share = 1/(1+1.5*lateral); slows cascade, does NOT add R0
    "granite":          dict(width=2,  depth=3, lateral=0.10, water_rate=0.05, ft_rate=0.20, shear_cap=0.90),
    "field_stone":      dict(width=3,  depth=3, lateral=0.40, water_rate=0.30, ft_rate=0.40, shear_cap=0.65),
    "roman_pozzolan":   dict(width=4,  depth=3, lateral=0.30, water_rate=0.15, ft_rate=0.40, shear_cap=0.85),
    "massive_arch":     dict(width=3,  depth=3, lateral=0.50, water_rate=0.40, ft_rate=0.50, shear_cap=0.90),
    "concrete":         dict(width=2,  depth=3, lateral=0.30, water_rate=0.50, ft_rate=0.50, shear_cap=0.85),
    "modern_reinforced":dict(width=5,  depth=3, lateral=0.60, water_rate=0.80, ft_rate=0.50, shear_cap=0.95),
    "lumber":           dict(width=5,  depth=3, lateral=0.70, water_rate=0.70, ft_rate=0.30, shear_cap=0.75),
    "dry_stone":        dict(width=8,  depth=4, lateral=1.00, water_rate=0.60, ft_rate=0.70, shear_cap=0.70),
    # ── RENEWAL ───────────────────────────────────────────────────────────────
    "timber_laced":     dict(width=6,  depth=4, lateral=0.85, water_rate=0.90, ft_rate=0.60, shear_cap=0.75),
    "treehouse":        dict(width=4,  depth=2, lateral=0.50, water_rate=0.80, ft_rate=0.20, shear_cap=0.60),
    # ice/snow: no FT or water edge damage; thermal_melt governs analytically
    "ice":              dict(width=3,  depth=2, lateral=0.40, water_rate=0.00, ft_rate=0.00, shear_cap=0.60),
    "snow":             dict(width=2,  depth=2, lateral=0.30, water_rate=0.00, ft_rate=0.00, shear_cap=0.50),
    "cob":              dict(width=5,  depth=3, lateral=0.40, water_rate=0.90, ft_rate=0.70, shear_cap=0.55),
    "bamboo":           dict(width=8,  depth=3, lateral=0.90, water_rate=0.80, ft_rate=0.30, shear_cap=0.65),
    "bamboo_and_clay":  dict(width=6,  depth=3, lateral=0.80, water_rate=0.75, ft_rate=0.35, shear_cap=0.60),
    "willow_and_clay":  dict(width=6,  depth=3, lateral=0.70, water_rate=0.85, ft_rate=0.40, shear_cap=0.55),
    "sod":              dict(width=4,  depth=2, lateral=0.40, water_rate=0.80, ft_rate=0.50, shear_cap=0.45),
    "straw":            dict(width=3,  depth=2, lateral=0.30, water_rate=0.90, ft_rate=0.60, shear_cap=0.50),
}


def build_graph(archetype_key, base_scale=1):
    """
    archetype_key selects topology character. Width (independent columns) is the
    redundancy driver and is archetype-specific.
    """
    if archetype_key not in _TOPOLOGIES:
        raise ValueError(f"No graph topology for '{archetype_key}'")
    A = _TOPOLOGIES[archetype_key]
    return _layered(width=A["width"] * base_scale, depth=A["depth"], lateral=A["lateral"],
                    water_rate=A["water_rate"], ft_rate=A["ft_rate"],
                    shear_cap=A["shear_cap"], name=archetype_key)
