def m_method(c_obj, A_mat, b_rhs, types=None, opt="max"):
    rows = len(b_rhs)
    cols = len(c_obj)

    if types is None:
        types = ['<='] * rows

    BIG_M = 10**6

    total_cols = cols
    for t in types:
        if t == '<=':
            total_cols += 1
        elif t == '>=':
            total_cols += 2
        elif t == '=':
            total_cols += 1

    table = []
    basis = []
    var_names = [f"x{j+1}" for j in range(cols)]
    artificial = []
    cur_idx = cols
    art_cnt = 1

    for i in range(rows):
        row = [0.0] * total_cols
        for j in range(cols):
            row[j] = float(A_mat[i][j])

        t = types[i]
        rhs = float(b_rhs[i])

        if t == '<=':
            row[cur_idx] = 1.0
            var_names.append(f"s{cur_idx - cols + 1}")
            basis.append(cur_idx)
            cur_idx += 1

        elif t == '>=':
            row[cur_idx] = -1.0
            cur_idx += 1
            row[cur_idx] = 1.0
            var_names.append(f"a{art_cnt}")
            art_cnt += 1
            artificial.append(cur_idx - 1)
            basis.append(cur_idx - 1)
            cur_idx += 1

        elif t == '=':
            row[cur_idx] = 1.0
            var_names.append(f"a{art_cnt}")
            art_cnt += 1
            artificial.append(cur_idx)
            basis.append(cur_idx)
            cur_idx += 1

        row.append(rhs)
        table.append(row)

    obj_row = [0.0] * total_cols
    for j in range(cols):
        obj_row[j] = -c_obj[j] if opt == "max" else c_obj[j]

    m_coef = -BIG_M if opt == "max" else BIG_M
    for a_idx in artificial:
        obj_row[a_idx] = m_coef
    obj_row.append(0.0)
    table.append(obj_row)

    for a_idx in artificial:
        if a_idx in basis:
            row_idx = basis.index(a_idx)
            factor = table[-1][a_idx]
            if abs(factor) > 1e-9:
                for j in range(total_cols + 1):
                    table[-1][j] -= factor * table[row_idx][j]

    MAX_ITER = 200
    for _ in range(MAX_ITER):
        obj = table[-1]

        pivot_col = -1
        if opt == "max":
            min_val = -1e-9
            for j in range(total_cols):
                if obj[j] < min_val:
                    min_val = obj[j]
                    pivot_col = j
        else:
            max_val = 1e-9
            for j in range(total_cols):
                if obj[j] > max_val:
                    max_val = obj[j]
                    pivot_col = j

        if pivot_col == -1:
            break

        ratios = []
        for i in range(rows):
            if table[i][pivot_col] > 1e-9:
                ratios.append((table[i][-1] / table[i][pivot_col], i))

        if not ratios:
            return {"status": "unbounded", "solution": None, "value": None}

        _, pivot_row = min(ratios)

        pivot_val = table[pivot_row][pivot_col]
        table[pivot_row] = [x / pivot_val for x in table[pivot_row]]

        for i in range(rows + 1):
            if i != pivot_row:
                factor = table[i][pivot_col]
                table[i] = [
                    table[i][j] - factor * table[pivot_row][j]
                    for j in range(total_cols + 1)
                ]

        basis[pivot_row] = pivot_col

    for i, bvar in enumerate(basis):
        if bvar in artificial and abs(table[i][-1]) > 1e-6:
            return {"status": "infeasible", "solution": None, "value": None}

    x_opt = [0.0] * cols
    for i, bvar in enumerate(basis):
        if bvar < cols:
            x_opt[bvar] = table[i][-1]

    z_val = table[-1][-1]
    if opt == "min":
        z_val = -z_val

    return {"status": "optimal", "solution": x_opt, "value": z_val}