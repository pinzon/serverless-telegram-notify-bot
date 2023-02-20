import aws_cdk as core
import aws_cdk.assertions as assertions

from hackathon.hackathon_stack import HackathonStack

# example tests. To run these tests, uncomment this file along with the example
# resource in hackathon/hackathon_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = HackathonStack(app, "hackathon")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
