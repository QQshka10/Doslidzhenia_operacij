from flask import Flask, render_template, request, jsonify
from bigm import big_m

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/solve", methods=["POST"])
def solve():
    data = request.json
    try:
        n_vars = int(data["n_vars"])
        c = [float(v) for v in data["c"]]
        A = [[float(v) for v in row] for row in data["A"]]
        b = [float(v) for v in data["b"]]
        constraint_types = data["constraint_types"]
        objective = data.get("objective", "max")

        if len(c) != n_vars:
            return jsonify({"error": "Кількість коефіцієнтів цільової функції не відповідає кількості змінних"}), 400
        if len(A) != len(b) or len(A) != len(constraint_types):
            return jsonify({"error": "Розміри матриці обмежень не співпадають"}), 400

        result = big_m(c, A, b, constraint_types, objective)

        return jsonify({
            "status": result["status"],
            "x": result["x"],
            "obj": result["obj"],
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5051)