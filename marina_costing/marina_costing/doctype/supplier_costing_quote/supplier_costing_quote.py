import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SupplierCostingQuote(Document):
    def validate(self):
        calculate_quote_totals(self)


def calculate_quote_totals(doc):
    direct_cost = 0
    for row in doc.get("cost_lines", []):
        allocation_qty = max(flt(row.allocation_qty), 1)
        row.cost_per_garment = (
            flt(row.consumption_per_garment)
            * (1 + flt(row.wastage_percentage) / 100)
            * flt(row.cost_per_unit)
            + flt(row.sampling_charges) / allocation_qty
        )
        direct_cost += flt(row.cost_per_garment)

    packaging_cost = 0
    logistics_cost = 0
    logistics_types = {"Testing / Compliance", "Inspection", "Freight", "Duty / Customs"}
    for row in doc.get("packaging_logistics", []):
        row.cost_per_garment = flt(row.qty_per_garment) * flt(row.cost_per_unit)
        if row.cost_type in logistics_types:
            logistics_cost += flt(row.cost_per_garment)
        else:
            packaging_cost += flt(row.cost_per_garment)

    total_bulk_qty = sum(flt(row.bulk_qty) for row in doc.get("size_curve", []))
    for row in doc.get("size_curve", []):
        row.size_curve_percentage = (flt(row.bulk_qty) / total_bulk_qty * 100) if total_bulk_qty else 0

    doc.direct_cost = direct_cost
    doc.packaging_cost = packaging_cost
    doc.logistics_cost = logistics_cost
    doc.rework_amount = direct_cost * flt(doc.rework_percentage) / 100
    doc.overhead_amount = (direct_cost + flt(doc.rework_amount)) * flt(doc.overhead_percentage) / 100
    doc.margin_amount = (
        direct_cost + flt(doc.rework_amount) + flt(doc.overhead_amount)
    ) * flt(doc.margin_percentage) / 100
    doc.quoted_unit_cost = (
        direct_cost
        + flt(doc.rework_amount)
        + flt(doc.overhead_amount)
        + flt(doc.margin_amount)
        + packaging_cost
        + logistics_cost
    )
    doc.target_gap = flt(doc.quoted_unit_cost) - flt(doc.target_unit_cost)
    doc.estimated_gross_margin = (
        (flt(doc.target_retail_price) - flt(doc.quoted_unit_cost)) / flt(doc.target_retail_price) * 100
        if flt(doc.target_retail_price)
        else 0
    )

    if not doc.brand:
        doc.brand = "Marina Fashion Retail"


@frappe.whitelist()
def get_default_review_lines():
    return [
        "Target cost achieved or justified",
        "Fabric consumption plausible vs tech pack",
        "Wastage reasonable for print, stripe, placement, or embellishment",
        "MOQ and MCQ acceptable",
        "Sample cost separated from bulk price",
        "Trims, labels, and branding included",
        "Packaging requirements included",
        "Testing and compliance included or clearly excluded",
        "Freight and incoterm clear",
        "Quote validity date provided",
        "Negotiation or redesign decision recorded",
    ]

