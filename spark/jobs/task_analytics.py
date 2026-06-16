from __future__ import annotations

import os
import time
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    BooleanType,
    DoubleType,
    IntegerType,
    StructField,
    StructType,
    TimestampType,
)


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


DATABASE_HOST = env("DATABASE_HOST", "opengauss")
DATABASE_PORT = env("DATABASE_PORT", "5432")
DATABASE_NAME = env("DATABASE_NAME", "postgres")
DATABASE_USER = env("DATABASE_USER", "gaussdb")
DATABASE_PASSWORD = env("DATABASE_PASSWORD", "Gauss@2026")
MAX_ATTEMPTS = int(env("SPARK_DB_MAX_ATTEMPTS", "30"))

JDBC_URL = (
    f"jdbc:postgresql://{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    "?sslmode=disable"
)

JDBC_PROPERTIES = {
    "user": DATABASE_USER,
    "password": DATABASE_PASSWORD,
    "driver": "org.postgresql.Driver",
}


ANALYTICS_SCHEMA = StructType(
    [
        StructField("available", BooleanType(), nullable=False),
        StructField("generated_at", TimestampType(), nullable=False),
        StructField("total_tasks", IntegerType(), nullable=False),
        StructField("done_tasks", IntegerType(), nullable=False),
        StructField("running_tasks", IntegerType(), nullable=False),
        StructField("overdue_tasks", IntegerType(), nullable=False),
        StructField("high_priority_open_tasks", IntegerType(), nullable=False),
        StructField("completion_rate", DoubleType(), nullable=False),
    ]
)


def read_tasks_with_retry(spark: SparkSession):
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return spark.read.jdbc(
                url=JDBC_URL,
                table="cloud_tasks",
                properties=JDBC_PROPERTIES,
            )
        except Exception as exc:
            last_error = exc
            print(
                f"Waiting for openGauss before Spark analytics "
                f"({attempt}/{MAX_ATTEMPTS}): {exc}",
                flush=True,
            )
            time.sleep(min(2.0, 0.25 * attempt))
    raise RuntimeError(f"Spark could not read cloud_tasks: {last_error}") from last_error


def main() -> None:
    spark = (
        SparkSession.builder.appName("GaussOps Spark Task Analytics")
        .config("spark.sql.session.timeZone", "Asia/Shanghai")
        .getOrCreate()
    )

    try:
        tasks = read_tasks_with_retry(spark)
        today = F.current_date()
        summary = tasks.agg(
            F.count("*").cast("int").alias("total_tasks"),
            F.sum(F.when(F.col("status") == "done", 1).otherwise(0))
            .cast("int")
            .alias("done_tasks"),
            F.sum(F.when(F.col("status") == "running", 1).otherwise(0))
            .cast("int")
            .alias("running_tasks"),
            F.sum(
                F.when(
                    (F.col("due_date") < today) & (F.col("status") != "done"),
                    1,
                ).otherwise(0)
            )
            .cast("int")
            .alias("overdue_tasks"),
            F.sum(
                F.when(
                    (F.col("priority") == "high") & (F.col("status") != "done"),
                    1,
                ).otherwise(0)
            )
            .cast("int")
            .alias("high_priority_open_tasks"),
        )

        row = summary.collect()[0].asDict()
        total_tasks = int(row["total_tasks"] or 0)
        done_tasks = int(row["done_tasks"] or 0)
        completion_rate = float(done_tasks / total_tasks) if total_tasks else 0.0

        analytics = spark.createDataFrame(
            [
                (
                    True,
                    datetime.now(),
                    total_tasks,
                    done_tasks,
                    int(row["running_tasks"] or 0),
                    int(row["overdue_tasks"] or 0),
                    int(row["high_priority_open_tasks"] or 0),
                    completion_rate,
                )
            ],
            schema=ANALYTICS_SCHEMA,
        )

        analytics.write.jdbc(
            url=JDBC_URL,
            table="spark_task_analytics",
            mode="append",
            properties=JDBC_PROPERTIES,
        )

        print(
            "Spark analytics written to openGauss: "
            f"total={total_tasks}, done={done_tasks}, "
            f"completion_rate={completion_rate:.4f}",
            flush=True,
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
