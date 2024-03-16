import os
import logging
import aiohttp
import asyncio
from nltk import word_tokenize, pos_tag, ne_chunk, download
from nltk.tree import Tree
import nltk
import openai
import requests
from config import Config

async def make_api_request(url, params={}):
    """
    Make an asynchronous API request.

    Args:
        url (str): The URL of the API endpoint.
        params (dict): The query parameters for the API request (default: {}).

    Returns:
        dict: The JSON response from the API if successful, or None if an error occurred.
    """
    async with aiohttp.ClientSession() as session:
        try:
            logging.debug(f"Making API request to {url} with params {params}")
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raises an HTTPError for bad responses
                data = await response.json()
                logging.debug(f"API response: {data}")
                return data
        except aiohttp.ClientError as e:
            logging.error(f"API request failed: {e}")
            return None

def setup_nltk():
    """
    Set up the required NLTK resources.
    """
    resources = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
    for resource in resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            download(resource, quiet=True)

def get_continuous_chunks(text):
    """
    Extract continuous chunks (named entities) from the given text.

    Args:
        text (str): The input text.

    Returns:
        list: A list of continuous chunks (named entities) found in the text.
    """
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if isinstance(i, Tree):
            current_chunk.append(" ".join([token for token, _ in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
            current_chunk = []
    return continuous_chunk

def perform_web_search(query):
    """
    Perform a web search using the Google Custom Search API.

    Args:
        query (str): The search query.

    Returns:
        dict: The JSON response from the API if successful, or None if an error occurred.
    """
    base_url = "https://www.googleapis.com/customsearch/v1"
    search_engine_id = Config.GOOGLE_PSE_ID
    api_key = Config.GOOGLE_PSE_API_KEY
    params = {
        "q": query,
        "cx": search_engine_id,
        "key": api_key,
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return None

def format_search_results(results):
    """
    Format the search results obtained from the web search.

    Args:
        results (dict): The JSON response from the web search API.

    Returns:
        str: The formatted search results, or a default message if no results are found.
    """
    if not results or 'items' not in results:
        return "I'm sorry, I couldn't find any results."
    snippets = [result['snippet'] for result in results['items'][:3]]
    return "\\n".join(snippets)