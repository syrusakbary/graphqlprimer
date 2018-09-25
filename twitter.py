import os
import asyncio
from peony import PeonyClient
from peony.oauth_dance import oauth_dance
from aiostream import operator

if not os.getenv("CONSUMER_KEY"):
    raise Exception("Need to setup twitter env vars (create a .env file)")

twitter_client = PeonyClient(
    consumer_key=os.getenv("CONSUMER_KEY"),
    consumer_secret=os.getenv("CONSUMER_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)


class TweetStore(object):
    def __init__(self):
        self.tweets = []
        self.max_id = None
        self.stream = None

    def add_tweets(self, tweets):
        # We prepend the tweets to the list
        self.tweets = tweets + self.tweets

    async def retrieve_tweets(self, since_id=-1):
        results = await twitter_client.api.search.tweets.get(
            q="hello", since_id=since_id, count=200, tweet_mode="extended"
        )
        return results.statuses, results.search_metadata["max_id_str"]

    async def get_tweets(self, only_recent=False, update=False):
        if not self.max_id or only_recent or update:
            tweets, self.max_id = await self.retrieve_tweets(since_id=self.max_id)
            self.add_tweets(tweets)
            if only_recent:
                return tweets
        return self.tweets

    async def tweet_iterator(self):
        while True:
            tweets = await self.get_tweets(only_recent=True)
            for tweet in tweets:
                yield tweet
            await asyncio.sleep(1)

    async def get_stream(self):
        # return self.tweet_iterator()
        if not self.stream:

            async def tweet_iterator():
                while True:
                    tweets = await self.get_tweets(only_recent=True)
                    for tweet in tweets:
                        yield tweet
                    await asyncio.sleep(1)

            self.stream = operator(tweet_iterator)()

        async with self.stream.stream() as streamer:
            async for tweet in streamer:
                yield tweet
        # return self.stream


store = TweetStore()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_test())
