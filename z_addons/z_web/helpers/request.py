import json


class ZRequest:
    @staticmethod
    def parse_to_json(payload):
        data = payload.get("data", {})
        if isinstance(data, str):
            return json.loads(data)
        return {}
