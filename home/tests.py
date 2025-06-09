from django.test import TestCase
from home.models import *

""" 
class AdapterModelTests(TestCase):

    def setUp(self):
        self.pxi_card = RelayCard.objects.create(name="PXI-1", bus=1, device=1)

        # Conectores físicos
        self.test_connector = PhysicalConnector.objects.create(
            connector_type="DB50F", label="Conector A"
        )
        self.pxi_connector_1 = PhysicalConnector.objects.create(
            connector_type="DB25M", label="PXI Entrada 1"
        )
        self.pxi_connector_2 = PhysicalConnector.objects.create(
            connector_type="DB25M", label="PXI Entrada 2"
        )

        # Adaptador
        self.adapter = Adapter.objects.create(name="Adaptador A")

    def test_create_adapter_connection_and_pin_maps(self):
        # Una conexión: A -> PXI Entrada 1
        connection1 = AdapterConnection.objects.create(
            adapter=self.adapter,
            test_connector=self.test_connector,
            pxi_connector=self.pxi_connector_1
        )

        # Pin maps
        AdapterPinMap.objects.create(
            adapter_connection=connection1,
            test_pin=1,
            relay_card=self.pxi_card,
            pxi_channel=5
        )
        AdapterPinMap.objects.create(
            adapter_connection=connection1,
            test_pin=2,
            relay_card=self.pxi_card,
            pxi_channel=6
        )

        self.assertEqual(connection1.pin_maps.count(), 2)

    def test_multiple_pxi_connections_from_single_test_connector(self):
        # Conector A mapea tanto a PXI Entrada 1 como a PXI Entrada 2
        AdapterConnection.objects.create(
            adapter=self.adapter,
            test_connector=self.test_connector,
            pxi_connector=self.pxi_connector_1
        )
        AdapterConnection.objects.create(
            adapter=self.adapter,
            test_connector=self.test_connector,
            pxi_connector=self.pxi_connector_2
        )

        self.assertEqual(self.adapter.connections.count(), 2)

    def test_duplicate_connection_raises_error(self):
        AdapterConnection.objects.create(
            adapter=self.adapter,
            test_connector=self.test_connector,
            pxi_connector=self.pxi_connector_1
        )
        with self.assertRaises(Exception):
            AdapterConnection.objects.create(
                adapter=self.adapter,
                test_connector=self.test_connector,
                pxi_connector=self.pxi_connector_1
            )
 """
 
import re
from dataclasses import dataclass
from home.utils import find_opposite_sex_connectors

COMPATIBLE_CONNECTOR_TYPES = {
    "DB": [("DB", False), ("DD", True)],
    "DD": [("DD", False), ("DB", True)],
}

@dataclass
class FixedConnector:
    connector_type: str
    label: str

@dataclass
class AdapterConnector:
    connector_type: str
    label: str
    connector_side: str
    adapter_name: str

def test_find_opposite_sex_connectors_dd15f():
    fixed_connectors = [
        FixedConnector("DB15M", "Zócalo 1"),
        FixedConnector("DD15M", "Zócalo 2"),
    ]
    adapter_connectors = [
        AdapterConnector("DB15M", "AdapterPortA", "test-side", "Adaptador X"),
        AdapterConnector("DD15M", "AdapterPortB", "test-side", "Adaptador Y"),
        AdapterConnector("DB15M", "AdapterPortC", "non-test-side", "Adaptador Z"),
    ]

    result = find_opposite_sex_connectors("DD15F", fixed_connectors, adapter_connectors)

    assert len(result) == 4
    assert ('fixed', fixed_connectors[1], 'DD', False) in result
    assert ('fixed', fixed_connectors[0], 'DB', True) in result
    assert ('adapter', adapter_connectors[1], 'DD', False) in result
    assert ('adapter', adapter_connectors[0], 'DB', True) in result

def test_invalid_format_returns_empty():
    result = find_opposite_sex_connectors("DB15", [], [])
    assert result == []

def test_no_matches_returns_empty():
    result = find_opposite_sex_connectors("DB9F", [], [])
    assert result == []
