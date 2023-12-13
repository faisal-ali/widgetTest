import aws_cdk as core
import aws_cdk.assertions as assertions

from my_widget_service.my_widget_service_stack import MyWidgetServiceStack

# example tests. To run these tests, uncomment this file along with the example
# resource in my_widget_service/my_widget_service_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MyWidgetServiceStack(app, "my-widget-service")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
