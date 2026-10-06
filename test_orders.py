import unittest
from orders import list_orders, migrate_orders

DATA = [dict(id=3, tenant_id="A"), dict(id=2, tenant_id="B"), dict(id=1, tenant_id="A")]

class ContractTests(unittest.TestCase):
    def test_tenant_isolation(self):
        self.assertEqual([o["id"] for o in list_orders(DATA, "A")], [1, 3])
    def test_page_one(self):
        self.assertEqual([o["id"] for o in list_orders(DATA, "A", 1, 1)], [1])
    def test_page_two(self):
        self.assertEqual([o["id"] for o in list_orders(DATA, "A", 2, 1)], [3])
    def test_empty_tenant(self):
        self.assertEqual(list_orders(DATA, "Z"), [])
    def test_zero_page(self):
        with self.assertRaises(ValueError): list_orders(DATA, "A", 0)
    def test_negative_page(self):
        with self.assertRaises(ValueError): list_orders(DATA, "A", -1)
    def test_zero_size(self):
        with self.assertRaises(ValueError): list_orders(DATA, "A", 1, 0)
    def test_migration_preserves_ids(self):
        self.assertEqual([o["id"] for o in migrate_orders(DATA)], [3, 2, 1])
    def test_migration_updates_version(self):
        updated=migrate_orders(DATA)
        self.assertEqual(len(updated), 3)
        self.assertTrue(all(o["schema_version"] == 2 for o in updated))
    def test_inputs_unchanged(self):
        before=[dict(o) for o in DATA]
        migrate_orders(DATA)
        self.assertEqual(DATA, before)

if __name__ == "__main__": unittest.main()
