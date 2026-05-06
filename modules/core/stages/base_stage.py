# =========================================================
# BASE STAGE
# =========================================================

class BaseStage:

    """
    Base interface for all pipeline stages.
    """

    # =====================================================
    # PROCESS
    # =====================================================
    def process(
        self,
        *args,
        **kwargs
    ):

        raise NotImplementedError(
            "Stage must implement process()"
        )