from open_xai.explainers._explainer import Explainer
from open_xai.core._types import Model


class TCAV(Explainer):
    def __init__(self, model: Model):
        super().__init__(model)

    def attribute(self, *args, **kwargs):
        raise NotImplementedError()
