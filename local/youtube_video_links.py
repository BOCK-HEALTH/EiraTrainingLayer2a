import os
import time
from typing import List
import requests
from googleapiclient.discovery import build
from dotenv import load_dotenv

class YouTubeScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_uploads_playlist_id(self, channel_id: str) -> str:
        ch_request = self.youtube.channels().list(
            part='contentDetails',
            id=channel_id
        )
        ch_response = ch_request.execute()
        uploads_playlist_id = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return uploads_playlist_id

    def get_video_links_from_playlist(self, playlist_id: str) -> List[str]:
        video_links = []
        next_page_token = None
        while True:
            request = self.youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            for item in response['items']:
                video_id = item['contentDetails']['videoId']
                video_links.append(f'https://www.youtube.com/watch?v={video_id}')
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        return video_links

    def get_video_links_from_channel(self, channel_id: str) -> List[str]:
        uploads_playlist_id = self.get_uploads_playlist_id(channel_id)
        return self.get_video_links_from_playlist(uploads_playlist_id)

    def send_to_ec2(self, video_url: str):
        try:
            response = requests.post(self.ec2_endpoint, json={"url": video_url})
            if response.status_code == 200:
                print(f"[+] Sent {video_url} → {response.json()['status']}")
            else:
                print(f"[!] Failed to send {video_url} → Status: {response.status_code}")
        except Exception as e:
            print(f"[×] Error sending {video_url}:", e)


def main():
    load_dotenv()

    api_key = "AIzaSyBvSYm4TBbwCZUwpp_306UuXbkbB6NBZcE"
    channel_id = input("Enter YouTube channel ID: ").strip()

    if not all([api_key, channel_id]):
        print("API key or channel ID missing.")
        return

    scraper = YouTubeScraper(api_key)
    video_links = scraper.get_video_links_from_channel(channel_id)


    # Write all video links to a TXT file
    with open("youtube_video_links.txt", "w") as f:
        for link in video_links:
            f.write(link + "\n")


    print(f"\nFound {len(video_links)} video links. Saved to youtube_video_links.txt.\n")


    # The following code for sending links to EC2 and polling status is commented out as per user request.
    # max_retries = 5
    # delay_between_links = 5  # seconds
    # poll_interval = 10  # seconds between status checks
    # status_url_base = ec2_endpoint.rstrip('/process')
    # for idx, link in enumerate(video_links):
    #     print(f"Sending link {idx+1}/{len(video_links)} for processing: {link}")
    #     retries = 0
    #     request_id = None
    #     while retries < max_retries:
    #         try:
    #             response = requests.post(
    #                 ec2_endpoint,
    #                 json={"url": link},
    #                 timeout=30
    #             )
    #             if response.status_code == 200:
    #                 resp_json = response.json()
    #                 print(f"[✓] EC2 response: {resp_json}")
    #                 request_id = resp_json.get('request_id')
    #                 if not request_id:
    #                     print(f"[!] No request_id returned for {link}, skipping.")
    #                     break
    #                 # Poll for completion
    #                 status_url = status_url_base + f"/status/{request_id}"
    #                 print(f"[~] Polling status at {status_url}")
    #                 while True:
    #                     try:
    #                         status_resp = requests.get(status_url, timeout=10)
    #                         if status_resp.status_code == 200:
    #                             status = status_resp.json().get('status')
    #                             print(f"[~] Status for {link}: {status}")
    #                             if status == 'done':
    #                                 print(f"[✓] Processing complete for {link}")
    #                                 break
    #                             elif status and status.startswith('error'):
    #                                 print(f"[×] Error processing {link}: {status}")
    #                                 break
    #                         else:
    #                             print(f"[!] Status check failed: {status_resp.status_code}")
    #                     except Exception as e:
    #                         print(f"[!] Exception while polling status: {e}")
    #                     time.sleep(poll_interval)
    #                 break  # move to next link
    #             else:
    #                 print(f"[!] EC2 returned status {response.status_code}: {response.text}")
    #         except requests.exceptions.RequestException as e:
    #             print(f"[!] Error sending to EC2 for {link}: {e}")
    #         retries += 1
    #         if retries < max_retries:
    #             print(f"[!] Retrying ({retries}/{max_retries}) after delay...")
    #             time.sleep(delay_between_links)
    #         else:
    #             print(f"[×] Failed to send {link} after {max_retries} attempts. Skipping.")
    #     # Wait a bit before sending the next link
    #     time.sleep(delay_between_links)


if __name__ == '__main__':
    main()


# wget https://raw.githubusercontent.com/Samuel-0316/EC2_S3_Pipeline/youtube_video_links.py