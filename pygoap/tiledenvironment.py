"""
Copyright 2010, 2011 Leif Theden

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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

