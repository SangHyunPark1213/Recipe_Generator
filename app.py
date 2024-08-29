from flask import Flask, render_template, request, jsonify, session
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from flask_sqlalchemy import SQLAlchemy
from google.cloud import translate_v2 as translate
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Google Cloud Translation API 클라이언트 설정
translate_client = translate.Client()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/user/Desktop/Recipe_Generator/eastern-rider-433904-g8-833cb3388538.json'

# Flask 애플리케이션 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 사용자 검색 기록 모델
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    selected_recipe = db.Column(db.String(100), nullable=False)

# 사용자 선호도 모델
class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    recipe_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 0: Dislike, 1: Like

# 레시피 데이터 로드 및 벡터화
df = pd.read_csv('recipes.csv')  # 업로드한 파일 사용
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['ingredients'])

def translate_text(text, target_language):
    """텍스트를 지정된 언어로 번역합니다."""
    try:
        result = translate_client.translate(text, target_language=target_language)
        return result['translatedText']
    except Exception as e:
        print(f"Translation error: {e}")
        return text


@app.route('/')
def index():
    language = session.get('language', 'en')
    # 각 요소에 대한 번역 설정
    texts = {
        "title": "Recipe Generator",
        "generate_button": "Generate Recipes",
        "reset_button": "Reset Preferences",
        "input_placeholder": "Enter ingredients, separated by commas",
    }

    # 모든 텍스트를 번역
    translated_texts = {key: translate_text(value, language) for key, value in texts.items()}

    return render_template('index.html', **translated_texts, language=language)

@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    ingredients = request.json.get('ingredients', '').split(',')
    ingredients = [ingredient.strip() for ingredient in ingredients]
    user_id = request.remote_addr
    language = session.get('language', 'en')
    country_preference = session.get('country', None)

    top_recipes = find_top_n_recipes(ingredients, user_id, country_preference)

    # 추천할 레시피가 없으면 메시지를 반환
    if top_recipes.empty:
        return jsonify([{"message": translate_text("추천할 만한 레시피가 존재하지 않습니다.", language)}])

    recommendations = []

    for _, recipe in top_recipes.iterrows():
        new_search = SearchHistory(user_id=user_id, ingredients=', '.join(ingredients), selected_recipe=recipe['recipe_name'])
        db.session.add(new_search)
        db.session.commit()
        
        translated_instructions = translate_text(recipe['directions'], target_language=language)
        
        recommendations.append({
            "recipe_name": recipe['recipe_name'],
            "instructions": translated_instructions,
            "rating": recipe['rating'],
            "img_src": recipe['img_src']
        })
    
    return jsonify(recommendations)



@app.route('/change_language', methods=['POST'])
def change_language():
    language = request.form.get('language')
    country = request.form.get('country')
    session['language'] = language
    session['country'] = country
    return jsonify({"message": f"Language and country changed to {language} - {country}"})

@app.route('/rate_recipe', methods=['POST'])
def rate_recipe():
    user_id = request.remote_addr  # 간단하게 IP를 사용자 ID로 사용
    recipe_name = request.json.get('recipe_name')
    rating = request.json.get('rating')

    # 요청에서 recipe_name과 rating이 제대로 전달됐는지 확인
    if not recipe_name or rating is None:
        return jsonify({"message": "Recipe name or rating is missing."}), 400

    try:
        rating = int(rating)  # rating을 정수로 변환
    except ValueError:
        return jsonify({"message": "Invalid rating value."}), 400

    # 평점 업데이트나 새로 추가를 강제함
    existing_preference = UserPreference.query.filter_by(user_id=user_id, recipe_name=recipe_name).first()
    if existing_preference:
        # 기존 기록이 있는 경우에도 항상 업데이트를 강제
        existing_preference.rating = rating
    else:
        # 기존 기록이 없으면 새로 추가
        new_preference = UserPreference(user_id=user_id, recipe_name=recipe_name, rating=rating)
        db.session.add(new_preference)

    # 데이터베이스에 커밋
    db.session.commit()
    
    return jsonify({"message": "Rating saved successfully."})


def find_top_n_recipes(ingredients, user_id, country_preference, n=3):
    ingredients_str = ', '.join(ingredients)
    
    # 국가 선호도 필터링
    if country_preference:
        filtered_df = df[df['preferred_countries'].str.contains(country_preference, na=False)]
    else:
        filtered_df = df

    # 제공된 재료를 포함하는 레시피 필터링
    filtered_df = filtered_df[filtered_df['ingredients'].apply(lambda x: all(ingredient.lower() in x.lower() for ingredient in ingredients))]

    # 필터링 결과가 없으면 빈 DataFrame 반환
    if filtered_df.empty:
        return pd.DataFrame()

    # 별점 0 또는 1을 준 레시피를 제외
    excluded_recipes = UserPreference.query.filter(UserPreference.user_id == user_id, UserPreference.rating.in_([0, 1])).all()
    excluded_recipe_names = set(pref.recipe_name for pref in excluded_recipes)

    # 제외된 레시피를 필터링
    filtered_df = filtered_df[~filtered_df['recipe_name'].isin(excluded_recipe_names)]

    # 필터링된 결과가 없으면 빈 DataFrame 반환
    if filtered_df.empty:
        return pd.DataFrame()

    # 필터링된 레시피 중에서 n개 랜덤 선택
    selected_df = filtered_df.sample(min(n, len(filtered_df)))

    return selected_df

@app.route('/reset_preferences', methods=['POST'])
def reset_preferences():
    user_id = request.remote_addr
    # 사용자 선호도 초기화
    UserPreference.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({"message": "Preferences have been reset successfully."})

@app.route('/undefined')
def undefined_route():
    return "This route is intentionally left undefined."


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 데이터베이스 테이블 생성
    app.run(debug=True)
