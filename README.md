# [TravelMadeEasy](https://travelmadeeasy.streamlit.app/)
<img width="1440" alt="Screenshot 2024-08-24 at 6 47 18 PM" src="https://github.com/user-attachments/assets/f06e82b3-f14c-4ee2-9a59-04b8ecc2d74b">

![image](https://github.com/user-attachments/assets/f4bc9951-cc8f-48f0-a832-005139878f81)

![image](https://github.com/user-attachments/assets/16dc17bf-f0cb-40f5-9317-36d2b0be6b28)


## Features

- **Custom Itinerary Generation:** Generate travel itineraries based on user preferences such as budget, destination, and travel duration.
- **Interactive Map:** Display destinations on a map with coordinates extracted from the generated itinerary and download map to access offline.
- **Shareable Itineraries:** Easily share generated itineraries via Email or download them as PDFs.
- **Caching and Rate Limiting:** Utilizes Redis for efficient caching and rate limiting.
- **Dockerized Deployment:** The application is containerized using Docker. Easily build and run the app using Docker, ensuring that all dependencies and configurations are packaged together.

## Installation
### Prerequisites

- **Docker:** Ensure Docker is installed for containerization.
- **Python 3.9.6:** Required version of Python for running the application.
- **pip 23.2.1:** Python package installer.
- **Upstash (Redis) Account:** Set up a Redis instance with Upstash for caching and rate limiting.
- **Gemini API Key:** Obtain an API key from Google Generative AI (Gemini 1.5) for itinerary generation.


### Clone the Repository

```bash
git clone https://github.com/yourusername/TravelMadeEasy.git
cd TravelMadeEasy
```

### Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configuration
#### Environment Variables
Create a .env file in the root directory and add the following configuration:
```bash
REDIS_HOST = ''
REDIS_PORT=
REDIS_PASSWORD=''
GEMINI_API_KEY = ''
```

### Run Locally
```bash
streamlit run application.py
```

## Docker Usage
#### Build and run the Docker container:
```bash
docker build -t gotravel .
docker run -p 8501:8501 gotravel
```

## Forking and Sharing

- **Fork the Repository:** Click the "Fork" button at the top right of the [TravelMadeEasy GitHub repository](https://github.com/yourusername/TravelMadeEasy) page to create your own copy of the repository.

- **Share Your Fork:** After forking, you can make changes and share your version by providing others with the URL of your forked repository.

- **Contribute:** If you have improvements or fixes, consider creating a pull request to contribute back to the original repository.


### Suggestions are appreciated! You can connect with me on [Linkedin](https://www.linkedin.com/in/narendra-maurya-01/)

## Happy Coding :)
