def list_orders(orders, tenant_id, page=1, page_size=20):
    if page < 1 or page_size < 1:
        raise ValueError("invalid pagination")
    selected = sorted(orders, key=lambda o: o["id"])
    start = (page - 1) * page_size
    return selected[start:start + page_size]


def migrate_orders(orders):
    return [dict(order, schema_version=2) for order in orders]
