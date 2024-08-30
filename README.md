# Recipe Recommendation System

## Overview
This project is a recipe recommendation system that suggests recipes based on user-provided ingredients. The system uses natural language processing to match the ingredients with a database of recipes and recommends the most relevant ones. Users can rate the recipes, and recipes rated with 1 star are excluded from future recommendations until preferences are reset.

## Features
- **Ingredient-based Recipe Search**: Enter ingredients and get recipe suggestions.
- **Multilingual Support**: Supports multiple languages including English, Korean, Chinese, Japanese, French, and German.
- **User Preferences**: Users can rate recipes, and those rated with 1 star will be excluded from future recommendations.
- **Responsive Design**: The UI adapts to different screen sizes.

## Project Structure
- `app.py`: The main Flask application that handles the backend logic, including the recommendation engine and user preferences.
- `templates/`
  - `index.html`: The main HTML file that renders the UI, including the ingredient input, language selection, and recipe display.
- `static/`
  - `css/`: Contains CSS files for styling the application.
  - `js/`: Contains JavaScript files for handling front-end logic such as rating and updating recipes in real-time.
  - `images/`: Contains flag icons and other static images used in the UI.
- `user_data.db`: The SQLite database file that stores user preferences and search history.
- `recipes.csv`: The dataset containing recipe information, including ingredients, directions, ratings, and images.
- `requirements.txt`: Lists all Python dependencies required to run the project.
- `README.md`: The file you are reading now, which provides an overview of the project and instructions for setup and usage.

## Setup and Installation
1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/recipe-recommendation-system.git
    cd recipe-recommendation-system
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Setup Google Cloud Translation API**:
    - Ensure you have set up a Google Cloud project with the Translation API enabled.
    - Place your `credentials.json` file in the project root directory and update the path in `app.py`:
      ```python
      os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path_to_your_credentials.json'
      ```

4. **Run the application**:
    ```bash
    python app.py
    ```

5. **Access the application**:
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Usage
- Enter the ingredients in the input box, separated by commas.
- Select your preferred language using the flag icons.
- Click "Generate Recipes" to see recipe suggestions.
- Rate the recipes, and those you rate with 1 star will not appear in future suggestions.
- To reset your preferences, click "Reset Preferences".

## Contributing
If you'd like to contribute to this project, please fork the repository and use a feature branch. Pull requests are welcome.

## License
This project is licensed under the MIT License.
