#!/bin/bash

# Set variables
CONTAINER_NAME="llama-agent"
TAR_NAME="llama-agent.tar"
APP_NAME="llama-agent"

# Build the container
echo "Building container..."
docker build -t $CONTAINER_NAME .

# Save the container as a tar file
echo "Creating tar file..."
docker save -o $TAR_NAME $CONTAINER_NAME

# Create the IOx package structure
echo "Creating IOx package..."
mkdir -p package/artifacts
mv $TAR_NAME package/artifacts/

# Create the final IOx package
tar czf ${APP_NAME}.tar.gz -C package .

echo "Done! Created ${APP_NAME}.tar.gz ready for deployment to IOS-XE" 