import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    Stack
)
from aws_cdk import (aws_apigateway as apigateway,
                     aws_lambda as lambda_,
                     aws_dynamodb as dynamodb,
                     aws_cognito as cognito)


class WidgetResourceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api = apigateway.RestApi(
            self,
            "widgets-api",
            rest_api_name="Widget Service",
            description="This service serves widgets.",
            deploy_options=apigateway.StageOptions(
                logging_level=apigateway.MethodLoggingLevel.INFO
            ),
            cloud_watch_role=True
        )

        # create cognito userpool
        user_pool = cognito.UserPool(self, "UserPool")

        #add app client to above cognito userpool with callback url set to http://localhost
        user_pool.add_client(
            "AppClient",
             generate_secret=True,
             auth_flows=cognito.AuthFlow(
                 admin_user_password=True,
                 user_password=True
             ),
             #add grant types to above app client
             o_auth=cognito.OAuthSettings(
                 flows=cognito.OAuthFlows(
                     authorization_code_grant=True
                 ),
                 callback_urls=["http://localhost", "https://oauth.pstmn.io/v1/callback"]
             ),
             user_pool_client_name="widgetclient"
        )


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
            table_name="Widgettable",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        cfn_table.grant_read_write_data(handler)

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

        # create a "post" method for above api with integration to above "handler" lambda function
        post_widget_integration = apigateway.LambdaIntegration(handler)

        api.root.add_method(
            "POST",
            post_widget_integration,
            authorizer=auth,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )  # POST /

        # create a "delete" method for above api with integration to above "handler" lambda function
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

        # create a "put" method for above api with integration to above "handler" lambda function
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
