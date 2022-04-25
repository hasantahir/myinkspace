#! /usr/bin/env python3

# this extension is under licence CC-by-sa   @ Tiemen DUVILLARD 2020
# for all questions, comments, bugs: duvillard.tiemen@gmail.com 

import inkex
from lxml import etree

# my maze module
from maze import *


def points_to_svgd(p, close=False):
    """ convert list of points (x,y) pairs
        into a SVG path list
    """
    f = p[0]
    p = p[1:]
    svgd = 'M%.4f,%.4f' % f
    for x in p:
        svgd += 'L%.4f,%.4f' % x
    if close:
        svgd += 'z'
    return svgd


class Recursive(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--verti", type=int, default=20, help="Height")
        pars.add_argument("--horiz", type=int, default=20, help="Length")
        pars.add_argument("--size",  type=float, default=10.0, help="Cell Size")
        pars.add_argument("--algo", default=1, help="Algorithm")
        pars.add_argument("--width", type=float, default=10.0, help="Line width")

    def effect(self):
        # basic style
        style = { 'stroke': "black", "fill":"none", 'stroke-width': self.options.width }
        # my group of paths
        topgroup = etree.SubElement(self.svg.get_current_layer(), 'g' )

        lc = self.options.size
        X = self.options.verti
        Y = self.options.horiz
        
        L = Maze(X,Y,self.options.algo)

        for i,j,door in L.verticalDoors():
            if door:
                path = points_to_svgd([(lc*(j+1), lc*(i)), (lc*(j+1), lc*(i+1))])
                mypath_attribs = { 'style': str(inkex.Style(style)), 'd': path }
                squiggle = etree.SubElement(topgroup, inkex.addNS('path','svg'), mypath_attribs )
    
        for i,j,door in L.horizontalDoors():
            if door:
                path = points_to_svgd([(lc*(j), lc*(i+1)), (lc*(j+1), lc*(i+1))])
                mypath_attribs = { 'style': str(inkex.Style(style)), 'd': path }
                squiggle = etree.SubElement(topgroup, inkex.addNS('path','svg'), mypath_attribs )

        
        path = points_to_svgd([(0,0),(0,lc*Y),(lc*X,lc*Y),(lc*X,0)], True)
        mypath_attribs = { 'style': str(inkex.Style(style)), 'd': path }
        squiggle = etree.SubElement(topgroup, inkex.addNS('path','svg'), mypath_attribs )

 
if __name__ == '__main__':
    Recursive().run()