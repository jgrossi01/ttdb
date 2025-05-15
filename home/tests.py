from django.test import TestCase
from home.models import PhysicalConnector, Adapter, AdapterConnection, RelayCard, AdapterPinMap

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
