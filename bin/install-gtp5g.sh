#!/bin/bash

# Define variables for clarity and easy updates
BUILD_DIR="../build"
GTP5G_REPO="https://github.com/free5gc/gtp5g.git"
GTP5G_BRANCH="v0.8.2"

if [ ! -d "$BUILD_DIR" ]; then
  mkdir -p "$BUILD_DIR"
fi

# Change to the build directory
cd "$BUILD_DIR" || exit 1 

if [ ! -d "gtp5g" ]; then
  git clone -b "$GTP5G_BRANCH" "$GTP5G_REPO"
  cd "gtp5g" || exit 1 
else
  echo "gtp5g directory already exists, skipping clone..."
  cd "gtp5g" || exit 1  # Ensure we're in the right directory
  git fetch --tags
  git checkout "$GTP5G_BRANCH" || exit 1  # Ensure the correct branch is checked out
fi

# Compile the gtp5g module
make || echo "Error: Failed to compile gtp5g."

# Install the gtp5g module
sudo make install || echo "Error: Failed to install gtp5g."

# Display module information
modinfo gtp5g || echo "Error: Failed to display modinfo for gtp5g."



