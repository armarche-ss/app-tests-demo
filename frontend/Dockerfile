# =============================================================================
# frontend/Dockerfile — Serves the static frontend via nginx
#
# This is a minimal image: we take the official nginx image and just:
#   1. Replace its default config with ours
#   2. Copy the static HTML/JS/CSS files into the right directory
#
# The result is a tiny, fast container that serves the UI and proxies
# API calls to the api container on the internal Docker network.
# =============================================================================

FROM nginx:1.25-alpine

# Replace the default nginx config with our custom one
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static frontend files into nginx's web root
COPY index.html /usr/share/nginx/html/index.html

# Document that this container listens on port 80
EXPOSE 80
