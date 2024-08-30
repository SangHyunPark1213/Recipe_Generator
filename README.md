# Recipe Recommendation System

## Overview
This is a Flask-based web application that provides personalized recipe recommendations based on the ingredients input by the user, while considering the user's country preferences and prior ratings. The application uses a GPT-4o model for data preprocessing, Google Cloud Translation API for language translation, and a SQLAlchemy-based database for managing user preferences and search history.

## Features
- **Personalized Recipe Recommendations**: Users input ingredients, and the application generates top recipe recommendations by considering the ingredients and the user's country preferences. Recipes are filtered based on user preferences, including excluding low-rated recipes.
- **Language Selection**: Users can select their preferred language from a variety of options, including English, Korean, Chinese, Japanese, French, and German. All displayed texts (titles, buttons, placeholders, etc.) will be translated into the selected language using Google Cloud Translation API.
- **Recipe Rating System**: Users can rate recipes on a scale of 1-5 stars. Recipes rated with a score of 1 are excluded from future recommendations unless preferences are reset.
- **Country Preference**: The application prioritizes recommending recipes that are popular in the user’s selected country.
- **Preference Reset**: Users can reset their recipe preferences, allowing previously excluded recipes to appear again in recommendations.

## Project Structure
- `app.py`: The main Flask application that handles the backend logic, including the recommendation engine and user preferences.
- `templates/`
  - `index.html`: The main HTML file that renders the UI, including the ingredient input, language selection, and recipe display.
- `static/`
  - `css/`: Contains CSS files for styling the application.
  - `images/`: Contains flag icons used in the UI.
- `user_data.db`: The SQLite database file that stores user preferences and search history.
- `recipes.csv`: The dataset containing recipe information, including ingredients, directions, ratings, and images.
- `requirements.txt`: Lists all Python dependencies required to run the project.

## Requirements

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
