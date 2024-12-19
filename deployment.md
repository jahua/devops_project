# Docker and Google Cloud Deployment Guide for Beginners

This guide explains step-by-step how to containerize and deploy our FastAPI UNO game application using Docker and Google Cloud Run.

## Prerequisites

Before starting, ensure you have:
1. Docker Desktop installed and running
2. Google Cloud SDK installed
3. A Google Cloud account
4. Git installed
5. Our project repository cloned locally

## Step 1: Understanding the Dockerfile

First, let's understand what's in our `Dockerfile`:
```dockerfile
FROM python:3.11-slim         # Base image with Python 3.11
WORKDIR /code                 # Sets working directory in container
COPY ./requirements.txt /code/requirements.txt   # Copies requirements
RUN pip install --no-cache-dir -r /code/requirements.txt  # Installs dependencies
COPY ./server /code/server    # Copies our application code
EXPOSE 8080                   # Declares the port our app uses
CMD ["uvicorn", "server.py.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Step 2: Building the Docker Image

```bash
docker build -t uno_team12_image .
```

Breaking down this command:
- `docker build`: Command to create a Docker image
- `-t uno_team12_image`: Tags our UNO game image as "uno_team12_image"
- `.`: Tells Docker to look for `Dockerfile` in current directory

After running this command:
1. Docker reads our Dockerfile
2. Downloads the Python base image
3. Executes each instruction to create our image
4. Stores the image locally (verify with `docker images`)

## Step 3: Running the Docker Container Locally

```bash
docker run -d --name uno_team12_container -p 888:8080 uno_team12_image
```

Breaking down this command:
- `docker run`: Creates and starts a container
- `-d`: Runs in detached mode (background)
- `--name uno_team12_container`: Names our UNO game container
- `-p 888:8080`: Port mapping
  - `888`: Port on your computer
  - `8080`: Port inside container (matches EXPOSE in Dockerfile)
- `uno_team12_image`: The image name from Step 2

Verify it's running:
```bash
docker ps  # Lists running containers
```

Test the application at: `http://localhost:888`

## Step 4: Google Cloud Setup and Configuration

1. **Install Google Cloud SDK**
   - Download from: https://cloud.google.com/sdk/docs/install
   - Run the installer and follow the prompts

2. **Initialize Google Cloud:**
   ```bash
   # Login to your Google account
   gcloud auth login

   # Create a new project (in our case, our project was already created so skip this step)
   gcloud projects create devops-team-12-597759

   # Set the project as active (the project name was provided in the google sheet by the professor)
   gcloud config set project devops-team-12-597759

   # Enable required APIs (these are previously enabled for our project so skip this step)
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

3. **Configure Docker Authentication:**
   ```bash
   # Configure Docker to use Google Cloud (this was preconfigured so skip this step)
   gcloud auth configure-docker europe-west6-docker.pkg.dev
   ```

## Step 5: Deploying to Google Cloud Run

```bash
# can be done without the --region flag and then the region can be set when prompted in the terminal, we type 22.
gcloud run deploy uno-team12 --port 8080 --source . --allow-unauthenticated --region europe-west6
```

Breaking down this command:
- `gcloud run deploy`: Command to deploy to Cloud Run
- `uno-team12`: Our service name
  - Creates URL: `https://uno-team12-xxxx-xx.run.app`
- `--port 8080`: Port our FastAPI app listens on
- `--source .`: Uses current directory (with Dockerfile)
- `--allow-unauthenticated`: Makes our game publicly accessible
- `--region europe-west6`: Deploys to Zurich region

Deployment Process:
1. Code is uploaded to Google Cloud
2. Cloud Build creates container image
3. Image is deployed as a Cloud Run service
4. You receive a deployment URL

## Step 6: Post-Deployment Verification

1. **Test the Deployment:**
   - Open the provided URL in your browser
   - Test the UNO game API endpoints
   - Verify WebSocket connections work

2. **Monitor the Service:**
   ```bash
   # View service details
   gcloud run services describe uno-team12

   # View deployment logs
   gcloud run services logs read uno-team12
   ```

## Common Docker Commands

```bash
# List all images
docker images

# List running containers
docker ps

# Stop the UNO game container
docker stop uno_team12_container

# Remove the container
docker rm uno_team12_container

# Remove the image
docker rmi uno_team12_image
```

## Troubleshooting

1. **Docker Issues:**
   - If build fails:
     - Check if Dockerfile exists
     - Verify requirements.txt is present
     - Check Python version compatibility
   - If container won't start:
     - Port 888 might be in use (change port)
     - Check logs: `docker logs uno_team12_container`

2. **Google Cloud Issues:**
   - If deployment fails:
     - Verify Google Cloud SDK installation
     - Check authentication: `gcloud auth list`
     - Ensure billing is enabled
     - Check project permissions
   - If service is unreachable:
     - Verify deployment status: `gcloud run services describe uno-team12`
     - Check logs: `gcloud run services logs read uno-team12`

3. **Application-Specific Issues:**
   - If WebSocket connections fail:
     - Ensure Cloud Run service allows WebSocket connections
     - Check client connection URLs
   - If game features don't work:
     - Verify environment variables
     - Check application logs

## Cleanup Resources

When you're done testing:

```bash
# Stop and remove local container
docker stop uno_team12_container
docker rm uno_team12_container

# Delete Cloud Run service
gcloud run services delete uno-team12 --region europe-west6

# Optional: Delete entire project
gcloud projects delete uno-team12-project
