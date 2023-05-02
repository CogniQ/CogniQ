def parse_webpages(*, results, item):
    target_id = item["value"]["id"]
    result = next(
        iter(filter(lambda el: el["id"] == target_id, results["webPages"]["value"])),
        None,
    )

    if result:
        parsed_result = {
            "name": result.get("name"),
            "snippet": result.get("snippet"),
            "url": result.get("url"),
        }
        return parsed_result
    else:
        return None
