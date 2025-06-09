import re
from .models import FixedConnector, AdapterConnector, RelayPinMap, AdapterPinMap

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

def find_opposite_sex_connectors(connector_type_str):
    """
    Busca conectores del sexo opuesto, compatibles por tipo y cantidad de pines.
    
    Retorna una lista de tuplas:
    (tipo: 'fixed'/'adapter', instancia, tipo_compatible_base, requiere_adaptador_extra)
    """
    match = re.match(r'^([A-Za-z]+)(\d+)([MF])$', connector_type_str)
    if not match:
        return []

    tipo, cantidad, sexo = match.groups()
    sexo_opuesto = 'M' if sexo == 'F' else 'F'

    compatibles = COMPATIBLE_CONNECTOR_TYPES.get(tipo, [(tipo, False)])

    resultados = []

    for tipo_compatible, requiere_adaptador in compatibles:
        connector_type_base = f"{tipo_compatible}{cantidad}{sexo_opuesto}"

        # FixedConnector
        fixed_matches = FixedConnector.objects.filter(connector_type=connector_type_base)
        resultados.extend([
            ('fixed', fc, tipo_compatible, requiere_adaptador)
            for fc in fixed_matches
        ])

        # AdapterConnector (solo del lado test-side)
        adapter_matches = AdapterConnector.objects.filter(
            connector_type__startswith=f"{tipo_compatible}{cantidad}",
            connector_type__endswith=sexo_opuesto,
            connector_side='test-side'
        )
        resultados.extend([
            ('adapter', ac, tipo_compatible, requiere_adaptador)
            for ac in adapter_matches
        ])

    return resultados


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

