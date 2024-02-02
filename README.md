# Overview

---
This application is able to parse a dataset by link to a **.json file**, and either print the data to the console, or batch send it to **Azure Event Hub** (aka Kafka). It will also store the dataset as a file locally/in Docker Volume.

The app has integration with **Redis** to store file processing status. Status will be updated:
* when the file processing has just started,
* if the data sent as batches, at the end of each batch,
* at the end of the file processing,
* if the file was already processed.

### Data Batching

The application has a smarter batching algorithm implemented (at least I think it is smarter).

Before sending the data to Azure Event Hub, the app will check your default batching for the downloaded dataset (see **settings/BATCH_SIZE**) and calculate the estimated size of batches. 

If the batch size is greater than the limit dictated by the subscription (see `settings/MAX_BATCH_SIZE_IN_BYTES`), it means that the application could drop, because the size of the batch is not suitable for your Azure subscription. 

So, if needed, the algorithm will re-calculate the optimal batch size and split the dataset with the new batching strategy.


### Usage

**Use Swagger endpoint:** http://127.0.0.1:8000/schema/swagger-ui/#/api/api_dataset_processor_load_retrieve

**Or ```curl```:**
```
curl -X 'GET' \
  'http://127.0.0.1:8000/api/dataset-processor/load/?ignore_status=false&link=https%3A%2F%2Fopendata.utah.gov%2Fresource%2Fs9t3-bccv.json' \
  -H 'accept: application/json'
```

**Available parameters:**
* ```ignore_status``` (bool) - process the file again even if it was processed before (ignore "Already processed" status)
* ```link``` (string) - URL to the .json file. Uses this dataset by default: https://opendata.utah.gov/resource/s9t3-bccv.json

You can run the app manually or with Docker.
# Setup

---
### Manual:
* create a ```.env``` in ```django_app/``` directory based on ```.env.example```
  * Django app secret (`SECRET_KEY`) can be generated using the following approach:
    ```shell
    $ python manage.py shell
    from django.core.management.utils import get_random_secret_key
    get_random_secret_key()
    ```
  * Default dataset link (`DEFAULT_DATASET`) can stay intact, this is just an example link that will be displayed in Swagger.
  * To get Azure Event Hub connection string (`EVENT_HUB_CONNECTION_STRING`), please follow the [official Azure documentation](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-get-connection-string).
* (opt) create a venv
* run ```pip install -r requirements.txt```
* run ```python manage.py runserver```

### With Docker:
* (opt) change line 26 in ```docker-compose.yml```: use ${WRITE_TO_KAFKA} to use the value from ```.env```, or override it with True/False
* run ```docker-compose up -d```
  * (opt) you may use ```docker-compose --profile dev up -d``` to run Redis in a container for manual testing

To get into the container's shell:
* ```docker exec -it dataset_scrapper /bin/bash```

To check the logs:
* ```docker logs dataset_scrapper --tail 100``` - get the last 100 log lines
* ```docker logs --follow dataset_scrapper``` - attach to the container's logs to view them in real time

To check your Redis status:
* install ```redis-cli``` (please follow the [official Redis documentation](https://redis.io/docs/install/install-redis/))
* run ```redis-cli -h <REDIS_HOST_NAME> -p 6379 -a <REDIS_KEY> -n 0```
* to check file status: ```hget file <LINK>```