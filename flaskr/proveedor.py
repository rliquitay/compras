import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from flaskr.db import get_db

bp = Blueprint("proveedor", __name__, url_prefix="/proveedores")


@bp.route("/registrar", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        cuit = request.form["cuit"]
        razon_social = request.form["razon_social"]
        db = get_db()
        error = None

        if not razon_social:
            error = "Razon social es requerido."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO proveedores (cuit, razon_social) VALUES (?, ?)",
                    (cuit, razon_social),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Razon social {razon_social} ya esta registrado."
            else:
                return redirect(url_for("proveedor.index"))

        flash(error)

    return render_template("proveedor/create.html")


@bp.route("/", methods=["GET"])
def index():
    db = get_db()
    proveedores = db.execute("SELECT cuit, razon_social FROM proveedores").fetchall()
    return render_template("proveedor/index.html", proveedores=proveedores)
