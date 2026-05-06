# Cloud Resume Portfolio

This is Karan Ahuja's cloud engineer resume portfolio. It is intentionally
static at first so it can be deployed quickly, then expanded with serverless
features in stages.

## Customize

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

Open `index.html` in your browser. No build step is required.

## AWS Deployment Path

Start simple, then add cloud features:

1. Create an S3 bucket for static website assets.
2. Upload `index.html`, `styles.css`, and `resume.pdf`.
3. Put CloudFront in front of the bucket.
4. Request an ACM certificate for HTTPS.
5. Point a Route 53 domain or subdomain at CloudFront.
6. Add GitHub Actions to sync the site to S3 after each push.
7. Add a visitor counter with API Gateway, Lambda, and DynamoDB.
8. Add a contact form with API Gateway, Lambda, DynamoDB, and SES or SNS.
9. Convert the setup into Infrastructure as Code with Terraform, AWS CDK, or CloudFormation.

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
