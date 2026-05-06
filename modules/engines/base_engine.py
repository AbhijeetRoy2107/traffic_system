# =========================================================
# BASE ENGINE
# =========================================================

class BaseEngine:

    def detect(
        self,
        *args,
        **kwargs
    ):

        raise NotImplementedError(
            "Engine must implement detect()"
        )