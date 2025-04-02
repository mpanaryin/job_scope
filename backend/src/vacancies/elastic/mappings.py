VACANCY_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "source": {
                "type": "object",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "keyword"},
                }
            },
            "name": {"type": "text"},
            "url": {"type": "keyword"},
            "description": {"type": "text"},
            "area": {
                "type": "object",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "keyword"},
                    "url": {"type": "keyword"}
                }
            },
            "address": {
                "type": "object",
                "properties": {
                    "city": {"type": "keyword"},
                    "street": {"type": "text"},
                    "building": {"type": "text"},
                    "raw": {"type": "text"},
                    "lat": {"type": "float"},
                    "lng": {"type": "float"}
                }
            },
            "employer": {
                "type": "object",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text"},
                    "trusted": {"type": "boolean"},
                    "url": {"type": "keyword"}
                }
            },
            "salary": {
                "type": "object",
                "properties": {
                    "currency": {"type": "keyword"},
                    "from": {"type": "integer"},
                    "to": {"type": "integer"},
                    "gross": {"type": "boolean"}
                }
            },
            "experience": {
                "type": "object",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text"}
                }
            },
            "employment": {
                "type": "object",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text"}
                }
            },
            "schedule": {
                "type": "object",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text"}
                }
            },
            "snippet": {
                "type": "object",
                "properties": {
                    "requirement": {"type": "text"},
                    "responsibility": {"type": "text"}
                }
            },
            "has_test": {"type": "boolean"},
            "is_archived": {"type": "boolean"},
            "published_at": {"type": "date"},
            "created_at": {"type": "date"}
        }
    }
}
