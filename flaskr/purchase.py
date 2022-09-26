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

bp = Blueprint("purchase", __name__, url_prefix="/compras")


@bp.route("/registrar", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        numero_comprobante = request.form["numero_comprobante"]
        fecha_compra = request.form["fecha_compra"]
        fecha_pago = request.form["fecha_pago"]
        iva_compra = request.form["iva_compra"]
        otros_impuestos = request.form["otros_impuestos"]
        no_gravado = request.form["no_gravado"]
        total = request.form["total"]
        supplier_id = request.form["supplier_id"]
        db = get_db()
        error = None

        if not numero_comprobante:
            error = "Número de comprobante es requerido."
        if not fecha_compra:
            error = "Fecha de compra es requerida."
        if not fecha_pago:
            error = "Fecha de pago es requerida."
        if not total:
            error = "El Total es requerido."

        query = """
            INSERT INTO compras 
                (numero_comprobante, fecha_compra, fecha_pago, iva_compra, otros_impuestos, no_gravado, total, proveedor_id)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)
        """
        if error is None:
            try:
                db.execute(
                    query,
                    (
                        numero_comprobante,
                        fecha_compra,
                        fecha_pago,
                        iva_compra,
                        otros_impuestos,
                        no_gravado,
                        total,
                        supplier_id,
                    ),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Numero de comprobante ya registrado"
            else:
                return redirect(url_for("purchase.index"))

        flash(error)
    suppliers = get_suppliers()
    return render_template("purchase/create.html", suppliers=suppliers)


@bp.route("/", methods=["GET"])
def index():
    db = get_db()
    query = """
        SELECT
            c.id,
            c.numero_comprobante,
            c.fecha_compra,
            c.fecha_pago,
            c.iva_compra,
            c.otros_impuestos,
            c.no_gravado,
            c.total,
            p.razon_social,
            p.cuit
        FROM
            compras AS c
        JOIN
            proveedores AS p
            ON c.proveedor_id = p.id
        ORDER BY
            fecha_compra DESC
    """
    purchases = db.execute(query).fetchall()
    return render_template("purchase/index.html", purchases=purchases)


def get_purchase(purchase_id: int):
    query = """
        SELECT
            c.id,
            c.numero_comprobante,
            c.fecha_compra,
            c.fecha_pago,
            c.iva_compra,
            c.otros_impuestos,
            c.no_gravado,
            c.total,
            p.id AS supplier_id,
            p.cuit,
            p.razon_social
        FROM
            compras AS c
        JOIN
            proveedores AS p
            ON c.proveedor_id = p.id
        WHERE
            c.id = ?
    """
    purchase = get_db().execute(query, (purchase_id,)).fetchone()
    if purchase is None:
        abort(404, f"No se encontro la compra")

    return purchase


def get_suppliers():
    suppliers = (
        get_db()
        .execute(
            """
        SELECT
            id,
            cuit,
            razon_social
        FROM
            proveedores
        """
        )
        .fetchall()
    )

    if suppliers is None:
        return []
    return suppliers


@bp.route("/<int:purchase_id>/actualizar", methods=("GET", "POST"))
def update(purchase_id: int):
    if request.method == "POST":
        numero_comprobante = request.form["numero_comprobante"]
        fecha_compra = request.form["fecha_compra"]
        fecha_pago = request.form["fecha_pago"]
        iva_compra = request.form["iva_compra"]
        otros_impuestos = request.form["otros_impuestos"]
        no_gravado = request.form["no_gravado"]
        total = request.form["total"]
        supplier_id = request.form["supplier_id"]
        db = get_db()
        error = None

        if not numero_comprobante:
            error = "Número de comprobante es requerido."
        if not fecha_compra:
            error = "Fecha de compra es requerida."
        if not fecha_pago:
            error = "Fecha de pago es requerida."
        if not total:
            error = "El Total es requerido."

        query = """
            UPDATE compras
             SET numero_comprobante=?, fecha_compra=?, fecha_pago=?, iva_compra=?, otros_impuestos=?, no_gravado=?, total=?, proveedor_id=?
            WHERE id=?
        """
        if error is None:
            try:
                db.execute(
                    query,
                    (
                        numero_comprobante,
                        fecha_compra,
                        fecha_pago,
                        iva_compra,
                        otros_impuestos,
                        no_gravado,
                        total,
                        supplier_id,
                        purchase_id,
                    ),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Numero de comprobante ya registrado"
            else:
                return redirect(url_for("purchase.index"))
    purchase = get_purchase(purchase_id)
    suppliers = get_suppliers()
    return render_template(
        "purchase/update.html", purchase=purchase, suppliers=suppliers
    )


@bp.route("/<int:purchase_id>/eliminar", methods=("POST",))
def delete(purchase_id: int):
    db = get_db()
    db.execute("DELETE FROM compras WHERE id = ?", (purchase_id,))
    db.commit()
    return redirect(url_for("purchase.index"))
