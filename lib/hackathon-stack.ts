import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import { FunctionUrlAuthType } from 'aws-cdk-lib/aws-lambda';

export class HackathonStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const db =  new dynamodb.Table(this, "table", {
      tableName: "chats-ids",
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING }, 
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST, 
      tableClass: dynamodb.TableClass.STANDARD_INFREQUENT_ACCESS,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    })

    const fun = new lambda.Function(this, "function", {
      runtime: lambda.Runtime.PYTHON_3_9,
      code: lambda.Code.fromAsset("resources"),
      handler: "handler.handle",
      environment: {
        "TELEGRAM_TOKEN": "put-token-here",
        "TABLE_NAME": db.tableName
      },
    })
    const url = fun.addFunctionUrl({authType: FunctionUrlAuthType.NONE})

    const iamPolicy: iam.PolicyStatement = new iam.PolicyStatement({
      actions: ['dynamodb:*'],
      resources: [db.tableArn]
    }) 

    fun.addToRolePolicy(iamPolicy)

    const output = new cdk.CfnOutput(this, "url", {value: url.url})
  }
}
