import json

def save_to_json(data, file_name):
    try:
        with open(file_name, 'a', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.write(",\n")
    except Exception as e:
        print(f"Error saving data to {file_name}: {e}")