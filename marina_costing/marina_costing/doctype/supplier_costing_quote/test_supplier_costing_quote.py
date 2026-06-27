from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from marina_costing.api import require_quote_manager


class TestSupplierCostingQuote(FrappeTestCase):
    def make_quote(self):
        return frappe.get_doc(
            {
                "doctype": "Supplier Costing Quote",
                "status": "Pending",
                "supplier": "Test Supplier",
                "style_no": "TEST-STYLE",
                "conversion_rate": 2,
                "target_retail_price": 100,
                "target_margin_percentage": 40,
                "sampling_charge_per_unit": 3,
                "margin_percentage": 20,
                "overhead_percentage": 10,
                "cost_lines": [
                    {
                        "cost_category": "Main Fabric",
                        "consumption_per_garment": 2,
                        "wastage_percentage": 10,
                        "cost_per_unit": 5,
                    }
                ],
                "packaging_logistics": [
                    {
                        "cost_type": "Polybag",
                        "qty_per_garment": 1,
                        "cost_per_unit": 2,
                    }
                ],
            }
        )

    @patch("frappe.get_roles", return_value=["Supplier"])
    def test_supplier_cannot_use_manager_transition(self, _get_roles):
        with self.assertRaises(frappe.PermissionError):
            require_quote_manager()

    @patch("frappe.get_roles", return_value=["Supplier Costing Manager"])
    def test_manager_can_use_manager_transition(self, _get_roles):
        require_quote_manager()

    def test_quote_calculation(self):
        quote = self.make_quote()
        quote.validate_numeric_inputs()

        from marina_costing.marina_costing.doctype.supplier_costing_quote.supplier_costing_quote import (
            calculate_quote_totals,
        )

        calculate_quote_totals(quote)

        self.assertAlmostEqual(quote.direct_cost, 14)
        self.assertAlmostEqual(quote.packaging_cost, 2)
        self.assertAlmostEqual(quote.target_unit_cost, 30)
        self.assertAlmostEqual(quote.margin_amount, 3.52)
        self.assertAlmostEqual(quote.quoted_unit_cost, 21.12)
        self.assertAlmostEqual(quote.target_gap, -8.88)

    def test_conversion_rate_must_be_positive(self):
        quote = self.make_quote()
        quote.conversion_rate = 0

        with self.assertRaises(frappe.ValidationError):
            quote.validate_numeric_inputs()

    def test_negative_cost_is_rejected(self):
        quote = self.make_quote()
        quote.cost_lines[0].cost_per_unit = -1

        with self.assertRaises(frappe.ValidationError):
            quote.validate_numeric_inputs()

    @patch("frappe.get_roles", return_value=["Supplier"])
    def test_supplier_cannot_set_internal_fields_on_new_quote(self, _get_roles):
        quote = self.make_quote()

        with self.assertRaises(frappe.PermissionError):
            quote.validate_internal_fields()
