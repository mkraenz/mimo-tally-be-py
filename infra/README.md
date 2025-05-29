# Infrastructure

## Push docker image to GCP Artifact Registry

[Quickstart guide](https://cloud.google.com/artifact-registry/docs/docker/store-docker-container-images)

```sh
LOCAL_IMAGE_IDENTIFIER='backend:latest'
PROJECT='mimo-tally-2025'
REGION='europe-west1'
REPO_ID='mimo-tally-repo'
IMAGE_NAME='mimo-tally-py-backend'
TAG='latest'

# tag local image
# Q: Why inclued the registry in the tag? A: Tagging the Docker image with a repository name configures the docker push command to push the image to a specific location.
docker tag ${LOCAL_IMAGE_IDENTIFIER} \
${REGION}-docker.pkg.dev/${PROJECT}/${REPO_ID}/${IMAGE_NAME}:${TAG}

# then push
docker push ${REGION}-docker.pkg.dev/${PROJECT}/${REPO_ID}/${IMAGE_NAME}:${TAG}
```

## Deployment

Make sure you have all vars defined in, for example, `staging.auto.tfvars`. Then

```sh
tf apply
```
