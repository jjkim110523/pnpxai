from typing import Any, Optional, Dict
from captum._utils.typing import TargetType

from pnpxai.core._types import Model, DataSource, Task
from pnpxai.explainers._explainer import Explainer
from .lrp_zennit import LRPZennit

class LRP(Explainer):
    def __init__(self, model: Model):
        super(LRP, self).__init__(model)
        self.source = LRPZennit(model)

    def attribute(
        self,
        inputs: DataSource,
        targets: TargetType = None,
        additional_forward_args: Any = None,
        return_convergence_delta: bool = False,
        verbose: bool = False
    ) -> DataSource:
        attributions = self.source.attribute(
            inputs=inputs,
            target=targets,
            additional_forward_args=additional_forward_args,
            return_convergence_delta=return_convergence_delta,
            verbose=verbose
        )

        return attributions

    def format_outputs_for_visualization(
        self,
        inputs: DataSource,
        targets: DataSource,
        explanations: DataSource,
        task: Task,
        kwargs: Optional[Dict[str, Any]] = None,
    ):
        explanations = explanations.permute((1, 2, 0))
        return super().format_outputs_for_visualization(
            inputs=inputs,
            targets=targets,
            explanations=explanations,
            task=task,
            kwargs=kwargs
        )
