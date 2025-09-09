import json
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from youtube_transcript_api import YouTubeTranscriptApi
from llama_index.readers.youtube_transcript import YoutubeTranscriptReader
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.core import VectorStoreIndex, Response, StorageContext


class YoutubeTool:
    def __init__(self):
        load_dotenv()
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        self.loader = YoutubeTranscriptReader()
        self.chroma_client = chromadb.PersistentClient('./chromadb_storage')

    def add_watch_list(self, yt_channel):
        username = yt_channel.split('@')[1]
        
        channel_id = self.youtube.channels().list(
            part='id',
            forHandle= username
        ).execute()
        channel_id = channel_id['items'][0]['id']

        if os.path.exists('./utils/data/watchlist.json'):
            with open('./utils/data/watchlist.json', 'r') as file:
                watchlist = json.load(file)
        else:
            watchlist = []

        for entry in watchlist:
                if username in entry:
                    return f"{username} already in watchlist"
        
        watchlist.append({username: channel_id})
        with open('./utils/data/watchlist.json', 'w') as file:
            json.dump(watchlist, file, indent=4)
        return f"{username} added!"

    def clear_watch_list(self):
        if os.path.exists('./utils/data/watchlist.json'):
            with open('./utils/data/watchlist.json', 'w') as file:
                json.dump([], file, indent=4)
        return 'Watchlist cleared!'

    def delete_watch_list(self, yt_channel_name):
        if os.path.exists('./utils/data/watchlist.json'):
            with open('./utils/data/watchlist.json', 'r') as file:
                watchlist = json.load(file)
            
            for entry in watchlist:
                if yt_channel_name in entry:
                    watchlist.remove(entry)
                    with open('./utils/data/watchlist.json', 'w') as file:
                        json.dump(watchlist, file, indent=4)
                    return f"{yt_channel_name} removed from watchlist"

            return f"{yt_channel_name} is not in the watchlist"
        
    def pull_updated_vids_from_watchlist(self):
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=5)
        published_after = yesterday.isoformat(timespec='seconds').replace('+00:00', 'Z')
        print(f"Published after: {published_after}")

        if os.path.exists('./utils/data/watchlist.json'):
            with open('./utils/data/watchlist.json', 'r') as file:
                watchlist = json.load(file)
                yt_links = []

                for entry in watchlist:
                    for username, channel_id in entry.items():
                        vids = self.youtube.search().list(
                            part='snippet',
                            channelId=channel_id,
                            type='video',
                            publishedAfter=published_after,
                            videoCaption='closedCaption'
                        ).execute()
                        
                        for vid in vids.get('items', []):
                            print(vid)
                            yt_links.append(vid['id']['videoId'])
            self.yt_links = yt_links
            self.last_pulled = now.date()
            print(self.yt_links, self.last_pulled)

    def summarize_youtube(self, youtube_link: str, llm, embed_model, query: str) -> str:
        if not llm or not embed_model:
            raise Exception("No llm orembed_model")

        try:
            # Only works for web link, not mobile link
            ytb_id = youtube_link.split("?v=")[1]
            print(ytb_id)
            
            language_code = ""
            transcript_list = YouTubeTranscriptApi.list_transcripts(ytb_id)
            for transcript in transcript_list:
                language_code = transcript.language_code
            print(language_code)
            
            loader = YoutubeTranscriptReader()
            documents = loader.load_data(
                ytlinks=[youtube_link],
                languages=["zh", "zh-TW", "en", language_code]
            )

            index = VectorStoreIndex.from_documents(
                documents=documents,
                embed_model=embed_model
            )
            query_engine = index.as_query_engine(llm=llm)
            res: Response = query_engine.query(query)
            # pprint_response(res, show_source=True)
            return res.response
        except Exception as e:
            print(e)
            return "Oops...Not able to summarize this vdeo"

def main():
    yt = YoutubeTool()
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    llm = Ollama(model='llama3.2:1b', request_timeout=600)
    embed_model = HuggingFaceEmbedding('BAAI/bge-base-en-v1.5')

    yt.summarize_youtube(youtube_link="https://www.youtube.com/watch?v=KsX3fRnC_HQ", llm=llm, embed_model=embed_model)
    



if __name__ == '__main__':
    main()