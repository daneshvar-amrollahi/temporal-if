"""Is a candidate spec already covered by the grammar of proposals/temporal-if.md (Section 3.2-3.3)?

A candidate is an LTLf formula (future and past operators) over named atoms, each atom a property
of one round: of the assistant reply (side A) or of the user message (side U). It is covered if,
on every trace in the test set, it agrees with one grammar instance or with a conjunction of
grammar instances (instructions can be stacked). Grammar roles are filled conservatively:
the action `a` by any non-constant Boolean function of the A atoms (pairwise combos if >2 atoms),
the pattern trigger `u` likewise over U atoms, scope triggers `o`, `c` by a U literal.
Scopes use Dwyer's convention when a trigger is absent: FROM with no opener holds vacuously,
UNTIL with no closer covers the whole trace.

Usage:
  python3 covered.py --atoms "a:A,h:U" --ltl "G(h -> X a)"
  python3 covered.py --selftest
Formula syntax: true false ! & | -> <-> X N F G U W R, F<=k G<=k X^k N^k,
past: Y (yesterday), Z (weak yesterday), O (once), H (historically), S (since).
Binary operators are right-associative; use parentheses.
"""
import argparse, itertools, random, re, sys

# ---------------- LTLf ----------------
TOK = re.compile(r"\s*(<->|->|F<=\d+|G<=\d+|X\^\d+|N\^\d+|[()!&|]|[A-Za-z_][A-Za-z0-9_]*)")
UN = {"X", "N", "F", "G", "Y", "Z", "O", "H", "!"}
BIN = [("<->",), ("->",), ("|",), ("&",), ("U", "W", "R", "S")]


def tokenize(s):
    s, out, i = s.strip(), [], 0
    while i < len(s):
        m = TOK.match(s, i)
        if not m:
            raise SyntaxError(f"bad token at {s[i:]!r}")
        out.append(m.group(1)); i = m.end()
        while i < len(s) and s[i].isspace():
            i += 1
    return out


def parse(s):
    toks = tokenize(s); pos = [0]
    peek = lambda: toks[pos[0]] if pos[0] < len(toks) else None
    def eat():
        pos[0] += 1; return toks[pos[0] - 1]
    def level(k):
        if k == len(BIN):
            return unary()
        left = level(k + 1)
        if peek() in BIN[k]:
            op = eat()
            return (op, left, level(k))  # right-assoc
        return left
    def unary():
        t = peek()
        if t is None:
            raise SyntaxError("unexpected end")
        if t in UN:
            eat(); return (t, unary())
        m = re.fullmatch(r"(F|G)<=(\d+)", t) or re.fullmatch(r"(X|N)\^(\d+)", t)
        if m:
            eat(); f = unary(); op, k = m.group(1), int(m.group(2))
            if op in "XN":
                for _ in range(k):
                    f = (op, f)
                return f
            return (op + "<=", k, f)
        if t == "(":
            eat(); f = level(0)
            if eat() != ")":
                raise SyntaxError("expected )")
            return f
        eat()
        if t == "true": return ("T",)
        if t == "false": return ("F0",)
        return ("atom", t)
    f = level(0)
    if pos[0] != len(toks):
        raise SyntaxError(f"trailing tokens {toks[pos[0]:]}")
    return f


def atoms_of(f):
    if f[0] == "atom": return {f[1]}
    return set().union(*[atoms_of(x) for x in f[1:] if isinstance(x, tuple)]) if len(f) > 1 else set()


def ev(f, tr):
    """Vector of truth values of f at positions 0..n-1 of trace tr (list of dicts)."""
    n, op = len(tr), f[0]
    if op == "T": return [True] * n
    if op == "F0": return [False] * n
    if op == "atom": return [st[f[1]] for st in tr]
    if op == "!": return [not v for v in ev(f[1], tr)]
    if op in ("F<=", "G<=" ):
        k, v = f[1], ev(f[2], tr)
        if op == "F<=": return [any(v[i:i + k + 1]) for i in range(n)]
        return [all(v[i:i + k + 1]) for i in range(n)]  # weak at the end
    if op in ("X", "N", "F", "G", "Y", "Z", "O", "H"):
        v = ev(f[1], tr); r = [False] * n
        if op == "X": return [v[i + 1] if i + 1 < n else False for i in range(n)]
        if op == "N": return [v[i + 1] if i + 1 < n else True for i in range(n)]
        if op == "Y": return [v[i - 1] if i > 0 else False for i in range(n)]
        if op == "Z": return [v[i - 1] if i > 0 else True for i in range(n)]
        if op in "FG":
            acc = op == "G"
            for i in range(n - 1, -1, -1):
                acc = (v[i] or acc) if op == "F" else (v[i] and acc)
                r[i] = acc
            return r
        acc = op == "H"
        for i in range(n):
            acc = (v[i] or acc) if op == "O" else (v[i] and acc)
            r[i] = acc
        return r
    a, b = ev(f[1], tr), ev(f[2], tr)
    if op == "&": return [x and y for x, y in zip(a, b)]
    if op == "|": return [x or y for x, y in zip(a, b)]
    if op == "->": return [(not x) or y for x, y in zip(a, b)]
    if op == "<->": return [x == y for x, y in zip(a, b)]
    r = [False] * n
    if op in ("U", "W", "R"):
        if op == "R":  # a R b = !(!a U !b)
            acc = True
            for i in range(n - 1, -1, -1):
                acc = b[i] and (a[i] or acc); r[i] = acc
            return r
        acc = op == "W"
        for i in range(n - 1, -1, -1):
            acc = b[i] or (a[i] and acc); r[i] = acc
        return r
    if op == "S":
        acc = False
        for i in range(n):
            acc = b[i] or (a[i] and acc); r[i] = acc
        return r
    raise ValueError(op)


def holds(f, tr):
    return ev(f, tr)[0] if tr else True

# ---------------- grammar (Section 3.3, direct implementation) ----------------

def pat_holds(p, a, u):
    kind, k = p
    L = len(a)
    if kind == "ALWAYS": return all(a)
    if kind == "NEVER": return not any(a)
    if kind == "EVENTUALLY": return any(a)
    if kind == "AT": return L >= k and all(a[i] == (i == k - 1) for i in range(L))
    if kind == "EVERY": return all(a[i] == ((i + 1) % k == 0) for i in range(L))
    if kind == "EXACTLY": return sum(a) == k
    if kind == "ATMOST": return sum(a) <= k
    if kind == "WITHIN": return all(any(a[i:i + k + 1]) for i in range(L) if u[i])
    if kind == "AFTER":
        us = [i for i in range(L) if u[i]]
        if len(us) < k: return not any(a)
        p_m = us[k - 1]
        return not any(a[:p_m]) and a[p_m]
    raise ValueError(kind)


def segment(scope, o, c, L):
    kind = scope
    if kind == "GLOBALLY": return (0, L)
    if kind == "FROM":
        i = next((j for j in range(L) if o[j]), None)
        return None if i is None else (i, L)
    if kind == "UNTIL":
        j = next((j for j in range(L) if c[j]), L)
        return (0, j)
    i = next((j for j in range(L) if o[j]), None)
    if i is None: return None
    j = next((j for j in range(i + 1, L) if c[j]), L)
    return (i, j)


_VEC = {}


def vec(f, tr):
    k = (id(f), id(tr))
    v = _VEC.get(k)
    if v is None:
        v = _VEC[k] = tuple(f(st) for st in tr)
    return v


def inst_holds(inst, tr):
    p, scope, af, uf, of, cf = inst
    a = vec(af, tr); u = vec(uf, tr) if uf else (False,) * len(tr)
    o = vec(of, tr) if of else None; c = vec(cf, tr) if cf else None
    seg = segment(scope, o, c, len(tr))
    if seg is None or seg[0] >= seg[1]: return True
    s, e = seg
    return pat_holds(p, a[s:e], u[s:e])

# ---------------- role fillers ----------------

def literal_funcs(names):
    out = []
    for n in names:
        out.append((n, lambda st, n=n: st[n]))
        out.append(("!" + n, lambda st, n=n: not st[n]))
    return out


def bool_funcs(names):
    if not names: return []
    if len(names) == 1: return literal_funcs(names)
    if len(names) == 2:
        x, y = names
        cand = [(f"{p}{x}", None) for p in ("", "!")] + [(f"{p}{y}", None) for p in ("", "!")]
        for px, py in itertools.product(("", "!"), repeat=2):
            cand += [(f"({px}{x}&{py}{y})", None), (f"({px}{x}|{py}{y})", None)]
        cand += [(f"({x}<->{y})", None), (f"!({x}<->{y})", None)]
        return [(n, lambda st, F=parse(n): holds(F, [st])) for n, _ in cand]
    lits = literal_funcs(names); out = list(lits)
    for (n1, f1), (n2, f2) in itertools.combinations(lits, 2):
        if n1.lstrip("!") == n2.lstrip("!"): continue
        out.append((f"({n1}&{n2})", lambda st, f1=f1, f2=f2: f1(st) and f2(st)))
        out.append((f"({n1}|{n2})", lambda st, f1=f1, f2=f2: f1(st) or f2(st)))
    return out


_ROLES = {}


def instances(A, U, maxp):
    key = (tuple(A), tuple(U))
    if key not in _ROLES:
        _ROLES[key] = (bool_funcs(A), bool_funcs(U), literal_funcs(U))
    afs, ufs, uls = _ROLES[key]
    pats = [("ALWAYS", 0), ("NEVER", 0), ("EVENTUALLY", 0)]
    for k in range(1, maxp + 1):
        pats += [("AT", k), ("EVERY", k), ("EXACTLY", k), ("ATMOST", k)]
    tpats = [("WITHIN", w) for w in range(0, maxp)] + [("AFTER", m) for m in range(1, maxp + 1)]
    scopes = [("GLOBALLY", None, None)]
    scopes += [("FROM", o, None) for o in uls] + [("UNTIL", None, c) for c in uls]
    scopes += [("FROMUNTIL", o, c) for o in uls for c in uls if o[0].lstrip("!") != c[0].lstrip("!")]
    for (sn, o, c) in scopes:
        for an, af in afs:
            for p in pats:
                yield (p, sn, af, None, o and o[1], c and c[1]), name(p, an, None, sn, o, c)
            for un, uf in ufs:
                for p in tpats:
                    yield (p, sn, af, uf, o and o[1], c and c[1]), name(p, an, un, sn, o, c)


def name(p, an, un, sn, o, c):
    kind, k = p
    s = {"ALWAYS": f"ALWAYS {an}", "NEVER": f"NEVER {an}", "EVENTUALLY": f"EVENTUALLY {an}",
         "AT": f"AT {k}, {an}", "EVERY": f"EVERY {k}, {an}", "EXACTLY": f"EXACTLY {k} TIMES, {an}",
         "ATMOST": f"AT MOST {k} TIMES, {an}", "WITHIN": f"{an} WITHIN {k} OF {un}",
         "AFTER": f"{an} AFTER {k} TIMES {un}"}[kind]
    sc = {"GLOBALLY": "GLOBALLY", "FROM": f"FROM {o and o[0]}", "UNTIL": f"UNTIL {c and c[0]}",
          "FROMUNTIL": f"FROM {o and o[0]} UNTIL {c and c[0]}"}[sn]
    return f"{s} {sc}"

# ---------------- traces ----------------

def traces(atoms, seed=0, budget=60000, nrand=40000, maxlen=10):
    states = [dict(zip(atoms, bits)) for bits in itertools.product([False, True], repeat=len(atoms))]
    out, L = [[]], 1
    while len(out) + len(states) ** L <= budget:
        out += [list(t) for t in itertools.product(states, repeat=L)]; L += 1
    exh = L - 1
    rng = random.Random(seed)
    for _ in range(nrand):
        n = rng.randint(exh + 1, max(maxlen, exh + 1)); p = rng.choice([0.15, 0.3, 0.5])
        out.append([{x: rng.random() < p for x in atoms} for _ in range(n)])
    rng.shuffle(out)
    return out, exh


def fmt(tr):
    return " ".join("{" + ",".join(k for k, v in st.items() if v) + "}" for st in tr) or "(empty)"

# ---------------- main check ----------------

def check(atom_sides, spec, maxp=None):
    atoms = list(atom_sides)
    A = [x for x in atoms if atom_sides[x] == "A"]; U = [x for x in atoms if atom_sides[x] == "U"]
    trs, exh = traces(atoms)
    maxp = maxp or 6
    S = [spec(t) for t in trs]
    s_true = [i for i, v in enumerate(S) if v]; s_false = [i for i, v in enumerate(S) if not v]
    print(f"atoms A={A} U={U}; {len(trs)} traces (exhaustive up to length {exh}, random up to 10); "
          f"spec true on {len(s_true)}, false on {len(s_false)}")
    if not s_false:
        print("VERDICT: TRIVIAL (spec holds on every trace)"); return "TRIVIAL"
    if not s_true:
        print("VERDICT: UNSATISFIABLE on test traces"); return "UNSAT"
    implied, count = [], 0
    for inst, nm in instances(A, U, maxp):
        count += 1
        ok = all(inst_holds(inst, trs[i]) for i in s_true)
        if ok:
            implied.append((inst, nm))
    print(f"{count} grammar instances; {len(implied)} are implied by the spec")
    # exact single match
    for inst, nm in implied:
        if all(not inst_holds(inst, trs[i]) for i in s_false):
            print(f"VERDICT: COVERED (equivalent to one instance)\n  {nm}"); return "COVERED"
    # conjunction: every S-false trace must be rejected by some implied instance
    nontrivial = [(inst, nm) for inst, nm in implied]
    used, uncovered = [], []
    rej_cache = {}
    for i in s_false:
        hit = None
        for j in ([u for u in used] + list(range(len(nontrivial)))):
            if not inst_holds(nontrivial[j][0], trs[i]):
                hit = j; break
        if hit is None:
            uncovered.append(i)
            if len(uncovered) >= 5: break
        elif hit not in used:
            used.append(hit)
    if not uncovered:
        # greedy minimise
        keep = list(used)
        for j in list(keep):
            trial = [x for x in keep if x != j]
            if all(any(not inst_holds(nontrivial[x][0], trs[i]) for x in trial) for i in s_false):
                keep = trial
        print("VERDICT: COVERED (equivalent to a conjunction of instances)")
        for j in keep: print("  " + nontrivial[j][1])
        return "COVERED"
    print("VERDICT: NOT COVERED")
    print("  Traces where the spec is false but every grammar instance it implies holds")
    print("  (no conjunction of grammar instructions can rule these out):")
    for i in uncovered[:3]: print("   ", fmt(trs[i]))
    # closest single instances by disagreement on a sample
    samp = list(range(0, len(trs), max(1, len(trs) // 1500)))
    best = []
    for inst, nm in instances(A, U, maxp):
        d = sum(inst_holds(inst, trs[i]) != S[i] for i in samp)
        best.append((d, nm, inst))
    best.sort(key=lambda x: x[0])
    print("  Closest single instances (disagreements on a sample of", len(samp), "traces) and a separating trace:")
    for d, nm, inst in best[:3]:
        sep = next(trs[i] for i in range(len(trs)) if inst_holds(inst, trs[i]) != S[i])
        print(f"    {d:5d}  {nm}\n           e.g. {fmt(sep)}  spec={spec(sep)}")
    return "NOT_COVERED"


def selftest():
    """The direct grammar implementation must agree with the LTLf formulas of Section 3.3."""
    E = lambda m: "(!a U (a & N G !a))" if m == 1 else f"(!a U (a & X {E(m-1)}))"
    B = lambda m: "G !a" if m == 0 else f"(!a W (a & N {B(m-1)}))"
    C = lambda m: "((!a & !u) W (u & a))" if m == 1 else f"((!a & !u) W (u & !a & N {C(m-1)}))"
    def AT(n):
        pre = " & ".join(["!a" if j == 0 else f"X^{j} !a" for j in range(n - 1)])
        main = f"X^{n-1} (a & N G !a)" if n > 1 else "(a & N G !a)"
        return f"({pre} & {main})" if pre else main
    def EV(k):
        Sk = " & ".join([("!a" if j == 0 else f"N^{j} !a") for j in range(k - 1)] + [f"N^{k-1} a" if k > 1 else "a"])
        Sp = " & ".join([f"N^{j} !a" for j in range(1, k)] + [f"N^{k} a"])
        return f"(({Sk}) & G(a -> ({Sp})))"
    cases = [(("ALWAYS", 0), "G a"), (("NEVER", 0), "G !a"), (("EVENTUALLY", 0), "F a")]
    for k in range(1, 5):
        cases += [(("AT", k), AT(k)), (("EVERY", k), EV(k)), (("EXACTLY", k), E(k)),
                  (("ATMOST", k), B(k)), (("AFTER", k), C(k)), (("WITHIN", k - 1), f"G(u -> F<={k-1} a)")]
    trs = [list(t) for L in range(1, 9) for t in itertools.product(
        [dict(a=x, u=y) for x in (0, 1) for y in (0, 1)], repeat=L)]
    trs = [[{k: bool(v) for k, v in st.items()} for st in t] for t in trs]
    bad = 0
    for p, f in cases:
        F = parse(f)
        for t in trs:
            if pat_holds(p, [s["a"] for s in t], [s["u"] for s in t]) != holds(F, t):
                print("MISMATCH", p, f, fmt(t)); bad += 1; break
    # scopes vs their LTLf readings for ALWAYS/NEVER
    sc = [("FROM", "a", "!o W (o & G a)", "ALWAYS"), ("UNTIL", "a", "a W c", "ALWAYS"), ("UNTIL", "!a", "!a W c", "NEVER")]
    trs2 = [[dict(a=bool(x), o=bool(y), c=bool(z)) for (x, y, z) in t] for L in range(1, 7)
            for t in itertools.product(list(itertools.product((0, 1), repeat=3)), repeat=L)]
    for scope, _, f, pk in sc:
        F = parse(f)
        inst = ((pk, 0), scope, lambda st: st["a"], None, lambda st: st["o"], lambda st: st["c"])
        for t in trs2:
            if inst_holds(inst, t) != holds(F, t):
                print("SCOPE MISMATCH", scope, f, fmt(t)); bad += 1; break
    print("selftest:", "OK" if not bad else f"{bad} failures"); return bad == 0


def equiv(s1, F1, s2, F2):
    side = lambda s, x: sorted(k for k in s if s[k] == x)
    if [len(side(s1, x)) for x in "AU"] != [len(side(s2, x)) for x in "AU"]:
        print("NOT EQUIVALENT: different numbers of A/U atoms"); return False
    trs, _ = traces(list(s1), nrand=20000)
    v1 = [holds(F1, t) for t in trs]
    A1, U1, A2, U2 = side(s1, "A"), side(s1, "U"), side(s2, "A"), side(s2, "U")
    for pa in itertools.permutations(A2):
        for pu in itertools.permutations(U2):
            m = dict(zip(A1 + U1, list(pa) + list(pu)))
            for neg in itertools.product([False, True], repeat=len(m)):
                ng = dict(zip(m, neg))
                if all(holds(F2, [{m[k]: st[k] != ng[k] for k in st} for st in t]) == v for t, v in zip(trs, v1)):
                    print("EQUIVALENT under", {k: ("!" if ng[k] else "") + m[k] for k in m}); return True
    print("NOT EQUIVALENT under any side-preserving renaming/negation"); return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--atoms", help="comma list name:A or name:U")
    ap.add_argument("--ltl")
    ap.add_argument("--maxp", type=int, default=6, help="largest pattern parameter tried")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--atoms2", help="with --ltl2: test equivalence of two specs up to side-preserving renaming and negation of atoms")
    ap.add_argument("--ltl2")
    g = ap.parse_args()
    if g.selftest:
        sys.exit(0 if selftest() else 1)
    sides = {}
    for part in g.atoms.split(","):
        n, s = part.strip().split(":"); sides[n] = s.upper()
        assert sides[n] in ("A", "U"), "side must be A (assistant reply) or U (user message)"
    F = parse(g.ltl)
    if g.ltl2:
        sides2 = {p.split(":")[0].strip(): p.split(":")[1].strip().upper() for p in g.atoms2.split(",")}
        sys.exit(0 if equiv(sides, F, sides2, parse(g.ltl2)) else 1)
    missing = atoms_of(F) - set(sides)
    assert not missing, f"undeclared atoms {missing}"
    check(sides, lambda t: holds(F, t), g.maxp)
