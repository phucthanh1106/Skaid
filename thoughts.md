always store the answer first to a redis key, and then publish the job id so that the subscriber 
receives the ID and retrieves the answer (if publish first the answer might not exist yet)

The backend has two roles: RQ producer when sending work, and Pub/Sub subscriber when listening for completed answers

Pub/sub is for avoid polling since we will know the exact moment to call redis.get(redis_key) (when notification arrives)