# deploy-streamlit-app

This app can be used as a starting point to easily create and deploy a GenAI demo, with web interface and user authentication. It is written in python only, with cdk template to deploy on AWS.

It deploys a basic Streamlit app, and contains the following components:

* The Streamlit app in ECS/Fargate, behind an ALB and CloudFront
* A Cognito user pool in which you can manage users

By default, the Streamlit app has the following features:

* Authentication through Cognito
* Connection to Bedrock 

## Architecture diagram

![Architecture diagram](img/archi_streamlit_cdk.png)

## Usage

In the docker_app folder, you will find the streamlit app. You can run it locally or with docker.

Note: for the docker version to run, you will need to give appropriate permissions to the container for bedrock access. This is not implemented yet.

In the main folder, you will find a cdk template to deploy the app on ECS / ALB.

Prerequisites:

* python3.11
* docker
* use a Chrome browser for development
* Agents for Amazon Bedrock you deployed from this [HR assistant example](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/agents-for-bedrock/use-case-examples/hr-assistant). Take note of the agent id and agent alias id and s3 bucket name
```text
        # vpc = ec2.Vpc(self, f"{prefix}AppVpc", ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
        #     max_azs=2, vpc_name=f"{prefix}-stl-vpc", nat_gateways=1)
        vpc = ec2.Vpc.from_lookup(self, f"{prefix}AppVpc", vpc_id=Config.VPC_ID)
```

To deploy:

1. Edit `docker_app/config_file.py`, 
     * choose a `STACK_NAME` and a `CUSTOM_HEADER_VALUE`.
     * replace value of `VPC_ID = "vpc-id-here"` with your existing VPC.
     * replace value of the following
```text
    BEDROCK_AGENT_ALIAS_ID = "BEDROCK_AGENT_ALIAS_ID_HERE"
    BEDROCK_AGENT_ID = "BEDROCK_AGENT_ID_HERE"
    S3_BUCKET_HR_ASSISTANCE_GENERATED_IMAGES = "S3_BUCKET_HR_ASSISTANCE_GENERATED_IMAGES_HERE"
```

2. Install dependencies
 
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Deploy the cdk template

```
cdk bootstrap
cdk deploy
```

The deployment takes 5 to 10 minutes.

Make a note of the output, in which you will find the CloudFront distribution URL
and the Cognito user pool id.

4. Create a user in the Cognito UserPool that has been created. You can perform this action from your AWS Console. 
5. From your browser, connect to the CloudFront distribution url.
6. Log in to the Streamlit app with the user you have created in Cognito.

## Testing and developing in Cloud9

After deployment of the cdk template containing the Cognito user pool required for authentication, you can test the Streamlit app directly from Cloud9.
You can either use docker, but this would require setting up a role with appropriate permissions, or run the Streamlit app directly in your terminal after having installed the required python dependencies.

To run the Streamlit app directly:

1. If you have activated a virtual env for deploying the cdk template, deactivate it:

```
deactivate
```

2. cd into the streamlit-docker directory, create a new virtual env, and install dependencies:

```
cd docker_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Launch the streamlit server

```
streamlit run app.py --server.port 8080
```

4. Click on the Preview/Preview running application button in Cloud9, and click on the button to Pop out the browser in a new window, as the Cloud9 embedded browser does not keep session cookies, which prevents the authentication mechanism to work properly.
If the new window does not display the app, you may need to configure your browser to accept cross-site tracking cookies.

5. You can now modify the streamlit app to build your own demo!

## Some limitations

* The connection between CloudFront and the ALB is in HTTP, not SSL encrypted.
This means traffic between CloudFront and the ALB is unencrypted.
It is **strongly recommended** to configure HTTPS by bringing your own domain name and SSL/TLS certificate to the ALB.
* The provided code is intended as a demo and starting point, not production ready.
The Python app relies on third party libraries like Streamlit and streamlit-cognito-auth.
As the developer, it is your responsibility to properly vet, maintain, and test all third party dependencies.
The authentication and authorization mechanisms in particular should be thoroughly evaluated.
More generally, you should perform security reviews and testing before incorporating this demo code in a production application or with sensitive data.
* In this demo, Amazon Cognito is in a simple configuration.
Note that Amazon Cognito user pools can be configured to enforce strong password policies,
enable multi-factor authentication,
and set the AdvancedSecurityMode to ENFORCED to enable the system to detect and act upon malicious sign-in attempts.
* AWS provides various services, not implemented in this demo, that can improve the security of this application.
Network security services like network ACLs and AWS WAF can control access to resources.
You could also use AWS Shield for DDoS protection and Amazon GuardDuty for threats detection.
Amazon Inspector performs security assessments.
There are many more AWS services and best practices that can enhance security -
refer to the AWS Shared Responsibility Model and security best practices guidance for additional recommendations.
The developer is responsible for properly implementing and configuring these services to meet their specific security requirements.
* Regular rotation of secrets is recommended, not implemented in this demo.

## Acknowledgments

This code is inspired from:

* https://github.com/tzaffi/streamlit-cdk-fargate.git
* https://github.com/aws-samples/build-scale-generative-ai-applications-with-amazon-bedrock-workshop/

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This application is licensed under the MIT-0 License. See the LICENSE file.