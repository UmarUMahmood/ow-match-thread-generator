# OW-Match-Thread-Generator

This project fetches match data from FACEIT to generate a Post-Match Discussion thread can be used for r/competitiveoverwatch.

## Prerequisites

- Python 3.6 or higher
- [FACEIT API Key](https://developers.faceit.com/)

## Installation

1. **Clone the repository:**

    ```sh
    git clone git@github.com:UmarUMahmood/ow-match-thread-generator.git
    cd ow-match-thread-generator
    ```

2. **Create a virtual environment:**

    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. **Create a `.env` file with your FACEIT API key:**

    ```sh
    echo "API_KEY=api-key-here" > .env
    ```

    Replace `api-key-here` with your actual FACEIT API key. You can obtain an API key from the [FACEIT Developer Portal](https://developers.faceit.com/).
    In App Studio, select your app, go to Webhooks and create a new Webhook.
    Use the organizer id for the event you want to focus on, check the "Match Finished" checkbox and use the callback URL used to host the Flask app along with the matching Security header name and value.

## Usage

1. **Run the script:**

    ```sh
    python3 main.py
    ```

2. **Copy/Paste the output:**

    After running the script, copy the output from the generated .md file and paste it in your reddit post/comment.
    The first line is your title and the rest is the body of the post.
