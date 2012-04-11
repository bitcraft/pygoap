from environment2d import XYEnvironment
import tmxloader
from pygame import Surface



class TiledEnvironment(XYEnvironment):
    """
    Environment that can use Tiled Maps
    """

    def __init__(self, filename):
        self.filename = filename
        self.tiledmap = tmxloader.load_pygame(self.filename)
    
        super(TiledEnvironment, self).__init__()

    def render(self, surface):
        # not going for effeciency here

        for l in xrange(0, len(self.tiledmap.layers)):
            for y in xrange(0, self.tiledmap.height):
                for x in xrange(0, self.tiledmap.width):
                    tile = self.tiledmap.get_tile_image(x, y, l)
                    xx = x * self.tiledmap.tilewidth
                    yy = y * self.tiledmap.tileheight
                    if not tile == 0:
                        surface.blit(tile, (xx, yy))

        for t in self.things:
            x, y = t.position[1]
            x *= self.tiledmap.tilewidth
            y *= self.tiledmap.tileheight

            s = Surface((self.tiledmap.tilewidth, self.tiledmap.tileheight))
            s.fill((128,0,0))

            surface.blit(s, (x, y))

    def __repr__(self):
        return "T-Env"

