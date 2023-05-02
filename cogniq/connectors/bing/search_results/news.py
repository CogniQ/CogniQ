def parse_news(*, results, item):
    target_id = item["value"]["id"]
    result = next(
        iter(filter(lambda el: el["id"] == target_id, results["news"]["value"])),
        None,
    )

    if result:
        parsed_result = {
            "name": result.get("name"),
            "snippet": result.get("description"),
            "url": result.get("url"),
        }
        return parsed_result
    else:
        return None
