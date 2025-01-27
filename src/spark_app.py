from transformers import pipeline
import pandas as pd
from pyspark.sql.functions import col, explode, from_json
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, IntegerType, TimestampType
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
import requests
import json, os, time

API_URL = os.getenv("API_URL")
headers = json.loads(os.getenv("headers"))

spark = SparkSession.builder \
    .appName("RedditPostAnalysis") \
    .getOrCreate()

def analyze_sentiment_udf(comment_body_series: pd.Series) -> pd.Series:

    print("Input to analyze_sentiment_udf:")
    print(comment_body_series)

    sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    results = sentiment_analyzer(comment_body_series.str[:512].tolist())

    print("Output from analyze_sentiment_udf:")
    print(results)

    return pd.Series([result["label"] for result in results])

def categorize_comment_udf(comment_body_series: pd.Series) -> pd.Series:
    batch_size = 15
    max_retries = 15  # Number of retries for failed batches
    results = []

    for i in range(0, len(comment_body_series), batch_size):
        batch = comment_body_series[i:i + batch_size]
        success = False

        for attempt in range(max_retries):
            try:
                payload = {
                    "inputs": batch.tolist(),
                    "parameters": {"candidate_labels": ["gameplay", "graphics", "story", "music", "criticism"]}
                }
                print(f"Payload being sent: {payload}")  # Log the payload
                response = requests.post(API_URL, headers=headers, json=payload)
                response.raise_for_status()  # Raise exception for HTTP errors
                response_json = response.json()
                print(f"Response JSON for batch {i // batch_size + 1}: {response_json}")  # Log the response

                # Process results and break out of the retry loop on success
                results.extend([
                    [label for label, score in zip(result['labels'], result['scores']) if score > 0.4]
                    or ["generic"]
                    for result in response_json
                ])
                success = True
                break  # Exit retry loop if successful

            except requests.exceptions.HTTPError as e:
                if response.status_code == 503:  # Retry for 503 errors
                    print(f"503 Error on attempt {attempt + 1} for batch {i // batch_size + 1}: Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"HTTPError on batch {i // batch_size + 1}: {e}")
                    break  # Exit retry loop for non-retriable errors

            except Exception as e:
                print(f"Error processing batch {i // batch_size + 1} on attempt {attempt + 1}: {e}")
                break  # Exit retry loop for other exceptions

        # Handle cases where all retries failed
        if not success:
            print(f"All retries failed for batch {i // batch_size + 1}.")
            results.extend([["retry_failed"]] * len(batch))  # Avoid sending "error" data

    return pd.Series(results)

analyze_sentiment = F.pandas_udf(analyze_sentiment_udf, returnType=StringType())
categorize_comment = F.pandas_udf(categorize_comment_udf, returnType=ArrayType(StringType()))

kafka_df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "posts_raw") \
    .option("startingOffsets", "latest") \
    .load()

schema = StructType([
    StructField("post_id", StringType(), True),
    StructField("post_title", StringType(), True),
    StructField("post_body", StringType(), True),
    StructField("comments", ArrayType(StructType([
        StructField("comment_id", StringType(), True),
        StructField("comment_body", StringType(), True),
        StructField("comment_score", IntegerType(), True),
        StructField("comment_publish_time", TimestampType(), True)
    ])), True),
    StructField("post_publish_time", TimestampType(), True),
    StructField("@timestamp", TimestampType(), True)
])

decoded_df = kafka_df.select(from_json(col("value").cast("string"), schema).alias("data"))

comments_df = decoded_df.withColumn("comment", explode(col("data.comments")))

comments_df = comments_df.select(
    col("data.post_id"),
    col("data.post_title"),
    col("comment.comment_id").alias("comment_id"),
    col("comment.comment_body").alias("comment_body"),
    col("comment.comment_score").alias("comment_score"),
    col("comment.comment_publish_time").alias("comment_publish_time"),
    col("data.post_publish_time").alias("post_publish_time"),
    col("data.@timestamp")
)

comments_df = comments_df.withColumn("sentiment", analyze_sentiment(col("comment_body")))
comments_df = comments_df.withColumn("categories", categorize_comment(col("comment_body")))

query = comments_df.writeStream \
    .outputMode("append") \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch") \
    .option("es.port", "9200") \
    .option("es.resource", "reddit-comments") \
    .option("checkpointLocation", "/tmp/checkpoint_es") \
    .start()

query.awaitTermination()
