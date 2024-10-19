# Data Streaming with Kafka
This project monitors a YouTube playlist using Confluent Kafka, Google API, and ksqlDB, and triggers real-time notifications via a Telegram bot when changes are detected (such as added likes,comments). 

## Features

- Monitor YouTube playlist data in real-time.
- Use Kafka with ksqlDB to track playlist changes.
- Send alerts via Telegram bot using an HTTP Sink Connector.
- Full setup instructions from Kafka cluster creation to running queries.

## Prerequisites

Ensure you have the following installed on your system before proceeding:

- Python 3.6 or later
- [Confluent Cloud](https://confluent.cloud/) account
- A [Telegram](https://telegram.org/) account and bot setup
- A Google API key for YouTube Data API v3

## Setup Instructions

### 1. Virtual Environment Setup

```bash
python -m venv env
env\Scripts\activate
```

### 2. Install Required Libraries

Install the necessary Python packages:
```bash
pip install requests confluent-kafka fastavro
```

### 3. Google API Setup

- Go to the [Google Cloud Console](https://console.cloud.google.com/).
- Create a new project and enable the YouTube Data API v3.
- Generate an API key and paste it into the `config.py` file as shown below:

```python

# config.py
YOUTUBE_API_KEY = 'your_google_api_key'
YOUTUBE_PLAYLIST_ID = 'your_youtube_playlist_id'  # Add the YouTube playlist ID here
```

### 4. Confluent Cloud Setup

#### Create a Kafka Cluster

- Sign up on [Confluent Cloud](https://confluent.cloud/).
- Create a new cluster named `watcher` (Basic/Free tier).

#### Create ksqlDB Cluster

- Go to **ksqlDB** and create a cluster named `watcher_ksql` with `cluster_size=1`. Wait a few minutes for initialization.
- Run Query-1 from `ksql_queries` file
- 
#### Kafka Cluster Configuration

- In the Confluent Cloud UI, navigate to **Cluster Settings**:
  
  - Copy the **Bootstrap Server URL** and paste it into `config.py`:
    ```python
    BOOTSTRAP_SERVER = 'your_bootstrap_server_url'
    ```
    
- Go to **API Keys**, generate a key, and copy the **API Key** and **Secret** to the `config.py` file:
  
    ```python
    KAFKA_API_KEY = 'your_kafka_api_key'
    KAFKA_API_SECRET = 'your_kafka_api_secret'
    ```

#### Schema Registry Setup

- Navigate to **Schema Registry** > **Cluster Settings**:
  - Copy the **Endpoint URL** and add it to `config.py`:
    
    ```python
    SCHEMA_REGISTRY_URL = 'your_schema_registry_url'
    ```
    
- Create and copy a **Schema Registry API Key** and **Secret**:
  
### 5. Running ksqlDB Queries

#### Query
- Open **ksqlDB Editor** and run the query 2 and 3 from the `ksql_queries.sql` file.

### 6. Telegram Bot Setup

- Go to Telegram and search for **BotFather**.
- Follow the steps to create a new bot. Copy the bot token and paste it into `config.py`:
    ```python
    TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
    ```
- Start a conversation with your bot.
- To get the chat ID, use the following command (replace `bottoken` with your actual bot token):
    ```bash
    curl https://api.telegram.org/bot<bottoken>/getUpdates
    ```
- Retrieve the `chat_id` from the response and add it to `config.py`:
    ```python
    TELEGRAM_CHAT_ID = 'your_telegram_chat_id'
    ```

- Run query-4 from `ksql_queries` file
  
### 7. HTTP Sink Connector

- In the Confluent Cloud UI, go to **Connectors**.
- Add a new **HTTP Sink Connector** and configure it as follows:
  - **Name**: `Telegram Connector`
  - **HTTP URL**: Use your bot's API to send messages:
    ```bash
    https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/sendMessage
    ```

### 8. Final Queries
- Run all remaining queries (from 5) from the `ksql_queries.sql` file to set up monitoring and trigger Telegram alerts.

---


## Running the Project

Once all setup is complete, activate the virtual environment and run your project to monitor YouTube playlist changes and receive notifications:

```bash
source env/Scripts/activate  # On Windows
```

Run the ksqlDB queries and ensure that the Telegram Bot is correctly configured. Your notifications will appear in Telegram once playlist changes are detected.

---
## Note:

- You have to run `youtube_watcher.py`(static) or `youtube_watcher_automated.py` (dynamic) to see changes in playlist.
- 
- All this changes will be send via Telegram Bot.
  
## Troubleshooting

- **API Key issues**: Make sure all API keys and secrets are correctly set in `config.py`.
- **Telegram Bot**: Ensure your bot token is valid and the chat ID is correct.
- **Confluent Cloud**: If you encounter errors with the Kafka cluster or ksqlDB, ensure the clusters are fully initialized before running queries.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


 
---
