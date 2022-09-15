DROP TABLE IF EXISTS vencimientos;
DROP TABLE IF EXISTS detalles;
DROP TABLE IF EXISTS compras;
DROP TABLE IF EXISTS proveedores;



create table if not exists proveedores(
    id integer primary key autoincrement,
    cuit integer null,
    razon_social text not null unique
);

create table if not exists compras(
    id integer primary key autoincrement,
    numero_comprobante integer not null,
    fecha_compra date not null,
    fecha_pago date not null,
    iva_compra integer null,
    otros_impuestos integer null,
    no_gravado integer null,
    total float not null,
    proveedor_id integer not null,
    foreign key(proveedor_id) references proveedores(id)
);

create table if not exists detalles(
    id integer primary key autoincrement,
    producto text not null,
    precio_unitario float not null,
    cantidad integer not null,
    subtotal float not null,
    compra_id integer not null,
    foreign key(compra_id) references compras(id)
);

create table if not exists vencimientos(
    id integer primary key autoincrement,
    fecha_vencimiento date not null,
    saldo float not null,
    pagado boolean not null default 0,
    compra_id integer not null,
    foreign key(compra_id) references compras(id)
);
