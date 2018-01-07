class Service:
    def __init__(self, client, handle):
        self.client = client
        self.handle = handle
        self.membase = client.get_bases()[0]
