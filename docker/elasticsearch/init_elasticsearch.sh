#!/bin/bash
until curl -s "http://elasticsearch:9200" > /dev/null; do
    echo "Waiting for Elasticsearch to start..."
    sleep 2
done

# Assegna i permessi di lettura al file mapping.json
echo "Setting read permissions for mapping.json..."
chmod a+r /app/elastic_mapping.json

echo "Creating index reddit-comments with mapping..."
curl -X PUT "http://elasticsearch:9200/reddit-comments" \
-H "Content-Type: application/json" \
-d @/app/elastic_mapping.json

echo "Creating index reddit-comments_custom with mapping..."
curl -X PUT "http://elasticsearch:9200/reddit-comments-custom" \
-H "Content-Type: application/json" \
-d @/app/elastic_mapping.json