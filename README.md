# Marina Costing

Custom Frappe / ERPNext v15 app for Marina Fashion Retail supplier costing quotes.

## What This App Adds

- Supplier-facing costing quote document
- ERPNext Supplier link
- Item/style reference
- RMB default currency
- Design/sample image attachment
- Cost breakdown child table
- Packaging and logistics child table
- Size curve child table
- Internal review child table
- Pending / Closed status workflow field
- Supplier portal page at `/supplier-costing`

## Frappe Cloud Install

1. Push this repository to:

   `https://github.com/Ahmedhassan729/Marina-Costing`

2. In Frappe Cloud, open your Bench.
3. Go to **Apps**.
4. Add a custom app from GitHub:

   `https://github.com/Ahmedhassan729/Marina-Costing`

5. Select branch, usually `main`.
6. Install the app on your ERPNext v15 site.
7. Run migration from Frappe Cloud if prompted.

## Self-Hosted Install

```bash
bench get-app https://github.com/Ahmedhassan729/Marina-Costing.git
bench --site YOUR-SITE install-app marina_costing
bench --site YOUR-SITE migrate
bench restart
```

## Supplier Access

Create supplier users in ERPNext and assign them one of:

- `Supplier`
- `Supplier Costing User`

Suppliers can open:

`https://YOUR-SITE/supplier-costing`

Internal users can review quotes from the Desk list:

`Supplier Costing Quote`

## Recommended ERPNext Setup

- Keep ERPNext `Supplier` records clean and active.
- Link each quote to an ERPNext `Item` where available.
- Use `Pending` while supplier quote is under review.
- Set `Closed` when the quote is finalized, rejected, or superseded.

