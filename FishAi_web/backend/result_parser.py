class ResultParser:

    @staticmethod
    def parse(result):
        if hasattr(result, "probs") and result.probs is not None:
            probs = result.probs
            cls_id = int(probs.top1)
            cls_name = result.names.get(cls_id, str(cls_id))
            confidence = float(probs.top1conf)
            return {
                "type": "classify",
                "label": cls_name,
                "confidence": confidence,
                "count": 1,
            }

        if hasattr(result, "boxes") and result.boxes is not None:
            count = len(result.boxes)
            return {
                "type": "detect",
                "label": "",
                "confidence": 0,
                "count": count,
            }

        return {
            "type": "unknown",
            "label": "",
            "confidence": 0,
            "count": 0,
        }
