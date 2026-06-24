import frappe

from marina_costing.marina_costing.doctype.supplier_costing_quote.supplier_costing_quote import (
    calculate_quote_totals,
)


def validate_supplier_costing_quote(doc, method=None):
    calculate_quote_totals(doc)


def can_manage_all_quotes():
    return bool(
        {"Supplier Costing Manager", "System Manager", "Purchase Manager"}
        & set(frappe.get_roles(frappe.session.user))
    )


@frappe.whitelist()
def get_supplier_costing_quotes(status=None):
    filters = {}
    if status in {"Pending", "Approved", "Rejected", "Cancelled"}:
        filters["status"] = status
    if not can_manage_all_quotes():
        filters["owner"] = frappe.session.user

    return frappe.get_all(
        "Supplier Costing Quote",
        filters=filters,
        fields=[
            "name",
            "status",
            "supplier",
            "style_no",
            "style_description",
            "category",
            "currency",
            "quoted_unit_cost",
            "target_gap",
            "modified",
        ],
        order_by="modified desc",
        limit_page_length=100,
    )


@frappe.whitelist()
def create_supplier_costing_quote():
    doc = frappe.new_doc("Supplier Costing Quote")
    doc.status = "Pending"
    doc.currency = "RMB"

    for size in ["XXS", "XS", "S", "M", "L", "XL", "XXL"]:
        doc.append("size_curve", {"size": size})

    for check in [
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
    ]:
        doc.append("review_lines", {"check_item": check, "review_status": "Pending"})

    doc.insert()
    return doc.name


@frappe.whitelist()
def close_supplier_costing_quote(name):
    doc = frappe.get_doc("Supplier Costing Quote", name)
    doc.status = "Approved"
    doc.save()
    return doc.name


@frappe.whitelist()
def reopen_supplier_costing_quote(name):
    doc = frappe.get_doc("Supplier Costing Quote", name)
    doc.status = "Pending"
    doc.save()
    return doc.name
