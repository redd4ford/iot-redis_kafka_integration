import pyspark.sql.functions as spark_func
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
)
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import json
from datetime import datetime
from pprint import pprint

start_event_pos = {
    "offset": "-1",
    "seqNo": -1,
    "enqueuedTime": None,
    "isInclusive": True
}

end_event_pos = {
    "offset": None,
    "seqNo": -1,
    "enqueuedTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    "isInclusive": True
}

client = Elasticsearch(
    cloud_id="ELK_CLOUD_ID",
    basic_auth=(
        "elastic",
        "ELK_PASSWORD"
    )
)

client.info()

event_hub_connection_string = "EVENT_HUB_CONNECTION_STRING"
event_data = (
    spark.read
    .format("eventhubs")
    .options(
        **{
            'eventhubs.connectionString':
                sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(
                    event_hub_connection_string
                ),
            'eventhubs.startingPosition': json.dumps(start_event_pos),
            'eventhubs.endingPosition': json.dumps(end_event_pos),
        }
    )
    .load()
)

event_data = (
    event_data.withColumn("body", event_data["body"].cast("string"))
)
pprint(event_data["body"].cast("string"))

read_schema = StructType([
    StructField("site_num", StringType(), nullable=True),
    StructField("parameter_code", StringType(), nullable=True),
    StructField("datum", StringType(), nullable=True),
    StructField("parameter_name", StringType(), nullable=True),
    StructField("sample_duration", StringType(), nullable=True),
    StructField("metric_used", StringType(), nullable=True),
    StructField("year", StringType(), nullable=True),
    StructField("observation_count", StringType(), nullable=True),
    StructField("observation_percent", StringType(), nullable=True),
    StructField("arithmetic_mean", StringType(), nullable=True),
    StructField("county_name", StringType(), nullable=True),
    StructField("cbsa_name", StringType(), nullable=True),
    StructField("date_of_last_change", StringType(), nullable=True),
])

decoded_data = (
    event_data.select(
        spark_func.from_json(spark_func.col("body").cast("string"), read_schema).alias("df")
    )
)

sort_by = "year"

if sort_by == "year":
    sorted_query = decoded_data.sort(spark_func.year("df.year"))
else:
    sorted_query = decoded_data

result_as_json = (
    sorted_query.toJSON().map(lambda j: json.loads(j)).collect()
)
pprint(result_as_json)

for obj in result_as_json:
    bulk(
        client,
        [{"_index": "ELASTICSEARCH_INDEX_NAME", "_source": obj}]
    )
