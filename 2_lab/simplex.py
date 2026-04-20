def simplex(c, A, b, constraints_types=None, objective="max"):
    m = len(b)
    n = len(c)

    if constraints_types is None:
        constraints_types = ['≤'] * m

    M = 1000000

    total_vars = n
    for constr_type in constraints_types:
        if constr_type == '≤':
            total_vars += 1
        elif constr_type == '≥':
            total_vars += 2
        elif constr_type == '=':
            total_vars += 1

    tableau = []
    basis = []
    var_names = [f"x{j + 1}" for j in range(n)]
    artificial_vars = []
    current_idx = n
    art_counter = 1

    for i in range(m):
        row = [0.0] * total_vars
        for j in range(n):
            row[j] = float(A[i][j])

        constr_type = constraints_types[i]
        rhs = float(b[i])

        if constr_type == '≤':
            row[current_idx] = 1.0
            var_names.append(f"s{current_idx - n + 1}")
            basis.append(current_idx)
            current_idx += 1

        elif constr_type == '≥':
            row[current_idx] = -1.0
            current_idx += 1
            row[current_idx] = 1.0
            var_names.append(f"a{art_counter}")
            art_counter += 1
            artificial_vars.append(current_idx - 1)
            basis.append(current_idx - 1)
            current_idx += 1

        elif constr_type == '=':
            row[current_idx] = 1.0
            var_names.append(f"a{art_counter}")
            art_counter += 1
            artificial_vars.append(current_idx)
            basis.append(current_idx)
            current_idx += 1

        row.append(rhs)
        tableau.append(row)

    obj_row = [0.0] * total_vars
    for j in range(n):
        obj_row[j] = -c[j] if objective == "max" else c[j]

    M_coef = -M if objective == "max" else M
    for art_idx in artificial_vars:
        obj_row[art_idx] = M_coef
    obj_row.append(0.0)
    tableau.append(obj_row)

    for i, art_idx in enumerate(artificial_vars):
        if art_idx in basis:
            row_idx = basis.index(art_idx)
            factor = tableau[-1][art_idx]
            if abs(factor) > 1e-9:
                for j in range(total_vars + 1):
                    tableau[-1][j] -= factor * tableau[row_idx][j]

    MAX_ITER = 200
    for _ in range(MAX_ITER):
        obj = tableau[-1]

        pivot_col = -1
        if objective == "max":
            min_val = -1e-9
            for j in range(total_vars):
                if obj[j] < min_val:
                    min_val = obj[j]
                    pivot_col = j
        else:
            max_val = 1e-9
            for j in range(total_vars):
                if obj[j] > max_val:
                    max_val = obj[j]
                    pivot_col = j

        if pivot_col == -1:
            break

        ratios = []
        for i in range(m):
            if tableau[i][pivot_col] > 1e-9:
                ratios.append((tableau[i][-1] / tableau[i][pivot_col], i))

        if not ratios:
            return {"status": "unbounded", "x": None, "obj": None}

        _, pivot_row = min(ratios)

        pivot_val = tableau[pivot_row][pivot_col]
        tableau[pivot_row] = [x / pivot_val for x in tableau[pivot_row]]

        for i in range(m + 1):
            if i != pivot_row:
                factor = tableau[i][pivot_col]
                tableau[i] = [
                    tableau[i][j] - factor * tableau[pivot_row][j]
                    for j in range(total_vars + 1)
                ]

        basis[pivot_row] = pivot_col

    for i, b_var in enumerate(basis):
        if b_var in artificial_vars and abs(tableau[i][-1]) > 1e-6:
            return {"status": "infeasible", "x": None, "obj": None}

    x = [0.0] * n
    for i, b_var in enumerate(basis):
        if b_var < n:
            x[b_var] = tableau[i][-1]

    obj_val = tableau[-1][-1]
    if objective == "min":
        obj_val = -obj_val

    return {"status": "optimal", "x": x, "obj": obj_val}