import re
from .models import FixedConnector, AdapterConnector, RelayPinMap, AdapterPinMap, GlobalConfig

COMPATIBLE_CONNECTOR_TYPES = {
    # Si el conector base es de tipo "DB", es compatible directamente con:
    # - "DB" (sin necesidad de adaptador de cambio de tipo)
    # - "DD" (requiere adaptador DB → DD)
    "DB": [("DB", False), ("DD", True)],
    
    # Si el conector base es "DD", es compatible directamente con:
    # - "DD" (sin adaptador)
    # - "DB" (requiere adaptador DD → DB)
    "DD": [("DD", False), ("DB", True)],
}

def find_compatible_connectors(connector_type_str, direction):
    """
    Busca conectores compatibles para conectar el DUT.
    - connector_type_str: Ej "DB15F".
    - direction: "input" o "output"; filtra por label que contenga "-IN-" o "-OUT-".

    Retorna tres listas ordenadas de tuplas:
    - usable: conectores utilizables (categoria, instancia, tipo_base, flags, adapter_name)
    - disabled_adapters: conectores de adaptadores deshabilitados
    - disabled_fixed: conectores fijos cuando están deshabilitados por configuración
    """
    match = re.match(r'^([A-Za-z]+)(\d+)([MF])$', connector_type_str)
    if not match:
        print("[FCC-DEBUG] Formato inválido del conector:", connector_type_str)
        return [], [], []

    tipo, cantidad, sexo = match.groups()
    sexo_opuesto = 'M' if sexo == 'F' else 'F'
    compatibles = COMPATIBLE_CONNECTOR_TYPES.get(tipo, [(tipo, False)])
    sub = 'IN' if direction == 'input' else 'OUT'

    allow_fixed = GlobalConfig.objects.filter(
        key="fixedconnectors_availability", value="1"
    ).exists()

    usable = []
    disabled_adapters = []
    disabled_fixed = []

    for tipo_compatible, requiere_ext in compatibles:
        base_opuesto = f"{tipo_compatible}{cantidad}{sexo_opuesto}"
        base_same = f"{tipo_compatible}{cantidad}{sexo}"

        combinaciones = [
            (base_opuesto, True, False),  # sexo opuesto
            (base_same, False, True)      # mismo sexo => cambiador
        ]

        for connector_type_to_find, is_opuesto, is_cambiador in combinaciones:
            # ---- FIXED CONNECTORS ----
            fixed_qs = FixedConnector.objects.filter(
                connector_type=connector_type_to_find,
                label__icontains=sub
            )
            print(f"[FCC-DEBUG] FIXED buscando {connector_type_to_find} con label *{sub}*")
            print("[FCC-DEBUG] Encontrados:", fixed_qs.count())

            for inst in fixed_qs:
                flags = {
                    'sexo_opuesto': is_opuesto,
                    'cambiador_sexo': is_cambiador,
                    'extender': tipo_compatible != tipo
                }
                if allow_fixed:
                    print(f"[FCC-DEBUG] + FIXED -> {inst.label} ({inst.connector_type}), Flags: {flags}")
                    usable.append(('fixed', inst, tipo_compatible, flags, None))
                else:
                    print(f"[FCC-DEBUG] FIXED encontrado pero DESHABILITADO: {inst.label} ({inst.connector_type})")
                    disabled_fixed.append(('fixed', inst, tipo_compatible, flags, None))

            # ---- ADAPTER CONNECTORS ----
            adapter_all_qs = AdapterConnector.objects.filter(
                connector_type__startswith=f"{tipo_compatible}{cantidad}",
                connector_type__endswith=connector_type_to_find[-1],
                connector_side='test-side',
                label__icontains=sub
            )
            print(f"[FCC-DEBUG] ADAPTER buscando {connector_type_to_find} con label *{sub}*")
            print("[FCC-DEBUG] Encontrados:", adapter_all_qs.count())

            for inst in adapter_all_qs:
                adapter_name = inst.adapter.name
                flags = {
                    'sexo_opuesto': is_opuesto,
                    'cambiador_sexo': is_cambiador,
                    'extender': tipo_compatible != tipo
                }
                if inst.adapter.availability:
                    print(f"[FCC-DEBUG] + ADAPTER -> {inst.label} ({inst.connector_type}) en '{adapter_name}', Flags: {flags}")
                    usable.append(('adapter', inst, tipo_compatible, flags, adapter_name))
                else:
                    print(f"[FCC-DEBUG] ADAPTER encontrado pero DESHABILITADO: {inst.label} ({inst.connector_type}) en adaptador '{adapter_name}'")
                    disabled_adapters.append(('adapter', inst, tipo_compatible, flags, adapter_name))

    return usable, disabled_adapters, disabled_fixed


""" 
python manage.py shell
from home.utils import find_compatible_connectors
find_compatible_connectors('DB50F','output') 
"""



def get_mapping_or_error(connector, pin):
    if connector is None or pin is None:
        return None

    if isinstance(connector, FixedConnector):
        mapping = RelayPinMap.objects.filter(
            test_connector=connector,
            to_test_pin=pin
        ).first()
        return (mapping.relay_card_id, mapping.pxi_channel) if mapping else None

    if isinstance(connector, AdapterConnector):
        mapping = AdapterPinMap.objects.filter(
            test_connector=connector,
            to_test_pin=pin
        ).select_related('relay_pin_map').first()
        if mapping and mapping.relay_pin_map:
            return (mapping.relay_pin_map.relay_card_id, mapping.relay_pin_map.pxi_channel)
        return None

    return None


def test_find_compatible_connectors(sessionConnector, direction):
    from home.models import FixedConnector, AdapterConnector
    from home.utils import find_compatible_connectors

    #sessionConnector = "DB9M"
    print(f"Probando find_compatible_connectors({sessionConnector}, {direction})")
    resultados = find_compatible_connectors(sessionConnector, direction)
    for i, (categoria, inst, tipo_base, flags) in enumerate(resultados, start=1):
        resumen = f"[{i}] {categoria.upper()} | {inst.label} ({inst.connector_type})"
        if categoria == "adapter":
            resumen += f" - Adaptador: "'{inst.adapter.name}'""

        anotaciones = []
        if flags['cambiador_sexo']:
            anotaciones.append("utilizando un cambiador de sexo")
        if flags['extender']:
            anotaciones.append("utilizando un extender DB a DD")

        msg = ""
        if categoria == "fixed":
            msg = f"Conecte {sessionConnector} en [{inst.label}]"
        else:
            msg = f"Utilice el adaptador \"{inst.adapter.name}\". Conecte {sessionConnector} en [{inst.label}]"

        if anotaciones:
            msg += " " + " y ".join(anotaciones)

        print(resumen)
        print("→", msg)
        print("-" * 70)

""" 
python manage.py shell
from home.utils import test_find_compatible_connectors
test_find_compatible_connectors('DB50F','output') 
"""
