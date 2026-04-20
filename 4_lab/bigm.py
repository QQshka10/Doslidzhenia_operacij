BIG_M = 1e6

def big_m(c, A, b, constraint_types, objective="max"):
    m = len(b)
    n = len(c)

    if objective == "min":
        c_work = [-float(v) for v in c]
    else:
        c_work = [float(v) for v in c]

    A_work = [list(map(float, row)) for row in A]
    b_work = list(map(float, b))
    ct_work = list(constraint_types)

    for i in range(m):
        if b_work[i] < 0:
            A_work[i] = [-v for v in A_work[i]]
            b_work[i] = -b_work[i]
            if ct_work[i] == "<=":
                ct_work[i] = ">="
            elif ct_work[i] == ">=":
                ct_work[i] = "<="

    slack_cols = []
    artificial_cols = []

    col_count = n
    for i in range(m):
        if ct_work[i] == "<=":
            slack_cols.append(col_count)
            col_count += 1
            artificial_cols.append(-1)
        elif ct_work[i] == ">=":
            slack_cols.append(col_count)
            col_count += 1
            artificial_cols.append(col_count)
            col_count += 1
        else:
            slack_cols.append(-1)
            artificial_cols.append(col_count)
            col_count += 1

    total_cols = col_count

    tableau = []
    for i in range(m):
        row = [0.0] * (total_cols + 1)
        for j in range(n):
            row[j] = A_work[i][j]
        if slack_cols[i] >= 0:
            row[slack_cols[i]] = 1.0 if ct_work[i] == "<=" else -1.0
        if artificial_cols[i] >= 0:
            row[artificial_cols[i]] = 1.0
        row[-1] = b_work[i]
        tableau.append(row)

    obj_row = [0.0] * (total_cols + 1)
    for j in range(n):
        obj_row[j] = -c_work[j]
    for i in range(m):
        if artificial_cols[i] >= 0:
            obj_row[artificial_cols[i]] = BIG_M
    tableau.append(obj_row)

    basis = []
    for i in range(m):
        if artificial_cols[i] >= 0:
            basis.append(artificial_cols[i])
        else:
            basis.append(slack_cols[i])

    for i in range(m):
        if artificial_cols[i] >= 0:
            factor = tableau[-1][artificial_cols[i]]
            if abs(factor) > 1e-10:
                for j in range(total_cols + 1):
                    tableau[-1][j] -= factor * tableau[i][j]

    MAX_ITER = 300
    for iteration in range(MAX_ITER):
        obj = tableau[-1]

        pivot_col = -1
        min_val = -1e-9
        for j in range(total_cols):
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

        _, pivot_row = min(ratios, key=lambda r: r[0])

        pv = tableau[pivot_row][pivot_col]
        tableau[pivot_row] = [v / pv for v in tableau[pivot_row]]

        for i in range(m + 1):
            if i != pivot_row:
                factor = tableau[i][pivot_col]
                tableau[i] = [
                    tableau[i][j] - factor * tableau[pivot_row][j]
                    for j in range(total_cols + 1)
                ]

        basis[pivot_row] = pivot_col

    else:
        return {"status": "infeasible", "x": None, "obj": None}

    for i, b_var in enumerate(basis):
        if b_var in [artificial_cols[k] for k in range(m) if artificial_cols[k] >= 0]:
            if abs(tableau[i][-1]) > 1e-6:
                return {"status": "infeasible", "x": None, "obj": None}

    x_full = [0.0] * total_cols
    for i, bv in enumerate(basis):
        x_full[bv] = tableau[i][-1]

    obj_val = tableau[-1][-1]
    if objective == "min":
        obj_val = -obj_val

    return {
        "status": "optimal",
        "x": x_full[:n],
        "obj": obj_val,
    }