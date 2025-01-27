import praw
import os
import json
import time
import joblib  
from datetime import datetime, timezone

def load_model():
    model = joblib.load('./model/model.joblib')  
    vectorizer = joblib.load('./model/vectorizer.joblib')  
    return model, vectorizer

def predict_title(title, model, vectorizer):
    title_tfidf = vectorizer.transform([title])  
    prediction = model.predict(title_tfidf)     
    return prediction[0]  

def has_minimum_words(title, min_words=2):
    words = title.split() 
    return len(words) >= min_words  

def is_question(title):
    return title.strip().endswith('?') 

def get_iso8601_timestamp(utc_timestamp):
    return datetime.fromtimestamp(utc_timestamp, timezone.utc).isoformat()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),        
    client_secret=os.getenv("REDDIT_SECRET"),  
    user_agent=os.getenv("REDDIT_USER_AGENT")  
)

subreddit_name = "INSERT YOUR SUBREDDIT"  
subreddit = reddit.subreddit(subreddit_name)

output_path = './data/reddit_out/reddit_posts.ndjson'

print(f"Monitorando il subreddit: r/{subreddit_name} per nuovi annunci...")

def extract_comments(post):
    post.comments.replace_more(limit=0) 
    comments = []
    for comment in post.comments.list(): 
        if comment.body in ["[deleted]", "[removed]"]:
            continue
        comments.append({
            "comment_id": comment.id,
            "comment_body": comment.body,
            "comment_score": comment.score,
            "comment_publish_time": get_iso8601_timestamp(comment.created_utc), 
        })
    return comments

model, vectorizer = load_model()

try:
    for post in subreddit.stream.submissions(skip_existing=True):
        if is_question(post.title):
            print(f"❌ Ignorato il post: {post.title} (è una domanda)")
            continue

        if not has_minimum_words(post.title):
            print(f"❌ Ignorato il post: {post.title} (meno di 2 parole)")
            continue

        prediction = predict_title(post.title, model, vectorizer)

        if prediction != "annuncio": 
            print(f"❌ Ignorato il post: {post.title} (previsione negativa)")
            continue

        print(f"🔔 Nuovo post trovato: {post.title}. Aspetto 30 secondi per raccogliere i commenti...")
        time.sleep(30)  

        post_data = {
            "post_id": post.id,
            "post_title": post.title,
            "post_body": post.selftext,  
            "post_publish_time": get_iso8601_timestamp(post.created_utc),  
            "comments": extract_comments(post) 
        }

        with open(output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(post_data) + "\n") 

        print(f"✅ Post salvato nel file: {output_path}")
except KeyboardInterrupt:
    print("Interrotto dall'utente.")
