import json

def get_keywords():
    print("Enter the keywords you want to scrape, separated by commas.")
    print("For example: 'headphones, laptops, smartphones'")
    user_input = input("Enter keywords: ")
    
    keywords = [keyword.strip() for keyword in user_input.split(',')]
    return keywords

def save_keywords(keywords, file_path='user_queries.json'):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(keywords, file, ensure_ascii=False, indent=4)
        print(f"Keywords saved successfully to {file_path}")
    except Exception as e:
        print(f"Error saving keywords: {e}")

if __name__ == '__main__':
    keywords = get_keywords()
    save_keywords(keywords)