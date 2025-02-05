# Used ports for localhost























# Postgres

Connect to database in the container
```shell
foo@bar:~$ echo "can use make shell-postgres command"
foo@bar:~$ echo "more commands inside cli here https://hasura.io/blog/top-psql-commands-and-flags-you-need-to-know-postgresql"
foo@bar:~$ docker exec -it postgres_database bash
# psql -h postgres_database -p 5432 -U postgres_user postgres_db
postgres# 
```

Create Postgres shell using Django + Makefile
```shell
foo@bar:~$ make database-shell
```

# Redis
## Get cli
```shell
	docker exec -it redis sh
	@echo "(or chortcut make redis-cli)"
	@echo "and then create cli"
	/data: redis-cli
```

## Common commands
```shell
	@echo "look here https://www.tutorialspoint.com/redis/hashes_hset.htm          -- really cool"
	@echo "look here https://www.digitalocean.com/community/cheatsheets/how-to-manage-replicas-and-clients-in-redis          -- really cool"
	@echo "look here https://www.youtube.com/watch?v=XCsS_NVAa1g          -- really cool"
	@echo "look here https://redis.io/docs/data-types/hashes/"
	@echo "look here https://realpython.com/python-redis/"
	# 127.0.0.1:6379> hello
	# 127.0.0.1:6379> keys *
	# 127.0.0.1:6379> keys *pattern*
	# 127.0.0.1:6379> keys a??
	# 127.0.0.1:6379> auth my-password       -->>     if not authenticated
	# 127.0.0.1:6379> config get maxmemory
	# 127.0.0.1:6379> setex mykey 60 "Hello world"
	# 127.0.0.1:6379> ttl mykey   -->> Returns the remaining time to live of a key that has a timeout.
	# 127.0.0.1:6379> keys *     -->> in this 60 sec
	# 127.0.0.1:6379> mget mykey     -->> in this 60 sec
	# 127.0.0.1:6379> del mykey
	# 127.0.0.1:6379> exists mykey
	# 127.0.0.1:6379> rename old_key new_key
	# 127.0.0.1:6379> type key_1
	# 127.0.0.1:6379> keys *     -->> after  60 sec
	# 127.0.0.1:6379> HSET bike:1 model Deimos brand Ergonom type 'Enduro bikes' price 4972     -->> like dict
	# 127.0.0.1:6379> HGET bike:1 model
	# 127.0.0.1:6379> HGETALL bike:1
	# 127.0.0.1:6379> dbsize     -->> returns the number of keys in the currently-selected database.
	# 127.0.0.1:6379> info     -->> returns information and statistics about the server in a format that is simple to parse by computers and easy to read by humans.
	# FLUSHDB : This command clears the current Redis database.
	# FLUSHALL : This command clears all databases in the Redis instance.
	# SAVE : Following example creates a backup of the current database. (into docker volume) https://www.tutorialspoint.com/redis/redis_backup.htm
	# 127.0.0.1:6379> set user:name Alex    -->> https://stackoverflow.com/questions/3554888/what-is-the-purpose-of-colons-within-redis-keys
	# 127.0.0.1:6379> set user:surname bush
	# 127.0.0.1:6379> get user  #(nil)
	# 127.0.0.1:6379> get user:name   -->> "Alex"
	# 127.0.0.1:6379> CONFIG GET databases
	# select 5  -->> 127.0.0.1:6379[5]>  number in square brackets        --->>> change db (must add to the redis-commander manually)
