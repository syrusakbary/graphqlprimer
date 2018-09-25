import asyncio
from graphene import Schema, ObjectType, String, Float, Int, Field, List, DateTime

from twitter import store
from utils import parse_datetime


class User(ObjectType):
    name = String()
    screen_name = String()
    tweets = List(lambda: Tweet)

    def resolve_tweets(self, info):
        return store.get_tweets_for_user(self.id)


class Tweet(ObjectType):
    user = Field(User, required=True)
    text = String(required=True)
    created_at = DateTime()

    def resolve_created_at(self, info):
        return parse_datetime(self.created_at)


class Query(ObjectType):
    timeline = List(Tweet)
    leaderboard = List(User)

    async def resolve_timeline(self, info):
        return await store.get_tweets()

    async def resolve_leaderboard(self, info):
        await store.get_tweets()
        return store.get_leaderboard()


class Subscription(ObjectType):
    tweet_stream = Field(Tweet)
    leaderboard = List(User)

    async def resolve_tweet_stream(root, info):
        tweet_generator = store.get_stream()
        async for tweet in tweet_generator:
            yield tweet

    async def resolve_leaderboard(root, info):
        tweet_generator = store.get_stream()
        async for tweet in tweet_generator:
            yield store.get_leaderboard()[:5]


schema = Schema(Query, subscription=Subscription)
