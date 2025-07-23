import os

import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines


def cleanup_deployment():
    """Clean up any failed deployments."""
    load_dotenv()

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("Missing required environment variable: GOOGLE_CLOUD_STAGING_BUCKET")
        return

    # Initialize Vertex AI
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )

    try:
        # Try to get all deployments
        deployments = agent_engines.list()
        if deployments:
            print("Found deployments:")
            for deployment in deployments:
                print(f"Deleting deployment: {deployment.resource_name}")
                deployment.delete(force=True)
        else:
            print("No deployments found to clean up.")
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    cleanup_deployment()