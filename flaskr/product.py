from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flaskr.db import get_db

bp = Blueprint("product", __name__, url_prefix="/compras/productos")


@bp.route("/<int:purchase_id>/registrar", methods=["GET", "POST"])
def register(purchase_id: int):
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
    purchase = get_purchase(purchase_id)
    return render_template("product/create.html", purchase=purchase)


@bp.route("/<int:purchase_id>", methods=["GET"])
def index(purchase_id: int):
    db = get_db()
    query = """
        SELECT
            d.id,
            d.producto,
            d.iva_compra,
            d.precio_unitario,
            d.cantidad,
            d.subtotal,
            d.compra_id,
            c.numero_comprobante,
            c.fecha_compra,
            c.fecha_pago,
            c.otros_impuestos,
            c.no_gravado,
            c.total,
            p.razon_social,
            p.cuit
        FROM
            detalles AS d
        JOIN
            compras AS c
            ON d.compra_id = c.id
        JOIN
            proveedores AS p
            ON c.proveedor_id = p.id
        WHERE
            d.compra_id = ?
        ORDER BY
            d.producto ASC
    """
    products = db.execute(query, (purchase_id,)).fetchall()
    return render_template("product/index.html", products=products, purchase_id=purchase_id)


def get_product(product_id: int):
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
    purchase = get_db().execute(query, (product_id,)).fetchone()
    if purchase is None:
        abort(404, f"No se encontro el producto")

    return purchase


def get_purchase(purchase_id: int):
    query = """
        SELECT
            c.id,
            c.numero_comprobante,
            c.fecha_compra,
            c.fecha_pago,
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
        return {}
    return purchase


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
