from flow.core import Flow


def handler(event, context):  # type: ignore
    client = Flow()
    channel = client.conf.channels[0]
    client.fetch(channel.name)
    client.publish(channel.name, post_frequency=1, limit=1)


handler(None, None)
