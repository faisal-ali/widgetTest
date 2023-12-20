import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    pipelines as pipe_lines
)
from . import widget_resources_stack

class WidgetService(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source = pipe_lines.CodePipeline(self, 'widgets-pipeline',
                    pipeline_name='WidgetsPipeline',
                    synth=pipe_lines.ShellStep('Synth',
                          input=pipe_lines.CodePipelineSource.git_hub('faisal-ali/widgetTest', 'main'),
                          commands=[
                              'npm install -g aws-cdk',
                              'python -m pip install -r requirements.txt',
                              'python -m pip install aws-cdk-lib',
                              'cdk synth'
                          ])
                    )
        widget_resources_stack.WidgetResourceStack(self, 'WidgetsResourceStack')