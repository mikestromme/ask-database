# start postgres instance
docker compose up -d

# Wait for Postgres to be ready
while ! docker exec -it postgres-demo-instance pg_isready -U postgres; do sleep 1; done

# Copy the schema and data files to the container
docker cp ./schema.sql postgres-demo-instance:/home
docker cp ./data.sql postgres-demo-instance:/home

# Load the dataset into the database
docker exec -it postgres-demo-instance psql -U postgres -c '\i /home/schema.sql'
docker exec -it postgres-demo-instance psql -U postgres -c '\i /home/data.sql'