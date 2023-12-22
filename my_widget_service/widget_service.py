import os

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    Stack,
    pipelines as pipe_lines
)
from . import widget_resources_stack
from .pipeline_stage import WidgetPipelineStage

class WidgetService(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pipeline = pipe_lines.CodePipeline(
            self,
            'widgets-pipeline',
            pipeline_name='WidgetsPipeline',
            synth=pipe_lines.ShellStep(
                'Synth',
                input=pipe_lines.CodePipelineSource.git_hub('faisal-ali/widgetTest', 'main'),
                commands=[
                    'npm install -g aws-cdk',
                    'python -m pip install --upgrade pip',
                    'python -m pip install -r requirements.txt',
                    'python -m pip install aws-cdk-lib',
                    'echo ${DEV_ACCOUNT}',
                    'export DEV_ACCOUNT=${DEV_ACCOUNT}',
                    'echo this should list the dev account: $DEV_ACCOUNT',
                    'cdk synth'
                ]
            )
        )

        dev_stage = pipeline.add_stage(WidgetPipelineStage(
            self,
            'dev',
            env=cdk.Environment(account='281971678385', region='ap-southeast-1')
        ))

        #this line is for testing only
        dev_stage.add_pre(pipe_lines.ManualApprovalStep('Promote To Dev'))

        dev_stage.add_post(pipe_lines.ManualApprovalStep('Promote To Prod'))

        prod_stage = pipeline.add_stage(WidgetPipelineStage(
            self,
            'prod',
            env=cdk.Environment(account='281971678385', region='ap-southeast-2')
        ))
