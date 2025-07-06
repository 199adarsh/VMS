import requests

def quick_test():
    session = requests.Session()
    
    # Login as admin
    login_response = session.post('http://127.0.0.1:5000/login', 
                                 json={'email': 'admin1@example.com', 'password': 'password123'})
    print(f"Login: {login_response.status_code}")
    
    # Create task
    task_data = {
        "title": "Quick Test Task",
        "description": "Testing task creation",
        "deadline": "2025-07-20",
        "priority": "High"
    }
    create_response = session.post('http://127.0.0.1:5000/tasks/create', json=task_data)
    print(f"Create task: {create_response.status_code}")
    if create_response.status_code == 201:
        task_id = create_response.json()['task_id']
        print(f"Task created: {task_id}")
        
        # Update task
        update_response = session.put(f'http://127.0.0.1:5000/tasks/{task_id}', 
                                     json={'priority': 'Medium'})
        print(f"Update task: {update_response.status_code}")
        
        # Delete task
        delete_response = session.delete(f'http://127.0.0.1:5000/tasks/{task_id}')
        print(f"Delete task: {delete_response.status_code}")
    else:
        print(f"Error: {create_response.text}")

if __name__ == "__main__":
    quick_test() 