# Objetivo

Aplicar descuentos automáticos en el punto de venta según franjas horarias configurables.

## Criterios de aceptación

* Nuevo modelo de configuración para definir reglas con campos como: `name`, `hour_from`,
  `hour_to`, `discount_percentage`.

* Aplicación automática del descuento en una orden de **pos.order** cuando la venta se registre
  dentro del horario definido.

* Validación para evitar que se apliquen múltiples descuentos incompatibles sobre la misma orden.

* Vista de configuración accesible desde el menú de punto de venta.

* Prueba que valide órdenes con y sin descuento, incluyendo casos límite (ej. orden fuera del
  rango horario o reglas solapadas).

# Enfoque de la solución

La implementación se realizó del lado del **backend**, que es lo interpretado a partir del enunciado:

el ejercicio indica explícitamente *"aplicación automática del descuento en una orden de
`pos.order`"*, y el criterio de pruebas exige validar órdenes con y sin descuento, es decir,
tests unitarios de Python sobre el modelo.

El punto de venta es una aplicación de Odoo Web Library (JavaScript) que mantiene su propio modelo de la orden en
memoria y calcula los totales en el navegador. La orden solo llega al servidor cuando el cajero
valida el pago, mediante `sync_from_ui()`, que a su vez crea o actualiza los registros invocando
`_process_order()`. Aquí el código fuente donde se hace el proceso:

https://github.com/odoo/odoo/blob/b968f3e3bbfc49994b8fa2d1e42fa4ea1dafcc1b/addons/point_of_sale/models/pos_order.py#L1241

## Limitaciones conocidas

Aplicar el descuento en el backend implica que este se calcula **después** de que el cajero haya
cobrado, ya que el pago ocurre en el frontend antes de la sincronización. En consecuencia, el
importe cobrado no reflejaría el descuento y la orden quedaría descuadrada (`amount_paid`
distinto de `amount_total`).

Una implementación productiva requeriría extender también el **frontend**, para que el cajero vea
los descuentos en tiempo real y los totales a pagar coincidan con los que muestra la orden una vez
calculados impuestos y descuentos.

