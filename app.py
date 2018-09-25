
from aiohttp import web
from aiohttp_graphql import GraphQLView
from graphql_ws.aiohttp import AiohttpSubscriptionServer
from graphql.execution.executors.asyncio import AsyncioExecutor

# To load the environment variables
from dotenv import load_dotenv, find_dotenv

if find_dotenv():
    load_dotenv()


from schema import schema
from playground import playground_view
from graphiql import graphiql_view


app = web.Application()

# GraphQL views
graphql_view = GraphQLView(schema=schema, graphiql=False, executor=AsyncioExecutor())
subscription_server = AiohttpSubscriptionServer(schema)


async def subscriptions(request):
    # We are handling GraphQL requests from subscription endpoint since
    # GraphQL playground doesn't let us specify two different
    # endpoints for each operation
    if request.method == "POST":
        return await graphql_view(request)

    ws = web.WebSocketResponse(protocols=("graphql-ws",))
    await ws.prepare(request)

    await subscription_server.handle(ws)
    return ws


# GraphQL routes

## GraphQL endpoint
app.router.add_route("*", "/graphql", graphql_view)
## GraphiQL
app.router.add_route("GET", "/graphiql", graphiql_view)
## Playground
app.router.add_route("GET", "/playground", playground_view)
## Subscriptions Websockets
app.router.add_route("*", "/subscriptions", subscriptions)

try:
    # We try to autoreload our app, to iterate faster
    import aioreloader

    aioreloader.start()
except ImportError:
    pass


async def app_factory():
    return app


web.run_app(app_factory())
