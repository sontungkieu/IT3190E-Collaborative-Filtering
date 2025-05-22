# Hybrid Recommendation System Prototype

## Introduction

E‑commerce businesses of all sizes rely on personalized product recommendations to enhance user experience and boost sales. While large platforms often have dedicated teams to build sophisticated algorithms, smaller enterprises may lack such resources, leading to suboptimal customer engagement. Our project implements a scalable, microservices‑based recommendation system prototype inspired by leading sites like GearVN and Cellphones. We leverage modern MLOps practices to automate training, deployment, and monitoring, and evaluate state‑of‑the‑art algorithms to maximize recommendation quality.

## Features

* **Microservices Architecture**: Five independent services (product, recommendation, review, user, UI) orchestrated with Docker Compose and Kubernetes.
* **Hybrid Algorithms**: Matrix Factorization, SBERT‑driven CB+CF, LightFM hybrid, UltraGCN.
* **MLOps Pipeline**: End‑to‑end automation with MongoDB → Debezium → Airflow → Feast → W\&B → GCR → GKE → ArgoCD → Prometheus/Grafana.
* **Evaluation Metrics**: Precision\@K, Recall\@K, NDCG\@K, MAP\@K, MRR, RMSE.
* **CI/CD & GitOps**: GitHub Actions for testing/building, ArgoCD for automated deployments.

## Repository Structure

```
├── docker-compose.yml       # Local orchestration
├── services/                # Microservice modules
│   ├── product/
│   ├── recommendation/
│   ├── review/
│   ├── user/
│   └── ui/
├── mlops/                   # Airflow DAGs, Feast configs
├── charts/                  # Helm charts for Kubernetes
├── setup_kaggle_data.sh     # Data download & preprocess script
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Getting Started

### Prerequisites

* Docker & Docker Compose
* Kubernetes cluster (GKE recommended)
* GitHub account with permissions for GitOps

### Local Setup

```bash
# Clone the repo
git clone https://github.com/your-org/hybrid-recommender.git
cd hybrid-recommender

# Download and preprocess data
bash setup_kaggle_data.sh

# Start services
docker-compose up --build
```

## MLOps Pipeline Overview

1. **Data Ingestion**: MongoDB captures interactions; Debezium streams changes to Pub/Sub.
2. **Feature Store**: Feast materializes user/item embeddings daily.
3. **Model Training**: Airflow DAGs train CF and CB jobs, logging to Weights & Biases.
4. **CI/CD & Deployment**: GitHub Actions build/push Docker images; ArgoCD syncs to GKE.
5. **Serving & Monitoring**: KServe endpoints, Prometheus/Grafana dashboards, EvidentlyAI for drift detection.

## Authors

* Nguyen Phu An (20235466)
* Pham Chi Bang (20235477)
* Pham Van Vu Hoan (20235497)
* Nguyen Ngoc Minh (20235533)
* Kieu Son Tung (20235571)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
