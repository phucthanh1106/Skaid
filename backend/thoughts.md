always store the answer first to a redis key, and then publish the job id so that the subscriber 
receives the ID and retrieves the answer (if publish first the answer might not exist yet)