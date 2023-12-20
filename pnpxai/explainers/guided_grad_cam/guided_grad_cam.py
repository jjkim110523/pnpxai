from typing import List, Dict, Optional, Any, Union
from torch import nn, Tensor

from captum.attr import GuidedGradCam as GuidedGradCamCaptum
from captum._utils.typing import TargetType
from zennit.types import SubclassMeta

from pnpxai.core._types import Model, DataSource, Task
from pnpxai.detector import ModelArchitecture
# from pnpxai.explainers.utils.operation_graph import OperationGraph
from pnpxai.explainers._explainer import Explainer

class Pool2d(metaclass=SubclassMeta):
    __subclass__ = (
        nn.AvgPool2d,
        nn.AdaptiveAvgPool2d,
        nn.MaxPool2d,
        nn.AdaptiveMaxPool2d,
    )

class GuidedGradCam(Explainer):
    def __init__(self, model: Model):
        super().__init__(model=model)
        self.source = GuidedGradCamCaptum(
            self.model,
            # layer=self._find_last_conv_layer()
            layer=self._find_target_layer(),
        )

    # def _find_last_conv_layer(self) -> Optional[nn.Conv2d]:
    #     op_graph = OperationGraph(self.model)
    #     if op_graph.tail is None:
    #         return None

    #     nodes_to_visit = [op_graph.tail]
    #     while len(nodes_to_visit) > 0:
    #         node = nodes_to_visit.pop()
    #         if isinstance(node.operator, nn.Conv2d):
    #             return node.operator

    #         nodes_to_visit.extend(node.prev_nodes)

    #     return None
    
    def _find_target_layer(self) -> Optional[Union[nn.Conv2d, Pool2d]]:
        ma = ModelArchitecture(self.model)
        conv_nodes = ma.find_node(lambda n: isinstance(n.operator, nn.Conv2d), all=True)
        assert conv_nodes, "Must have nn.Conv2d"
        last_conv_node = conv_nodes[-1]
        pool_nodes = ma.find_node(
            lambda n: isinstance(n.operator, Pool2d),
            root=last_conv_node,
            all=True,
        )
        assert pool_nodes, "Must have pooling layer"
        return pool_nodes[-1].operator

    def attribute(
        self,
        inputs: DataSource,
        targets: TargetType = None,
        additional_forward_args: Any = None,
        interpolate_mode: str = "nearest",
        attribute_to_layer_input: bool = False,
    ) -> List[Tensor]:
        attributions = self.source.attribute(
            inputs=inputs,
            target=targets,
            additional_forward_args=additional_forward_args,
            interpolate_mode=interpolate_mode,
            attribute_to_layer_input=attribute_to_layer_input,
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
        explanations = explanations.transpose(-1, -3)\
            .transpose(-2, -3)
        return super().format_outputs_for_visualization(
            inputs=inputs,
            targets=targets,
            explanations=explanations,
            task=task,
            kwargs=kwargs
        )
