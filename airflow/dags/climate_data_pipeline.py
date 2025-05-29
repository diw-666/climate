from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.emr import EmrCreateJobFlowOperator
from airflow.providers.amazon.aws.sensors.emr import EmrJobFlowSensor
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
from airflow.providers.amazon.aws.operators.redshift import RedshiftSQLOperator
from airflow.models import Variable

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'climate_data_pipeline',
    default_args=default_args,
    description='Process Sri Lankan climate data',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

# EMR cluster configuration
emr_config = {
    'Name': 'Climate-Data-Processing',
    'ReleaseLabel': 'emr-6.15.0',
    'Applications': [
        {'Name': 'Spark'},
        {'Name': 'Hadoop'}
    ],
    'Instances': {
        'InstanceGroups': [
            {
                'Name': 'Master nodes',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'MASTER',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1,
            },
            {
                'Name': 'Worker nodes',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'CORE',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 2,
            }
        ],
        'KeepJobFlowAliveWhenNoSteps': False,
        'TerminationProtected': False,
    },
    'Steps': [],
    'VisibleToAllUsers': True,
    'JobFlowRole': 'EMR_EC2_DefaultRole',
    'ServiceRole': 'EMR_DefaultRole',
}

# Create EMR cluster
create_emr_cluster = EmrCreateJobFlowOperator(
    task_id='create_emr_cluster',
    job_flow_overrides=emr_config,
    aws_conn_id='aws_default',
    dag=dag,
)

# Wait for EMR cluster to be ready
wait_for_emr_cluster = EmrJobFlowSensor(
    task_id='wait_for_emr_cluster',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag,
)

# Add Spark step to EMR
spark_step = {
    'Name': 'Process Climate Data',
    'ActionOnFailure': 'CONTINUE',
    'HadoopJarStep': {
        'Jar': 'command-runner.jar',
        'Args': [
            'spark-submit',
            '--deploy-mode', 'cluster',
            's3://{{ var.value.spark_scripts_bucket }}/process_climate_data.py',
            '--input', 's3://{{ var.value.raw_bucket }}/raw/',
            '--output', 's3://{{ var.value.processed_bucket }}/processed/'
        ]
    }
}

add_spark_step = EmrAddStepsOperator(
    task_id='add_spark_step',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
    steps=[spark_step],
    aws_conn_id='aws_default',
    dag=dag,
)

# Wait for Spark step to complete
wait_for_spark_step = EmrStepSensor(
    task_id='wait_for_spark_step',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull(task_ids='add_spark_step', key='return_value')[0] }}",
    aws_conn_id='aws_default',
    dag=dag,
)

# Load data into Redshift
load_to_redshift = RedshiftSQLOperator(
    task_id='load_to_redshift',
    sql="""
    COPY climate_data
    FROM 's3://{{ var.value.processed_bucket }}/processed/'
    IAM_ROLE '{{ var.value.redshift_role_arn }}'
    CSV
    IGNOREHEADER 1
    DELIMITER ',';
    """,
    redshift_conn_id='redshift_default',
    dag=dag,
)

# Set task dependencies
create_emr_cluster >> wait_for_emr_cluster >> add_spark_step >> wait_for_spark_step >> load_to_redshift 