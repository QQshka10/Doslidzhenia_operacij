from flask import Flask, render_template, request, jsonify
from simplex import simplex

app = Flask(__name__)

LAB1_EXAMPLE = {
    "objective": "max",
    "c": [5, 4],
    "constraints": [
        {"coeffs": [6, 4], "rhs": 24},
        {"coeffs": [1, 2], "rhs": 6},
        {"coeffs": [-1, 1], "rhs": 1},
        {"coeffs": [0, 1], "rhs": 2},
    ],
    "description": "Задача з лаб. роботи №1 (варіант 1): Z = 5x₁ + 4x₂ → max"
}

@app.route("/")
def index():
    return render_template("index.html", example=LAB1_EXAMPLE)

@app.route("/solve", methods=["POST"])
def solve():
    data = request.json
    try:
        n_vars = int(data["n_vars"])
        c = [float(v) for v in data["c"]]
        A = [[float(v) for v in row] for row in data["A"]]
        b = [float(v) for v in data["b"]]
        objective = data.get("objective", "max")

        if len(c) != n_vars:
            return jsonify({"error": "Кількість коефіцієнтів цільової функції не відповідає кількості змінних"}), 400

        if objective == "min":
            c_used = [-ci for ci in c]
        else:
            c_used = c

        result = simplex(c_used, A, b)

        if objective == "min" and result["obj"] is not None:
            result["obj"] = -result["obj"]

        return jsonify({
            "status": result["status"],
            "x": result["x"],
            "obj": result["obj"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5050)