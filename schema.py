import asyncio
from graphene import Schema, ObjectType, String, Float, Int, Field, List, DateTime

from twitter import store
from utils import parse_datetime


class User(ObjectType):
    name = String()
    screen_name = String()


class Tweet(ObjectType):
    user = Field(User, required=True)
    text = String(required=True)
    created_at = DateTime()

    def resolve_created_at(self, info):
        return parse_datetime(self.created_at)


class Query(ObjectType):
    timeline = List(Tweet)

    async def resolve_timeline(self, info):
        return await store.get_tweets()


class Subscription(ObjectType):
    tweet_stream = Field(Tweet)

    async def resolve_tweet_stream(root, info):
        tweet_generator = store.get_stream()
        async for tweet in tweet_generator:
            yield tweet


schema = Schema(Query, subscription=Subscription)
