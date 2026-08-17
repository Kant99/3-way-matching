import asyncio

from app.agents.matching_agent import create_matching_agent
from app.capabilities.matching_tools import run_3_way_matching


def test_agent_invokes_3_way_matching_tool():
    agent = create_matching_agent()

    contract = {
        "contract_id": "C001",
        "contract_number": "CON-001",
        "quantity_tolerance": "+5%",
        "price_tolerance": "±2%",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 250,
                "amount": 25000,
            }
        ],
    }

    purchase_order = {
        "po_id": "PO001",
        "po_number": "PO-001",
        "contract_reference": "CON-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 250,
                "amount": 25000,
            }
        ],
    }

    invoice = {
        "invoice_id": "INV001",
        "invoice_number": "INV-001",
        "purchase_order_reference": "PO-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 250,
                "amount": 25000,
            }
        ],
    }

    prompt = f"""
Run deterministic 3-way matching.

You MUST use the run_3_way_matching tool.
Do not calculate or decide the validation result yourself.

Contract:
{contract}

Purchase Order:
{purchase_order}

Invoice:
{invoice}

After using the tool, report the final validation status.
"""

    async def run_agent():
        return await agent.run(prompt)

    response = asyncio.run(run_agent())

    assert response is not None
    assert response.text

    text = response.text.upper()

    assert "PASS" in text

    print("\nAgent response:")
    print(response.text)


def test_agent_interprets_matching_exceptions():
    agent = create_matching_agent()

    contract = {
        "contract_id": "C001",
        "contract_number": "CON-001",
        "quantity_tolerance": "+5%",
        "price_tolerance": "±2%",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 250,
                "amount": 25000,
            }
        ],
    }

    purchase_order = {
        "po_id": "PO001",
        "po_number": "PO-001",
        "contract_reference": "CON-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 106,
                "unit": "EA",
                "unit_price": 256,
                "amount": 27136,
            }
        ],
    }

    invoice = {
        "invoice_id": "INV001",
        "invoice_number": "INV-001",
        "purchase_order_reference": "PO-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 107,
                "unit": "EA",
                "unit_price": 257,
                "amount": 27499,
            }
        ],
    }

    prompt = f"""
Run deterministic 3-way matching for these documents.

You MUST use the run_3_way_matching tool.

Do not perform validation calculations yourself.

The deterministic matching tool is the authoritative
source for the validation result.

After receiving the tool result:

1. State the final validation status.
2. Identify every exception type returned by the tool.
3. For every exception, explain:
   - exception type
   - field
   - expected value
   - actual value
   - tolerance, when available
4. Explain the quantity exceptions.
5. Explain the price exceptions.
6. Do not independently calculate, recalculate,
   override, or infer validation outcomes.
7. Base the explanation only on the deterministic
   tool result.
8. Clearly state that the case requires review.

Contract:
{contract}

Purchase Order:
{purchase_order}

Invoice:
{invoice}
"""

    async def run_agent():
        return await agent.run(prompt)

    response = asyncio.run(run_agent())

    assert response is not None
    assert response.text

    text = response.text.upper()

    # Final validation status
    assert "EXCEPTION" in text

    # Exception types
    assert "QUANTITY" in text
    assert "PRICE" in text

    # Fields
    assert "QUANTITY" in text
    assert "UNIT_PRICE" in text or "UNIT PRICE" in text

    # Deterministic values
    assert "106" in text
    assert "107" in text
    assert "256" in text
    assert "257" in text

    # Tolerance information
    assert "5%" in text or "5 %" in text
    assert "2%" in text or "2 %" in text

    # Review recommendation
    assert "REVIEW" in text

    print("\nAgent exception response:")
    print(response.text)

def test_run_3_way_matching_preserves_evidence():
    contract = {
        "contract_id": "C001",
        "contract_number": "CON-001",
        "quantity_tolerance": "+5%",
        "price_tolerance": "±2%",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 250,
                "amount": 25000,
            }
        ],
    }

    purchase_order = {
        "po_id": "PO001",
        "po_number": "PO-001",
        "contract_reference": "CON-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 106,
                "unit": "EA",
                "unit_price": 256,
                "amount": 27136,
            }
        ],
    }

    invoice = {
        "invoice_id": "INV001",
        "invoice_number": "INV-001",
        "purchase_order_reference": "PO-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 107,
                "unit": "EA",
                "unit_price": 257,
                "amount": 27499,
            }
        ],
    }

    result = run_3_way_matching(
        contract=contract,
        purchase_order=purchase_order,
        invoice=invoice,
    )

    assert result["status"] == "EXCEPTION"
    assert result["exceptions"]

    evidence_found = False

    for exception in result["exceptions"]:
        if exception["evidence"]:
            evidence_found = True

            assert isinstance(exception["evidence"], list)

            for evidence in exception["evidence"]:
                assert isinstance(evidence, dict)

    assert evidence_found