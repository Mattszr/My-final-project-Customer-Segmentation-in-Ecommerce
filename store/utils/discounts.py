from decimal import Decimal, ROUND_HALF_UP

RFM_DISCOUNT_MAP = {
    "Premium Customer": Decimal("0.10"),
    "Loyal and High-Value Customer": Decimal("0.05"),
    "Mid-Tier Customer": Decimal("0.02"),
    "New and Low-Value Customer": Decimal("0.00"),
}

from decimal import Decimal, ROUND_HALF_UP

def calculate_discounted_total(customer, cart_items, quantities):
    total = Decimal("0.00")

    # Calculate the total price for each item in the cart
    for item in cart_items:
        product_id = str(item.id)
        quantity = int(quantities.get(product_id, 1))

        # If there is a discounted price, use it, otherwise use the regular price.
        price = item.discounted_price if item.discounted_price else item.price
        total += price * quantity

    # Get discount rate by RFM segment
    segment = customer.customerstats.rfm_segment if hasattr(customer, "customerstats") else None
    discount_rate = RFM_DISCOUNT_MAP.get(segment, Decimal("0.00"))

    # Calculate the discount amount and the total discounted amount
    discount_amount = (total * discount_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    discounted_total = (total - discount_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return discounted_total, discount_amount, discount_rate
