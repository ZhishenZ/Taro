class SubCli:
    def __init__(self):
        pass

    def get_name(self):
        raise NotImplementedError

    def populate_subparser(self, subparser):
        raise NotImplementedError

    def run(self, ag):
        raise NotImplementedError
