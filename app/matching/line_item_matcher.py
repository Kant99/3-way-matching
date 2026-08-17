from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice


class LineItemMatcher:
    def match(
        self,
        contract: Contract,
        purchase_order: PurchaseOrder,
        invoice: Invoice,
    ) -> dict:
        contract_items = {
            item.item_code: item
            for item in contract.line_items
            if item.item_code is not None
        }

        purchase_order_items = {
            item.item_code: item
            for item in purchase_order.line_items
            if item.item_code is not None
        }

        invoice_items = {
            item.item_code: item
            for item in invoice.line_items
            if item.item_code is not None
        }

        all_item_codes = (
            set(contract_items)
            | set(purchase_order_items)
            | set(invoice_items)
        )

        matches = []

        for item_code in sorted(all_item_codes):
            matches.append(
                {
                    "item_code": item_code,
                    "contract": contract_items.get(item_code),
                    "purchase_order": purchase_order_items.get(item_code),
                    "invoice": invoice_items.get(item_code),
                }
            )

        return {
            "matches": matches,
        }