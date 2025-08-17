from __future__ import annotations
from flask import Flask, render_template, request, jsonify
from typing import List, Optional

app = Flask(__name__)


def multiply(A: List[List[int]], B: List[List[int]], modulus: Optional[int] = None) -> List[List[int]]:
    if not A or not B or not A[0] or not B[0]:
        raise ValueError("Matrices must be non-empty.")

    m, n = len(A), len(A[0])
    n_b, p = len(B), len(B[0])

    if n != n_b:
        raise ValueError(f"Incompatible dimensions: A is {m}x{n}, B is {n_b}x{p}. cols(A) must equal rows(B).")

    # Validate entries are integers
    for r, row in enumerate(A):
        if len(row) != n:
            raise ValueError("Matrix A has ragged rows.")
        for c, val in enumerate(row):
            if not isinstance(val, int):
                raise ValueError(f"Matrix A contains non-integer at ({r},{c}).")

    for r, row in enumerate(B):
        if len(row) != p:
            raise ValueError("Matrix B has ragged rows.")
        for c, val in enumerate(row):
            if not isinstance(val, int):
                raise ValueError(f"Matrix B contains non-integer at ({r},{c}).")

    result = [[0 for _ in range(p)] for _ in range(m)]

    # Compute (A x B) (with optional modulus)
    for i in range(m):
        for k in range(n):
            a_ik = A[i][k]
            if modulus:
                a_ik %= modulus
            if a_ik:
                for j in range(p):
                    b_kj = B[k][j]
                    if modulus:
                        b_kj %= modulus
                    val = result[i][j] + a_ik * b_kj
                    result[i][j] = val % modulus if modulus else val

    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/multiply", methods=["POST"])
def multiply_route():
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify({"ok": False, "error": "Invalid JSON payload."}), 400

        A = payload.get("A")
        B = payload.get("B")
        modulus = payload.get("modulus")

        if modulus is not None and not isinstance(modulus, int):
            return jsonify({"ok": False, "error": "Modulus must be an integer."}), 400
        if modulus is not None and modulus <= 0:
            return jsonify({"ok": False, "error": "Modulus must be a positive integer if specified."}), 400

        # Ensure matrices are lists of lists of ints
        def normalize_matrix(M, name):
            if not isinstance(M, list) or not M:
                raise ValueError(f"{name} must be a non-empty 2D array.")
            norm = []
            for r, row in enumerate(M):
                if not isinstance(row, list) or not row:
                    raise ValueError(f"{name} row {r} must be a non-empty list.")
                norm_row = []
                for c, val in enumerate(row):
                    if isinstance(val, bool):
                        val = int(val)
                    if not isinstance(val, int):
                        raise ValueError(f"{name} contains non-integer at ({r},{c}).")
                    norm_row.append(val)
                norm.append(norm_row)
            return norm

        A = normalize_matrix(A, "A")
        B = normalize_matrix(B, "B")

        result = multiply(A, B, modulus)
        return jsonify({"ok": True, "result": result})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"Unexpected error: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)