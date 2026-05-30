from itertools import combinations

from simpleai.search import CspProblem, backtrack


def _kind(name):
    return name.split("_", 1)[0]


def _make_names(amounts):
    names = []
    for kind, amount in amounts.items():
        names.extend(f"{kind}_{index}" for index in range(amount))
    return names


def _is_border(cell, size):
    row, col = cell
    rows, cols = size
    return row == 0 or col == 0 or row == rows - 1 or col == cols - 1


def _neighbors(cell, size):
    row, col = cell
    rows, cols = size
    candidates = (
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    )
    return [
        (r, c)
        for r, c in candidates
        if 0 <= r < rows and 0 <= c < cols
    ]


def _touching(cell_a, cell_b):
    return abs(cell_a[0] - cell_b[0]) + abs(cell_a[1] - cell_b[1]) == 1


def _different_cells(variables, values):
    return values[0] != values[1]


def _not_touching(variables, values):
    return not _touching(values[0], values[1])


def _lab_has_deposit(variables, values):
    lab_cell = values[0]
    deposit_cells = values[1:]
    return any(_touching(lab_cell, deposit_cell) for deposit_cell in deposit_cells)


def _hab_has_exit(size, craters):
    blocked_by_craters = set(craters)

    def check(variables, values):
        hab_cell = values[0]
        occupied = set(values)
        return any(
            cell not in blocked_by_craters and cell not in occupied
            for cell in _neighbors(hab_cell, size)
        )

    return check


def _build_domains(names, size, craters):
    rows, cols = size
    available = [
        (row, col)
        for row in range(rows)
        for col in range(cols)
        if (row, col) not in set(craters)
    ]

    domains = {}
    for name in names:
        kind = _kind(name)
        if kind == "air":
            domains[name] = [cell for cell in available if _is_border(cell, size)]
        elif kind == "hab":
            domains[name] = [cell for cell in available if not _is_border(cell, size)]
        else:
            domains[name] = available

    return domains


def _build_constraints(names, size, craters):
    constraints = []

    for first, second in combinations(names, 2):
        constraints.append(((first, second), _different_cells))

        pair = {_kind(first), _kind(second)}
        if pair == {"gen", "hab"} or (_kind(first) == "gen" and _kind(second) == "gen"):
            constraints.append(((first, second), _not_touching))

    deposits = [name for name in names if _kind(name) == "dep"]
    for lab in [name for name in names if _kind(name) == "lab"]:
        constraints.append(((lab, *deposits), _lab_has_deposit))

    for hab in [name for name in names if _kind(name) == "hab"]:
        others = [name for name in names if name != hab]
        constraints.append(((hab, *others), _hab_has_exit(size, craters)))

    return constraints



def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    amounts = {
        "hab": habs,
        "gen": generators,
        "lab": labs,
        "dep": deposits,
        "air": airlocks,
    }
    names = _make_names(amounts)
    domains = _build_domains(names, camp_size, craters)
    constraints = _build_constraints(names, camp_size, craters)

    solution = backtrack(CspProblem(names, domains, constraints))
    if solution is None:
        return None

    return [
        (_kind(name), row, col)
        for name, (row, col) in solution.items()
    ]
