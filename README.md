# Sri Lankan Climate Data Pipeline

This project implements an end-to-end data pipeline for processing Sri Lankan climate data using AWS services.

## Architecture

```
[Sri Lankan Climate CSV Files]
           ↓
    Upload to AWS S3 (Raw Zone)
           ↓
     Airflow (MWAA) DAG triggers
           ↓
  Spark (EMR) processes raw data
           ↓
    Save to S3 (Processed Zone)
           ↓
         dbt models
           ↓
     Load to Amazon Redshift
           ↓
     Power BI Dashboards
```

## Project Structure

```
.
├── airflow/
│   └── dags/
│       └── climate_data_pipeline.py
├── spark/
│   └── jobs/
│       └── process_climate_data.py
├── dbt/
│   ├── models/
│   └── dbt_project.yml
├── scripts/
│   ├── upload_to_s3.py
│   └── generate_fernet_key.py
├── Dockerfile.upload
├── Dockerfile.spark
├── Dockerfile.dbt
├── docker-compose.yml
└── requirements.txt
```

## Docker Setup

1. Generate Airflow Fernet key:
   ```bash
   python scripts/generate_fernet_key.py
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with your AWS credentials and the generated Fernet key.

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. Access services:
   - Airflow UI: http://localhost:8080
   - Default credentials: airflow/airflow

## Manual Setup (Alternative)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure AWS credentials:
   - Set up AWS credentials in `~/.aws/credentials`
   - Configure environment variables in `.env` file

3. Deploy Airflow DAG to MWAA:
   - Copy DAG file to MWAA S3 bucket
   - Configure MWAA environment variables

4. Set up EMR cluster:
   - Configure EMR cluster with Spark
   - Set up necessary IAM roles and permissions

5. Configure Redshift:
   - Create Redshift cluster
   - Set up database schema
   - Configure dbt connection

## Environment Variables

Create a `.env` file with the following variables:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
S3_RAW_BUCKET=climate-raw-data
S3_PROCESSED_BUCKET=climate-processed-data
REDSHIFT_HOST=your_redshift_endpoint
REDSHIFT_DATABASE=climate_db
REDSHIFT_USER=your_username
REDSHIFT_PASSWORD=your_password
AIRFLOW__CORE__FERNET_KEY=your_generated_fernet_key
```

## Usage

1. Upload raw data:
   ```bash
   # Using Docker
   docker-compose run data-uploader

   # Or manually
   python scripts/upload_to_s3.py
   ```

2. Monitor pipeline:
   - Access Airflow UI to monitor DAG execution
   - Check EMR cluster status
   - Monitor Redshift data loading

3. Access Power BI:
   - Connect Power BI to Redshift
   - Create visualizations and dashboards

## Docker Services

- `airflow-webserver`: Airflow web interface
- `airflow-scheduler`: Airflow scheduler
- `postgres`: PostgreSQL database for Airflow
- `data-uploader`: Service for uploading data to S3
- `dbt-runner`: Service for running dbt models 