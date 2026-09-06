def get_relationship_id(data, relationship_name):
    items = (
        data.get("relationships", {})
            .get(relationship_name, {})
            .get("data", [])
    )

    if not items:
        return None

    return items[0].get("id")