# import requests
# import threading
# import time
#
#
# def get_request_test():
#     url = 'https://common-dnd-backend.fly.dev/data'
#     response = requests.get(url)
#     if response.status_code == 200:
#         print("GET request successful.")
#         print("Response:", response.json())
#     else:
#         print(f"GET request failed with status code {response.status_code}.")
#
#
# def update_request_test():
#     url = 'https://common-dnd-backend.fly.dev/update'
#     response = requests.get(url)
#     if response.status_code == 200:
#         print("Update request successful!")
#         print("Response:", response.json())
#     else:
#         print(f"Update request failed with status code {response.status_code}.")
#
#
# def post_requests_test():
#     url = 'https://common-dnd-backend.fly.dev/post'
#     data = {"key": "value", "number": 123}
#     response = requests.post(url, json=data)
#     if response.status_code == 200:
#         print("POST request successful.")
#         print("Response:", response.json())
#     else:
#         print(f"POST request failed with status code {response.status_code}.")
#
#
# def stream_updates():
#     response = requests.get('https://common-dnd-backend.fly.dev/stream', stream=True)
#     for line in response.iter_lines():
#         if line:
#             print('Update:', line.decode('utf-8'))
#
#
# def run_all_test_calls():
#     get_request_test()
#     post_requests_test()
#     sse_thread = threading.Thread(target=stream_updates)
#     sse_thread.daemon = True  # Make sure the thread exits when the main program does
#     sse_thread.start()
#     updates_count = 0
#     while updates_count < 2:
#         updates_count += 1
#         update_request_test()
#         time.sleep(14)
