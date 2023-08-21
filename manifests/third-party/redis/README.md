# Redis

Chatbot use redis to persist messages and conversation entities.

We choose [redis-stack](https://hub.docker.com/r/redis/redis-stack) as the redis image, as we may leverage the similarity-search in the future.

This deployment runs a single instance with a volume mounted to persist data.
