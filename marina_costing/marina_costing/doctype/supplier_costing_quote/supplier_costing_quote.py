import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SupplierCostingQuote(Document):
    def validate(self):
        calculate_quote_totals(self)


def calculate_quote_totals(doc):
    direct_cost = 0
    for row in doc.get("cost_lines", []):
        row.cost_per_garment = (
            flt(row.consumption_per_garment)
            * (1 + flt(row.wastage_percentage) / 100)
            * flt(row.cost_per_unit)
        )
        direct_cost += flt(row.cost_per_garment)

    direct_cost += flt(doc.sampling_charge_per_unit)

    packaging_cost = 0
    for row in doc.get("packaging_logistics", []):
        row.cost_per_garment = flt(row.qty_per_garment) * flt(row.cost_per_unit)
        packaging_cost += flt(row.cost_per_garment)

    total_bulk_qty = sum(flt(row.bulk_qty) for row in doc.get("size_curve", []))
    for row in doc.get("size_curve", []):
        row.size_curve_percentage = (flt(row.bulk_qty) / total_bulk_qty * 100) if total_bulk_qty else 0

    doc.direct_cost = direct_cost
    doc.packaging_cost = packaging_cost
    conversion_rate = flt(doc.conversion_rate) or 1
    doc.target_unit_cost = (
        flt(doc.target_retail_price)
        * (1 - flt(doc.target_margin_percentage) / 100)
        / conversion_rate
    )

    base_cost = direct_cost + packaging_cost
    overhead_amount = base_cost * flt(doc.overhead_percentage) / 100
    doc.margin_amount = (base_cost + overhead_amount) * flt(doc.margin_percentage) / 100
    doc.quoted_unit_cost = base_cost + overhead_amount + flt(doc.margin_amount)
    doc.target_gap = flt(doc.quoted_unit_cost) - flt(doc.target_unit_cost)
    doc.estimated_gross_margin = (
        (flt(doc.target_retail_price) - flt(doc.quoted_unit_cost)) / flt(doc.target_retail_price) * 100
        if flt(doc.target_retail_price)
        else 0
    )


@frappe.whitelist()
def get_default_review_lines():
    return [
        "Target cost achieved or justified",
        "Fabric consumption plausible vs tech pack",
        "Wastage reasonable for print, stripe, placement, or embellishment",
        "MOQ and MCQ acceptable",
        "Sampling charge per unit entered when applicable",
        "Trims, labels, and branding included",
        "Packaging requirements included",
        "Testing and compliance included or clearly excluded",
        "Freight and commercial terms clear",
        "Quote validity date provided",
        "Negotiation or redesign decision recorded",
    ]
