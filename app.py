from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google.cloud import translate_v2 as translate
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Google Cloud Translation API 클라이언트 설정
translate_client = translate.Client()
# API 키 환경 변수 설정 (본인의 경로에 맞게 수정하세요)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/user/Desktop/my_recipe_app/eastern-rider-433904-g8-96c632e5408e.json'

# Flask 애플리케이션 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.db'  # SQLite 데이터베이스 설정
db = SQLAlchemy(app)

# 사용자 검색 기록 모델
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    selected_recipe = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<SearchHistory {self.user_id} - {self.selected_recipe}>'

# 사용자 선호도 모델
class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    recipe_name = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<UserPreference {self.user_id} - {self.recipe_name} - {self.rating}>'

# 데이터베이스 생성
with app.app_context():
    db.create_all()

# 데이터 로드 및 모델 초기화
df = pd.read_csv('recipes.csv')
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['ingredients'])

def find_top_n_recipes(ingredients, user_id, n=3):
    ingredients_str = ', '.join(ingredients)
    input_vec = vectorizer.transform([ingredients_str])
    cosine_sim = cosine_similarity(input_vec, tfidf_matrix)
    top_indices = cosine_sim[0].argsort()[-n*2:][::-1]  # 유사도가 높은 상위 n*2개의 인덱스 반환

    # 사용자의 선호도 데이터 불러오기
    disliked_recipes = UserPreference.query.filter_by(user_id=user_id, rating=1).all()
    disliked_recipe_names = [pref.recipe_name for pref in disliked_recipes]

    # 필터링: 1점을 준 레시피는 제외
    filtered_indices = [i for i in top_indices if df.iloc[i]['recipe_name'] not in disliked_recipe_names]

    # 상위 n개만 반환
    return df.iloc[filtered_indices[:n]] if filtered_indices else pd.DataFrame()  # 결과가 없을 경우 빈 데이터프레임 반환

def translate_text(text, target_language='ko'):
    """영어로 된 텍스트를 한글로 번역합니다."""
    result = translate_client.translate(text, target_language=target_language)
    return result['translatedText']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    ingredients = request.form.get('ingredients').split(',')
    ingredients = [ingredient.strip() for ingredient in ingredients]
    user_id = request.remote_addr  # 간단하게 IP를 사용자 ID로 사용, 실제 환경에서는 사용자 계정을 사용
    top_recipes = find_top_n_recipes(ingredients, user_id)
    
    if top_recipes.empty:
        # 추천할 레시피가 없는 경우
        return jsonify([])  # 빈 리스트 반환
    
    recommendations = []

    for _, recipe in top_recipes.iterrows():
        # 사용자가 선택한 레시피를 데이터베이스에 저장
        new_search = SearchHistory(user_id=user_id, ingredients=', '.join(ingredients), selected_recipe=recipe['recipe_name'])
        db.session.add(new_search)
        db.session.commit()
        
        # 레시피의 지침을 한글로 번역
        translated_instructions = translate_text(recipe['directions'])
        
        recommendations.append({
            "recipe_name": recipe['recipe_name'],
            "instructions": translated_instructions,
            "rating": recipe['rating'],
            "img_src": recipe['img_src']  # 이미지 URL 추가
        })
    
    return jsonify(recommendations)

@app.route('/rate_recipe', methods=['POST'])
def rate_recipe():
    user_id = request.remote_addr  # 간단하게 IP를 사용자 ID로 사용, 실제 환경에서는 사용자 계정을 사용
    recipe_name = request.form.get('recipe_name')
    rating = int(request.form.get('rating'))
    
    # 사용자 선호도 저장
    new_preference = UserPreference(user_id=user_id, recipe_name=recipe_name, rating=rating)
    db.session.add(new_preference)
    db.session.commit()
    
    return jsonify({"message": "Rating saved successfully."})

@app.route('/reset_preferences', methods=['POST'])
def reset_preferences():
    user_id = request.remote_addr  # 사용자 ID를 IP 주소로 사용
    # 사용자 선호도 초기화
    UserPreference.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({"message": "Preferences have been reset successfully."})

if __name__ == "__main__":
    app.run(debug=True)
