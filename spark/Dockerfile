FROM apache/spark:3.5.4

USER root

ARG POSTGRES_JDBC_VERSION=42.7.4

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fL "https://jdbc.postgresql.org/download/postgresql-${POSTGRES_JDBC_VERSION}.jar" \
      -o /opt/spark/jars/postgresql-${POSTGRES_JDBC_VERSION}.jar

WORKDIR /app

COPY jobs ./jobs

CMD ["/opt/spark/bin/spark-submit", "--master", "local[*]", "/app/jobs/task_analytics.py"]
