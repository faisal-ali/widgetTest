import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_apigateway as apigateway,
                     aws_lambda as lambda_,
                     aws_dynamodb as dynamodb,
                     aws_iam as iam,
                     aws_logs as logs,
                     aws_cognito as cognito)

class WidgetService(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        api = apigateway.RestApi(self, "widgets-api",
                  rest_api_name="Widget Service",
                  description="This service serves widgets.",
                  deploy_options=apigateway.StageOptions(
                      logging_level=apigateway.MethodLoggingLevel.INFO
                  )
         )

        # create cognito userpool
        user_pool = cognito.UserPool(self, "UserPool")

        auth = apigateway.CognitoUserPoolsAuthorizer(
            self,
            "WidgetsAuthorizer",
            cognito_user_pools=[user_pool]
        )

        handler = lambda_.Function(
            self, "WidgetHandler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("resources"),
            handler="widgets.lambda_handler"
        )

        get_widgets_integration = apigateway.LambdaIntegration(
            handler,
            request_templates={
                "application/json": '{ "statusCode": "200" }'
            }
        )

        # add query strings "id", "widgetType" and "widgetColor" to above api method
        api.root.add_method(
            "GET",
            get_widgets_integration,
            api_key_required=True,
            request_parameters={
                "method.request.querystring.id": True,
                "method.request.querystring.widgetType": True,
                "method.request.querystring.widgetColor": True
            },
            authorizer=auth,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )


        #create a "post" method for above api with integration to above "handler" lambda function
        post_widget_integration = apigateway.LambdaIntegration(handler)

        api.root.add_method(
            "POST",
            post_widget_integration,
            authorizer=auth,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )   # POST /

        #create a "delete" method for above api with integration to above "handler" lambda function
        delete_widget_integration = apigateway.LambdaIntegration(handler)
        # add query strings "id", "widgetType" and "widgetColor" to delete api method
        api.root.add_method(
            "DELETE",
            delete_widget_integration,
            api_key_required=True,
            request_parameters={
                "method.request.querystring.id": True,
                "method.request.querystring.widgetType": True
            }
        )

        #create a "put" method for above api with integration to above "handler" lambda function
        put_widget_integration = apigateway.LambdaIntegration(handler)
        api.root.add_method(
            "PUT",
            put_widget_integration,
            api_key_required=True
        )

        plan = api.add_usage_plan("UsagePlan",
                      name="Easy",
                      throttle=apigateway.ThrottleSettings(
                          rate_limit=10,
                          burst_limit=2
                      )
                  )

        key = api.add_api_key("ApiKey")
        plan.add_api_key(key)

        plan.add_api_stage(
            stage=api.deployment_stage
        )

        # crete dynamodb table
        cfn_table = dynamodb.Table(
                        self,
                        "MyWidgetTable",
                        partition_key=dynamodb.Attribute(
                            name="id",
                            type=dynamodb.AttributeType.STRING
                        ),
                        sort_key=dynamodb.Attribute(
                            name="widgetType",
                            type=dynamodb.AttributeType.STRING
                        ),
                        table_name="Widgetstable",
                        billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
                    )

        cfn_table.grant_read_write_data(handler)