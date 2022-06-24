from PygameCollection.game import Base2DGame


class PhysicsSim2D(Base2DGame):
    def __init__(self):
        super().__init__()
        #self.windowCaption = "2D-Physics-Engine" #todo: implement
        self.windowSize = (1080, 720)

    def loop(self):
        print("Das ist der Gameloop")


if __name__ == "__main__":
    i = PhysicsSim2D()
    i.run()