from PygameCollection.game import Base2DGame


class PhysicsSim2D(Base2DGame):
    def __init__(self):
        super().__init__()
        self.windowSize = (1080, 720)

    def loop(self):
        pass


if __name__ == "__main__":
    i = PhysicsSim2D()
    i.run()