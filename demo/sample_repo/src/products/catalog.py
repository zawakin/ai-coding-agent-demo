"""Product catalog management."""


def get_product_list(category: str = None, limit: int = 100) -> list:
    """
    Get a list of products, optionally filtered by category.

    Args:
        category: Optional category filter
        limit: Maximum number of products to return

    Returns:
        List of product dictionaries
    """
    # TODO: Implement actual database query
    # This is placeholder data
    products = [
        {
            "id": "prod_1",
            "name": "Laptop",
            "category": "electronics",
            "price": 999.99,
            "stock": 15
        },
        {
            "id": "prod_2",
            "name": "Desk Chair",
            "category": "furniture",
            "price": 199.99,
            "stock": 30
        },
        {
            "id": "prod_3",
            "name": "Coffee Maker",
            "category": "appliances",
            "price": 79.99,
            "stock": 50
        }
    ]

    if category:
        products = [p for p in products if p["category"] == category]

    return products[:limit]


def get_product_details(product_id: str) -> dict:
    """
    Get detailed information about a specific product.

    Args:
        product_id: The product ID

    Returns:
        Product details dictionary or None if not found
    """
    # TODO: Implement actual database lookup
    products = get_product_list()

    for product in products:
        if product["id"] == product_id:
            return product

    return None
