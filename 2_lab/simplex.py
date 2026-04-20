def simplex(c, A, b):
    m = len(b)
    n = len(c)

    for i, bi in enumerate(b):
        if bi < 0:
            return {"status": "infeasible", "x": None, "obj": None}

    total_vars = n + m
    tableau = []
    for i in range(m):
        row = list(A[i]) + [0.0] * m + [float(b[i])]
        row[n + i] = 1.0
        tableau.append(row)
    obj_row = [-float(ci) for ci in c] + [0.0] * m + [0.0]
    tableau.append(obj_row)

    basis = list(range(n, n + m))

    MAX_ITER = 200
    for iteration in range(MAX_ITER):
        obj = tableau[-1]

        pivot_col = -1
        min_val = -1e-9
        for j in range(total_vars):
            if obj[j] < min_val:
                min_val = obj[j]
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

    else:
        return {"status": "infeasible", "x": None, "obj": None}

    x = [0.0] * total_vars
    for i, b_var in enumerate(basis):
        x[b_var] = tableau[i][-1]

    obj_val = tableau[-1][-1]

    return {
        "status": "optimal",
        "x": x[:n],
        "obj": obj_val,
    }