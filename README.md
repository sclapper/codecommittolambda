# codecommittolambda

codecommittolambda deploys CodeCommit repos to lambda automatically on change. This is more efficient and faster than code deploy for small scale projects.

Deploy update_function.py to lambda
  1. set timeout 15sec (adjust as needed)

Create CodeCommit trigger/s
  1. select repo
  2. set trigger name
  3. Events = "Push to existing  branch"
  4. select your trigger branch
  5. Custom data = Name of lambda function to update
  6. repeat steps if you have multiple functions for branches eg, master branch = function_1 (prod), dev branch = function_2 (dev)

Set IAM permissions
  1. (fast) add AWSCodeCommitReadOnly, AWSLambdaBasicExecutionRole, AWSLambdaRole, AWSLambda_FullAccess
  2. (secure) Adjust least privileged as required, rather than AWSLambda_FullAccess make policy with lambda:UpdateFunctionCode and limit resource to function/s etc
