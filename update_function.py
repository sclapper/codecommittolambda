from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo, ZIP_STORED
import botocore
import logging
import boto3
import json
import io 

logger = logging.getLogger()
logger.setLevel(logging.INFO)
codecommit = boto3.client("codecommit")

def get_repo(repo, branch):

    try:
        response = codecommit.get_differences(
            repositoryName=repo,
            afterCommitSpecifier=branch,
        )
    except botocore.exceptions.ClientError as e:
        logger.error('could not get_differences... %s' %(e.response['Error']['Message']))

    differences = []
    while "nextToken" in response:
        try:
            response = codecommit.get_differences(
                repositoryName=repo,
                afterCommitSpecifier=branch,
                nextToken=response["nextToken"]
            )
        except botocore.exceptions.ClientError as e:
            logger.error('could not get_differences... %s' %(e.response['Error']['Message']))

        differences += response.get("differences", [])
    else:
        differences += response["differences"]
    return differences

def archive(repo, branch):

    buf = io.BytesIO()
    with ZipFile(buf, 'w', compression=ZIP_STORED, allowZip64=True) as Zip:

        for difference in get_repo(repo, branch):
            blobid = difference["afterBlob"]["blobId"]
            file_name = difference["afterBlob"]["path"]
            print(file_name)
            mode = difference["afterBlob"]["mode"]

            try:
                blob = codecommit.get_blob(repositoryName=repo, blobId=blobid)
            except botocore.exceptions.ClientError as e:
                logger.error('could not get_blob... %s' %(e.response['Error']['Message']))

            content = blob["content"]
            Zip.writestr(ZipInfo(file_name), content)

    return buf.getvalue()

def update_function(FunctionName, repo, branch):

    try:
        lambda_client = boto3.client('lambda')
        response = lambda_client.update_function_code(
            FunctionName=FunctionName,
            ZipFile=archive(repo, branch)
        )
        logger.info(f"updated {FunctionName} from {repo}, {branch}")
    except botocore.exceptions.ClientError as e:
        logger.error('could not update_function_code... %s' %(e.response['Error']['Message']))

def lambda_handler(event, context):

    logger.debug(f"event {json.dumps(event, indent = 4)}")
    trigger_name = event['Records'][0]['eventTriggerName']
    FunctionName = event['Records'][0]['customData']
    repo = event['Records'][0]['eventSourceARN'].split(':')[5]
    branch = event['Records'][0]['codecommit']['references'][0]['ref'].split('/')[2]
    update_function(FunctionName, repo, branch)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
