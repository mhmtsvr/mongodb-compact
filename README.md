# MongoDB Compact

MongoDB Compact is a Docker-based tool designed to facilitate the compaction of MongoDB databases. Compaction is a crucial maintenance operation for MongoDB instances, helping to reclaim unused space and optimize database performance. Over time, as documents are added, updated, or deleted, MongoDB's storage files (WiredTiger or MMAPv1) can become fragmented. This fragmentation may lead to inefficient disk space usage and slower data access speeds. By compacting the database, MongoDB Compact aims to reduce this fragmentation, ensuring more efficient disk space usage and potentially improving query performance.

MongoDB Compact streamlines and automates database compaction in microservices architectures using Kubernetes, enabling scheduled, hands-free maintenance.

🚨 Please use this cron job at your own risk and thoroughly test it before deployment.

💾 It is highly recommended to have a backup before proceeding with compacting.

### Key Benefits

- **Docker Integration**: MongoDB Compact is containerized, making it easy to deploy and run in any environment that supports Docker, including Kubernetes.
- **Automated Compaction**: Designed to be run as a cron job, facilitating regular and automated compaction processes.
- **Easy Configuration**: Configurable through environment variables, allowing for easy integration with your MongoDB deployment.
- **Node Stability**: Compaction only proceeds when the previously compacted node is in a stable state.

## How to deploy in Kubernetes

1. Deploy mongodb-compact cronjob
    ```
    kubectl apply -k k8s
    ```
2. Create a job out of the cronjob
    ```
    kubectl create job --from=cronjob/mongodb-compact mongodb-compact-job
    ```
3. Check the logs
    ```
    kubectl logs -l name=mongodb-compact -f
    ```

## Docker (Optional)

To customize the script and create your own image, follow these steps:

1. Make sure that you have [Docker](https://docs.docker.com/engine/install/) and [kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize/) installed in your local.
2. Build the Docker image locally using the Dockerfile in the current directory.
    ```
    docker build -t mongodb-compact .
    ```
3. Tag the built image with your Docker Hub username and version.
    ```
    docker tag mongodb-compact {YOUR_DOCKERHUB_USERNAME}/mongodb-compact:1.0.0
    ```
4. Push the tagged image to your Docker Hub repository.
    ```
    docker push {YOUR_DOCKERHUB_USERNAME}/mongodb-compact:1.0.0
    ```
5. Update the Kubernetes Kustomize configuration to use the new image version.
    ```
    cd k8s && kustomize edit set image {YOUR_DOCKERHUB_USERNAME}/mongodb-compact:1.0.0
    ```
6. Deploy the cronjob, see [here](./README.md#how-to-deploy-in-kubernetes)