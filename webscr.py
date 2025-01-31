import requests
import sqlite3
from bs4 import BeautifulSoup

def login_to_picoctf(login_url, username, password):
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    response = session.get(login_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to load login page: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = None
    csrf_input = soup.find('input', {'name': 'csrf_token'}) 
    if csrf_input:
        csrf_token = csrf_input.get('value')
    
    login_data = {
        'username': username,
        'password': password
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(login_url, data=login_data, headers=headers)
    if login_response.status_code != 200:
        print("Login failed!")
        return None
    
    print("Logged in successfully!")
    return session

def fetch_ctf_questions(url, session):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = session.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    questions = []
    
    for challenge in soup.find_all('div', class_='challenge-card'):
        title = challenge.find('h3').text.strip() if challenge.find('h3') else "Unknown"
        description = challenge.find('p').text.strip() if challenge.find('p') else "No description available"
        questions.append((title, description))
    
    return questions

def save_to_database(data, db_name="ctf_questions.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT,
                      description TEXT)''')
    
    cursor.executemany('INSERT INTO questions (title, description) VALUES (?, ?)', data)
    conn.commit()
    conn.close()
    print("Data saved successfully.")

def main():
    login_url = "https://play.picoctf.org/login"
    ctf_url = "https://play.picoctf.org/practice"
    username = "Basumatary" 
    password = "Gingerisnoob@12"

    session = login_to_picoctf(login_url, username, password)
    
    if session:
        questions = fetch_ctf_questions(ctf_url, session)
        if questions:
            save_to_database(questions)
        else:
            print("No questions found.")
    else:
        print("Failed to log in.")

if __name__ == "__main__":
    main()

