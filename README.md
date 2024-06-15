# OW-Match-Thread-Generator

This project fetches match data from FACEIT to generate a Post-Match Discussion thread can be used for r/competitiveoverwatch.

## Table of Contents

- [OW-Match-Thread-Generator](#ow-match-thread-generator)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)

## Prerequisites

- Python 3.6 or higher
- [FACEIT API Key](https://developers.faceit.com/)

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/faceit-match-data-fetcher.git
    cd faceit-match-data-fetcher
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

## Usage

1. **Run the script:**

    ```sh
    python3 main.py
    ```

    Follow the prompts to enter a match URL and generate the post-match discussion summary.

2. **Copy/Paste the output:**

    After running the script, copy the output from the terminal and paste it in your reddit post/comment.
