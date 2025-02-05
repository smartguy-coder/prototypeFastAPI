# Used ports for localhost

| Service             | Opened port | Inner Docker port |                          Notes                           |
|:--------------------|:-----------:|:-----------------:|:--------------------------------------------------------:|
| Nginx               |     80      |        80         |             you can go directly to 127.0.0.1             |
| main api server     |    9000     |       9000        |                            -                             |
| Postgres            |    5432     |       5432        |                            -                             |
| PgAdmin             |    5050     |        80         | to connect to Postgres use "postgres_database" host name |
| Documentation       |    8010     |       8010        |                            -                             |
| Redis               |    6379     |       6379        |                                                          |
| GUI Redis commander |    8081     |       8081        |                      quite popular                       |
| GUI Redis insight   |    5540     |       5540        |                 with interesting metrics                 |
| Celery Flower       |    5555     |       5555        |                                                          |
 
:memo: go to /etc/hosts on Linux, MacOS or C:/Windows/System32/Drivers/etc/ on Windows 
and set in bottom of the file *hosts*
```
127.0.0.1  your.domain
```

now toy can go in a browser by name, not host
read more -> [how set domain on local PC](https://hostiq.ua/wiki/ukr/hosts/) 

