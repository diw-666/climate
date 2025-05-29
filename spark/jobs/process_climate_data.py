from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create and return a Spark session."""
    return SparkSession.builder \
        .appName("Climate Data Processing") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .getOrCreate()

def process_climate_data(spark, input_path, output_path):
    """Process climate data files and save the results."""
    try:
        # Read all CSV files from input path
        df = spark.read.csv(
            input_path,
            header=True,
            inferSchema=True
        )

        # Clean and transform data
        processed_df = df \
            .withColumn("timestamp", to_timestamp("timestamp")) \
            .withColumn("year", year("timestamp")) \
            .withColumn("month", month("timestamp")) \
            .withColumn("day", dayofmonth("timestamp")) \
            .dropDuplicates(["timestamp", "station_id"]) \
            .na.fill(0)  # Fill null values with 0

        # Calculate daily statistics
        daily_stats = processed_df \
            .groupBy("station_id", "year", "month", "day") \
            .agg(
                avg("temperature").alias("avg_temperature"),
                max("temperature").alias("max_temperature"),
                min("temperature").alias("min_temperature"),
                avg("humidity").alias("avg_humidity"),
                avg("rainfall").alias("total_rainfall"),
                avg("wind_speed").alias("avg_wind_speed")
            )

        # Write processed data
        daily_stats.write \
            .mode("overwrite") \
            .partitionBy("year", "month") \
            .parquet(output_path)

        logger.info(f"Successfully processed data and saved to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Process climate data using Spark')
    parser.add_argument('--input', required=True, help='Input path for raw data')
    parser.add_argument('--output', required=True, help='Output path for processed data')
    
    args = parser.parse_args()
    
    spark = create_spark_session()
    
    try:
        process_climate_data(spark, args.input, args.output)
    finally:
        spark.stop()

if __name__ == "__main__":
    main() 