# Infrastructure

## Overview

- no ci/cd pipeline yet
- push image of local backend service to GCP Artifact registry
- manage GCP infra with Terraform
- remote database running on Railway.app
- manual database migrations from local machine using alembic
- manual redeploys on image changes needed

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

## Database

Currently deployed by hand on Railway.app. [Project](https://railway.com/project/944271c2-6983-4df6-b688-d0022a8c2656?environmentId=e42e3b41-d1bd-4b45-a581-b3e457776137). Reason being simplicity and the limited time I had.

TODO put this under terraform control, or better, move the DB to GCP (and do it with terraform).

## Migrations

I have yet to set up a CI/CD pipeline for this project. Currently I am running the respective migration commands from my local machine - using local code. Obviously, not ideal but its quick to get started.

```sh
# First, make sure are on the latest main branch.
# Second, set up your .env file to point to the remote database
cd backend
alembic history
# double check you see the **local** migrations files you want to have on the server, then
alembic upgrade head
```

## Manual redeploys

Pushing a new docker image to GCP Artifact Registry does not auto-trigger Cloud Run to deploy a new version. Neither does running `tf apply` if there are no config changes.

Instead, manually hop into the [project on GCP](https://console.cloud.google.com/run/detail/europe-west1/cloudrun-service/metrics?inv=1&invt=AbzBFw&project=mimo-tally-2025&supportedpurview=project,folder) and click the `Edit & deploy revision` button, then hit `Deploy`.
