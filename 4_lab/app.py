from flask import Flask, render_template, request, jsonify
from m_method import m_method

app = Flask(__name__)

TEST_EXAMPLE = {
    "opt_type": "max",
    "coeffs": [5, 4],
    "constraints": [
        {"coeffs": [6, 4], "rhs": 24},
        {"coeffs": [1, 2], "rhs": 6},
        {"coeffs": [-1, 1], "rhs": 1},
        {"coeffs": [0, 1], "rhs": 2},
    ],
    "info": "Тестова задача: Z = 5x₁ + 4x₂ → max (перевірка М-методу)"
}

@app.route("/")
def home():
    return render_template("index.html", example=TEST_EXAMPLE)

@app.route("/compute", methods=["POST"])
def compute():
    data = request.json
    try:
        n = int(data["num_vars"])
        obj_coeffs = [float(v) for v in data["obj_coeffs"]]
        mat = [[float(v) for v in row] for row in data["matrix"]]
        rhs = [float(v) for v in data["rhs"]]
        opt_dir = data.get("opt_dir", "max")
        types_list = data.get("types_list", ['<='] * len(rhs))

        if len(obj_coeffs) != n:
            return jsonify({"error": "Кількість коефіцієнтів цільової функції не збігається з кількістю змінних"}), 400

        result = m_method(obj_coeffs, mat, rhs, types_list, opt_dir)

        return jsonify({
            "status": result["status"],
            "solution": result["solution"],
            "value": result["value"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5051)