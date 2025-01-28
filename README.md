<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">R.I.S.E</h3>
  <h4 align="center">Reddit Insights and Sentiment Exploration</h3>

  <p align="center">
    Project for the Technologies for Advanced Programming course, 2024/2025, University of Catania.
    <br />
    <a href="https://web.dmi.unict.it/corsi/l-31/insegnamenti?seuid=B9ADB77F-582D-4956-A0DB-E0BB572ACD69"><strong>Read more about the course »</strong></a>
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>        
        <li><a href="#key-features">Key Features</a></li>
        <li><a href="#modes-of-operation">Modes of operation</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#additional-info">Additional Info</a>
      <ul>
        <li><a href="#notes">Notes</a></li>
        <li><a href="#hugging-face-models">Hugging Face Models</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a>
      <ul>
        <li><a href="#attribution">Attribution</a></li>
      </ul>
    </li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

**R.I.S.E (Reddit Insights and Sentiment Exploration)** is a tool for monitoring video game-related posts on Reddit. It performs sentiment analysis and comment classification to understand public perception of video games.

### Key Features

- **Data Collection**: Gathers posts and comments from gaming subreddits using PRAW.  
- **Post Classification**: Identifies announcements using a pre-trained Logistic Regression model.  
- **Sentiment Analysis & Comment Classification**: Analyzes and categorizes comments by sentiment (positive/negative) and topics (e.g., gameplay, graphics).  
- **Visualization**: Displays results through interactive dashboards.  
- **Real-Time Monitoring**: Continuously updates with new data.  

### Modes of Operation

1. **Generic Monitoring**: Tracks posts from specified subreddits.  
2. **Keyword Monitoring**: Focuses on posts with specific keywords for targeted insights.  

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

To run this project, you will need the following software and tools:

* **Docker** ([Docker Installation Guide](https://docs.docker.com/get-docker/))
* **Reddit API** ([Reddit PRAW Documentation](https://praw.readthedocs.io/en/stable/))
* **Hugging Face API** ([Hugging Face Docs](https://huggingface.co/docs/api-inference/getting-started))

### Installation

1. Get a free Reddit API Key here: [Reddit wiki - GitHub](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps) <br>
   Get a free Hugging Face API Key here: [Hugging Face API](https://huggingface.co/docs/hub/en/security-tokens)
2. Clone the repo
   ```sh
   git clone https://github.com/Fasarix/RISE
   ```
3. Create a `reddit.env` file in the root directory of the project and add the following:
   ```env
   REDDIT_SECRET = "ENTER YOUR SECRET_KEY"
   REDDIT_CLIENT_ID = "ENTER YOUR CLIENT_ID"
   REDDIT_USER_AGENT = "ENTER YOUR USER_AGENT"
   ```

   Create a `hf.env` file in `/docker/spark/` directory and add the following:
   ```env
   API_URL = "ENTER MODEL LINK"
   headers = "ENTER BEARER AUTH"
   ```
4. Inside `praw_reddit.py` set the `subreddit_name` you want to monitor.
5. Inside `praw_reddit_custom.py` set the `subreddit_name` you want to monitor and add your custom `relevant_words` list.
6. The setup is now complete. To launch the application, execute the following command:
    ```sh
    docker-compose up --build
    ```
7. The pipeline will now listen for new posts in the selected subreddit. You can access the data visualization at `localhost:5601` in your browser.
   
## Additional Info
### Notes
  - To make this project fully operational, it will be necessary to modify the comment fetching logic and tailor it to your specific requirements.
  - A custom machine learning model for post recognition (`praw_reddit.py` & `praw_reddit_custom.py`), trained and tailored to your specific needs is needed to customize your project.
  - You can freely modify the categories used for classification in the `spark_app.py` and `spark_app_custom.py` file within the payload configuration.
    ```html
    payload = {"inputs": batch.tolist(),
               "parameters": {"candidate_labels": ["Category1", "Category2", "Category3", "Category4", "Category5"]}}
    ```

### Hugging Face Models
[![Sentiment Analysis](https://img.shields.io/badge/Hugging_Face%20%28Sentiment_Analysis%29-cardiffnlp/twitter--roberta--base--sentiment--latest-%234F88FF?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest)

[![Zero-Shot](https://img.shields.io/badge/Hugging_Face%20%28Zero_Shot_Classification%29-facebook/bart--large--mnli-%234F88FF?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/facebook/bart-large-mnli)

<!-- LICENSE -->
## License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

### Attribution

- **ELK Stack**: Copyright © Elasticsearch B.V. and licensed under the Elastic License 2.0. 
- **Apache Kafka & Apache Spark**: Copyright © Apache Software Foundation, licensed under the Apache License 2.0.
- **facebook/bart-large-mnli**: developed by Facebook AI and licensed under the MIT License.
- **cardiffnlp/twitter-roberta-base-sentiment-latest**: developed by CardiffNLP and licensed under the MIT License.
