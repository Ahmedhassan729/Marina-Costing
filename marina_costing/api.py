import frappe
from frappe import _

MANAGER_ROLES = {"Supplier Costing Manager", "System Manager"}
SUPPLIER_ROLES = {"Supplier", "Supplier Costing User"}


def can_manage_all_quotes():
    return bool(
        MANAGER_ROLES & set(frappe.get_roles(frappe.session.user))
    )


def require_quote_manager():
    if not can_manage_all_quotes():
        frappe.throw(_("Only a Supplier Costing Manager can change quote status."), frappe.PermissionError)


@frappe.whitelist()
def get_supplier_costing_quotes(status=None):
    filters = {}
    if status in {"Pending", "Approved", "Rejected", "Cancelled"}:
        filters["status"] = status
    if not can_manage_all_quotes():
        filters["owner"] = frappe.session.user

    return frappe.get_list(
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

    if can_manage_all_quotes():
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
    require_quote_manager()
    doc = frappe.get_doc("Supplier Costing Quote", name)
    doc.status = "Approved"
    doc.save()
    return doc.name


@frappe.whitelist()
def reopen_supplier_costing_quote(name):
    require_quote_manager()
    doc = frappe.get_doc("Supplier Costing Quote", name)
    doc.status = "Pending"
    doc.save()
    return doc.name
