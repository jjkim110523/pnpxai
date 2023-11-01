from typing import Any, List, Sequence, Tuple, Union, Optional, Callable

from torch import Tensor
from captum.attr import Lime as _Lime
from captum._utils.typing import BaselineType, TargetType
from plotly import express as px
from plotly.graph_objects import Figure

from open_xai.core._types import Model, DataSource
from open_xai.explainers._explainer import Explainer


class Lime(Explainer):
    def __init__(
            self,
            model: Model,
            interpretable_model: Optional[Model] = None,
            similarity_func: Optional[Callable] = None,
        ):
        super().__init__(model)
        self.method = _Lime(
            forward_func = model.forward,
            interpretable_model = interpretable_model,
            similarity_func = similarity_func,
        )

    def run(
        self,
        data: DataSource,
        baselines: BaselineType = None,
        target: TargetType = None,
        additional_forward_args: Any = None,
        feature_mask: Union[None, Tensor, Tuple[Tensor, ...]] = None,
        n_samples: int = 25,
        perturbations_per_eval: int = 1,
        return_input_shape: bool = True,
        show_progress: bool = False
    ) -> List[Tensor]:
        attributions = []

        if type(data) is Tensor:
            data = [data]

        for datum in data:
            attributions.append(self.method.attribute(
                datum,
                baselines,
                target,
                additional_forward_args,
                feature_mask,
                n_samples,
                perturbations_per_eval,
                return_input_shape,
                show_progress,
            ))

        return attributions

    def format_outputs_for_visualization(self, inputs: DataSource, outputs: DataSource, *args, **kwargs) -> Sequence[Figure]:
        return [[
            px.imshow(output.permute((1, 2, 0))) for output in batch
        ] for batch in outputs]
