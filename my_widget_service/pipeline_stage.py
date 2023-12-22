from constructs import Construct
from aws_cdk import (
    Stage
)
from .widget_resources_stack import WidgetResourceStack

class WidgetPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = WidgetResourceStack(self, 'widget-' + id, **kwargs)