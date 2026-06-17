FROM apache/spark:3.5.4

USER root

ARG POSTGRES_JDBC_VERSION=42.7.4

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fL "https://jdbc.postgresql.org/download/postgresql-${POSTGRES_JDBC_VERSION}.jar" \
      -o /opt/spark/jars/postgresql-${POSTGRES_JDBC_VERSION}.jar

WORKDIR /app

RUN mkdir -p /tmp/spark-events && chmod 1777 /tmp/spark-events

COPY jobs ./jobs

EXPOSE 4040 7077 8080 8081 18080

CMD ["/opt/spark/bin/spark-submit", "--master", "spark://spark-master:7077", "--conf", "spark.ui.enabled=true", "--conf", "spark.ui.port=4040", "--conf", "spark.ui.bindAddress=0.0.0.0", "--conf", "spark.driver.host=spark-analytics", "--conf", "spark.driver.bindAddress=0.0.0.0", "--conf", "spark.eventLog.enabled=true", "--conf", "spark.eventLog.dir=file:/tmp/spark-events", "/app/jobs/task_analytics.py"]
