from pinecone import Pinecone
from dotenv import load_dotenv
from src.skaid.config import PINECONE_API_KEY
import os

# Initialize a Pineconce client
pc = Pinecone(api_key=PINECONE_API_KEY)