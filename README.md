# Cloud Resume Portfolio

This is Karan Ahuja's cloud engineer resume portfolio. It is intentionally
static at first so it can be deployed quickly, then expanded with serverless
features in stages.

Live site:

```text
https://da1sr8y7lqivy.cloudfront.net
```

## Customize

##cloudfront url: da1sr8y7lqivy.cloudfront.net

Edit these files:

- `index.html` for your name, resume summary, skills, projects, experience, and contact links.
- `styles.css` for visual changes.
- `resume.pdf` is the downloadable resume linked from the site.

Suggested personal details to update:

- GitHub profile URL
- Any updated certifications
- Any new cloud projects with measurable outcomes
- A custom domain once the AWS deployment is ready

## Local Preview

For the static page only, open `index.html` in your browser.

For the contact query form and Python CRUD backend, run:

```bash
python server.py
```

Then open:

```text
http://localhost:8000
```

The local CRUD API is:

- `POST /api/queries` to create a query
- `GET /api/queries` to list queries
- `GET /api/queries/{id}` to read one query
- `PUT /api/queries/{id}` to update a query
- `DELETE /api/queries/{id}` to delete a query

## Email Notifications

The backend can email new contact form messages to:

```text
karanahuja57226@gmail.com
```

Set these environment variables before starting the server:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-sending-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM=your-sending-email@gmail.com
```

For Gmail, use an app password rather than your normal Gmail password. The form
still saves messages to `queries.db` if email is not configured or if sending
fails.

## AWS Deployment Path

The first AWS deployment hosts the static portfolio with:

- S3 private bucket
- CloudFront CDN
- Origin Access Control
- GitHub Actions deployment

The local Python backend is not deployed to S3/CloudFront because static hosting
cannot run Python. The next backend step is converting the contact message API
to API Gateway, Lambda, DynamoDB, and SES.

### One-time AWS setup

Install and configure the AWS CLI, then run this from the project root:

```powershell
.\deploy-static.ps1
```

This creates the CloudFormation stack, uploads the static files, invalidates
CloudFront, and prints the CloudFront URL.

To choose a specific region:

```powershell
.\deploy-static.ps1 -Region ap-southeast-2
```

### GitHub Actions setup

After the static stack is deployed, get the stack outputs:

```powershell
aws cloudformation describe-stacks `
  --stack-name cloud-engineer-portfolio `
  --region ap-southeast-2 `
  --query "Stacks[0].Outputs"
```

Deploy the GitHub Actions IAM role:

```powershell
aws cloudformation deploy `
  --stack-name cloud-engineer-portfolio-github-actions `
  --template-file infra/github-actions-role.yaml `
  --parameter-overrides `
      SiteBucketName=YOUR_BUCKET_NAME `
      CloudFrontDistributionId=YOUR_DISTRIBUTION_ID `
  --capabilities CAPABILITY_NAMED_IAM `
  --region ap-southeast-2
```

Then add these to your GitHub repository:

- Repository secret: `AWS_DEPLOY_ROLE_ARN`
- Repository variable: `AWS_REGION`
- Repository variable: `S3_BUCKET_NAME`
- Repository variable: `CLOUDFRONT_DISTRIBUTION_ID`

After that, every push to `main` deploys the static portfolio.

### Future deployment steps

1. Add a custom domain with Route 53 and ACM.
2. Convert the contact message backend to API Gateway, Lambda, DynamoDB, and SES.
3. Add a visitor counter with API Gateway, Lambda, and DynamoDB.
4. Add monitoring with CloudWatch logs, metrics, and alarms.

## Suggested Architecture

```text
GitHub
  -> GitHub Actions
  -> S3 private bucket
  -> CloudFront CDN
  -> Route 53 custom domain
  -> Browser

Optional:
Browser -> API Gateway -> Lambda -> DynamoDB
Browser -> API Gateway -> Lambda -> SES/SNS
```

## Interview Story

This project can demonstrate:

- Static hosting and CDN fundamentals
- HTTPS and DNS setup
- IAM least-privilege thinking
- CI/CD automation
- Serverless API design
- DynamoDB persistence
- Cloud project documentation
