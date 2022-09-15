import functools

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from flaskr.db import get_db

bp = Blueprint("supplier", __name__, url_prefix="/proveedores")


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
    suppliers = db.execute("SELECT cuit, razon_social FROM proveedores").fetchall()
    return render_template("supplier/index.html", suppliers=suppliers)


def get_supplier(razon_social: str):
    supplier = (
        get_db()
        .execute(
            """
        SELECT cuit, razon_social
        FROM proveedores
        WHERE razon_social = ?""",
            (razon_social,),
        )
        .fetchone()
    )

    if supplier is None:
        abort(404, f"No existe el proveedor {razon_social}.")

    return supplier


@bp.route("/<string:razon_social>/actualizar", methods=("GET", "POST"))
def update(razon_social: str):
    supplier = get_supplier(razon_social)

    if request.method == "POST":
        cuit = request.form["cuit"]
        new_razon_social = request.form["razon_social"]
        error = None

        if not razon_social:
            error = "Razon social es requerido."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE proveedores SET cuit = ?, razon_social = ? WHERE razon_social = ?",
                (cuit, new_razon_social, razon_social),
            )
            db.commit()
            return redirect(url_for("supplier.index"))

    return render_template("supplier/update.html", supplier=supplier)


@bp.route("/<string:razon_social>/eliminar", methods=("POST",))
def delete(razon_social: str):
    get_supplier(razon_social)
    db = get_db()
    db.execute("DELETE FROM proveedores WHERE razon_social = ?", (razon_social,))
    db.commit()
    return redirect(url_for("supplier.index"))
