#!/usr/bin/env python3
# coding=utf-8
#
# Copyright (C) 2005,2007 Aaron Spike, aaron@ekips.org
# Copyright (C) 2009 Alvin Penner, penner@vaxxine.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
This extension converts a path into a dashed line using 'stroke-dasharray'
It is a modification of the file addnodes.py
It is a modification of the file convert2dash.py
Extension to convert paths into dash-array line

Extension for InkScape 1.X
Author: Mario Voigt / FabLab Chemnitz
Mail: mario.voigt@stadtfabrikanten.org
Date: 09.04.2021
Last patch: 14.04.2021
License: GNU GPL v3
"""

import copy
import re

import inkex
from inkex import bezier, CubicSuperPath, Group, PathElement
from inkex.bezier import csplength


class LinksCreator(inkex.EffectExtension):
    
    def add_arguments(self, pars):
        pars.add_argument("--tab")
        pars.add_argument("--path_types", default="closed_paths", help="Apply for closed paths, open paths or both")
        pars.add_argument("--creationunit", default="mm", help="Creation Units")
        pars.add_argument("--creationtype", default="entered_values", help="Creation")
        pars.add_argument("--link_count", type=int, default=1, help="Link count")
        pars.add_argument("--link_multiplicator", type=int, default=1, help="If set, we create a set of multiple gaps of same size next to the main gap")
        pars.add_argument("--length_link", type=float, default=1.000, help="Link length")
        pars.add_argument("--link_offset", type=float, default=0.000, help="Link offset (+/-)")
        pars.add_argument("--switch_pattern", type=inkex.Boolean, default=False, help="If enabled, we use gap length as dash length (switches the dasharray pattern")       
        pars.add_argument("--custom_dasharray_value", default="", help="A list of separated lengths that specify the lengths of alternating dashes and gaps. Input only accepts numbers. It ignores percentages or other characters.")
        pars.add_argument("--custom_dashoffset_value", type=float, default=0.000, help="Link offset (+/-)")       
        pars.add_argument("--length_filter", type=inkex.Boolean, default=False, help="Enable path length filtering")
        pars.add_argument("--length_filter_value", type=float, default=0.000, help="Paths with length more than")
        pars.add_argument("--length_filter_unit", default="mm", help="Length filter unit")
        pars.add_argument("--keep_selected", type=inkex.Boolean, default=False, help="Keep selected elements")
        pars.add_argument("--no_convert", type=inkex.Boolean, default=False, help="Do not create segments (cosmetic gaps only)")
        pars.add_argument("--breakapart", type=inkex.Boolean, default=False, help="Performs CTRL + SHIFT + K to break the new output path into it's parts")
        pars.add_argument("--show_info", type=inkex.Boolean, default=False, help="Print some length and pattern information")
        pars.add_argument("--skip_errors", type=inkex.Boolean, default=False, help="Skip errors")

    def breakContours(self, node, breakNodes = None): #this does the same as "CTRL + SHIFT + K"
        if breakNodes == None:
            breakNodes = []
        if node.tag == inkex.addNS('path','svg'):
            parent = node.getparent()
            idx = parent.index(node)
            idSuffix = 0    
            raw = node.path.to_arrays()
            subPaths, prev = [], 0
            for i in range(len(raw)): # Breaks compound paths into simple paths
                if raw[i][0] == 'M' and i != 0:
                    subPaths.append(raw[prev:i])
                    prev = i
            subPaths.append(raw[prev:])
            for subpath in subPaths:
                replacedNode = copy.copy(node)
                oldId = replacedNode.get('id')
                replacedNode.set('d', CubicSuperPath(subpath))
                replacedNode.set('id', oldId + str(idSuffix).zfill(5))
                parent.insert(idx, replacedNode)
                idSuffix += 1
                breakNodes.append(replacedNode)
            parent.remove(node)
        for child in node:
            self.breakContours(child, breakNodes)
        return breakNodes

    def effect(self):
        def createLinks(node):   
            nodeParent = node.getparent()

            pathIsClosed = False
            path = node.path.to_arrays() #to_arrays() is deprecated. How to make more modern?
            if path[-1][0] == 'Z' or path[0][1] == path[-1][1]:  #if first is last point the path is also closed. The "Z" command is not required
                pathIsClosed = True
            if self.options.path_types == 'open_paths' and pathIsClosed is True:
                return #skip this loop iteration
            elif self.options.path_types == 'closed_paths' and pathIsClosed is False:
                return #skip this loop iteration
            elif self.options.path_types == 'both':
                pass
                         
            # if keeping is enabled we make of copy of the current node and insert it while modifying the original ones. We could also delete the original and modify a copy...
            if self.options.keep_selected is True:
                parent = node.getparent()
                idx = parent.index(node)
                copynode = copy.copy(node)
                parent.insert(idx, copynode)

            # we measure the length of the path to calculate the required dash configuration
            csp = node.path.transform(node.composed_transform()).to_superpath()
            slengths, stotal = csplength(csp) #get segment lengths and total length of path in document's internal unit
           
            if self.options.length_filter is True:
                if stotal < self.svg.unittouu(str(self.options.length_filter_value) + self.options.length_filter_unit):
                    if self.options.show_info is True: self.msg("node " + node.get('id') + " is shorter than minimum allowed length of {:1.3f} {}. Path length is {:1.3f} {}".format(self.options.length_filter_value, self.options.length_filter_unit, stotal, self.options.creationunit))
                    return #skip this loop iteration

            if self.options.creationunit == "percent":
                length_link = (self.options.length_link / 100.0) * stotal
            else:
                length_link = self.svg.unittouu(str(self.options.length_link) + self.options.creationunit)

            dashes = [] #central dashes array
            
            if self.options.creationtype == "entered_values":
                dash_length = ((stotal - length_link * self.options.link_count) / self.options.link_count) - 2 * length_link * self.options.link_multiplicator
                dashes.append(dash_length)
                dashes.append(length_link)                  
                for i in range(0, self.options.link_multiplicator):
                    dashes.append(length_link) #stroke (=gap)
                    dashes.append(length_link) #gap
                    
                if self.options.switch_pattern is True:
                    dashes = dashes[::-1] #reverse the array
                    
                #validate dashes. May not be negative (dash or gap cannot be longer than the path itself). Otherwise Inkscape will freeze forever. Reason: rendering issue
                if any(dash <= 0.0 for dash in dashes) == True: 
                    if self.options.show_info is True: self.msg("node " + node.get('id') + ": Error! Dash array may not contain negative numbers: " + ' '.join(format(dash, "1.3f") for dash in dashes) + ". Path skipped. Maybe it's too short. Adjust your link count, multiplicator and length accordingly, or set to unit '%'")
                    return False if self.options.skip_errors is True else exit(1)
               
                if self.options.creationunit == "percent":
                    stroke_dashoffset = self.options.link_offset / 100.0
                else:         
                    stroke_dashoffset = self.svg.unittouu(str(self.options.link_offset) + self.options.creationunit)
                    
                if self.options.switch_pattern is True:
                    stroke_dashoffset = stroke_dashoffset + ((self.options.link_multiplicator * 2) + 1)  * length_link

            if self.options.creationtype == "use_existing":
                if self.options.no_convert is True:
                    if self.options.show_info is True: self.msg("node " + node.get('id') + ": Nothing to do. Please select another creation method or disable cosmetic style output paths.")
                    return False if self.options.skip_errors is True else exit(1)
                stroke_dashoffset = 0
                style = node.style
                if 'stroke-dashoffset' in style:
                    stroke_dashoffset = style['stroke-dashoffset']
                try:
                    floats = [float(dash) for dash in re.findall(r"[+]?\d*\.\d+|\d+", style['stroke-dasharray'])] #allow only positive values
                    if len(floats) > 0:
                        dashes = floats #overwrite previously calculated values with custom input
                    else:
                        raise ValueError
                except:
                    if self.options.show_info is True: self.msg("node " + node.get('id') + ": No dash style to continue with.")
                    return False if self.options.skip_errors is True else exit(1)
                           
            if self.options.creationtype == "custom_dashpattern":
                stroke_dashoffset = self.options.custom_dashoffset_value
                try:
                    floats = [float(dash) for dash in re.findall(r"[+]?\d*\.\d+|\d+", self.options.custom_dasharray_value)] #allow only positive values
                    if len(floats) > 0:
                        dashes = floats #overwrite previously calculated values with custom input
                    else:
                        raise ValueError
                except:
                    if self.options.show_info is True: self.msg("node " + node.get('id') + ": Error in custom dasharray string (might be empty or does not contain any numbers).")
                    return False if self.options.skip_errors is True else exit(1)

            #assign stroke dasharray from entered values, existing style or custom dashpattern
            stroke_dasharray = ' '.join(format(dash, "1.3f") for dash in dashes)

            # check if the node has a style attribute. If not we create a blank one with a black stroke and without fill
            style = None
            default_fill = 'none'
            default_stroke_width = '1px'
            default_stroke = '#000000'
            if node.attrib.has_key('style'):
                style = node.get('style')
                if style.endswith(';') is False:
                    style += ';'
                    
                # if has style attribute and dasharray and/or dashoffset are present we modify it accordingly
                declarations = style.split(';')  # parse the style content and check what we need to adjust
                for i, decl in enumerate(declarations):
                    parts = decl.split(':', 2)
                    if len(parts) == 2:
                        (prop, val) = parts
                        prop = prop.strip().lower()
                        #if prop == 'fill':
                        #    declarations[i] = prop + ':{}'.format(default_fill) 
                        #if prop == 'stroke':
                        #    declarations[i] = prop + ':{}'.format(default_stroke)
                        #if prop == 'stroke-width':
                        #    declarations[i] = prop + ':{}'.format(default_stroke_width)
                        if prop == 'stroke-dasharray': #comma separated list of one or more float values
                            declarations[i] = prop + ':{}'.format(stroke_dasharray)
                        if prop == 'stroke-dashoffset':
                            declarations[i] = prop + ':{}'.format(stroke_dashoffset)
                node.set('style', ';'.join(declarations)) #apply new style to node
                    
                #if has style attribute but the style attribute does not contain fill, stroke, stroke-width, stroke-dasharray or stroke-dashoffset yet
                style = node.style
                if re.search('fill:(.*?)(;|$)', str(style)) is None:
                    style += 'fill:{};'.format(default_fill)
                if re.search('(;|^)stroke:(.*?)(;|$)', str(style)) is None: #if "stroke" is None, add one. We need to distinguish because there's also attribute "-inkscape-stroke" that's why we check starting with ^ or ;
                    style += 'stroke:{};'.format(default_stroke)
                if not 'stroke-width' in style:
                    style += 'stroke-width:{};'.format(default_stroke_width)
                if not 'stroke-dasharray' in style:
                    style += 'stroke-dasharray:{};'.format(stroke_dasharray)
                if not 'stroke-dashoffset' in style:
                    style += 'stroke-dashoffset:{};'.format(stroke_dashoffset)
                node.set('style', style)
            else:
                style = 'fill:{};stroke:{};stroke-width:{};stroke-dasharray:{};stroke-dashoffset:{};'.format(default_fill, default_stroke, default_stroke_width, stroke_dasharray, stroke_dashoffset)
                node.set('style', style)

            # Print some info about values
            if self.options.show_info is True:
                self.msg("node " + node.get('id') + ":")
                if self.options.creationunit == "percent":
                    self.msg(" * total path length = {:1.3f} {}".format(stotal, self.svg.unit)) #show length, converted in selected unit
                    self.msg(" * (calculated) offset: {:1.3f} %".format(stroke_dashoffset))
                    if self.options.creationtype == "entered_values":
                        self.msg(" * (calculated) gap length: {:1.3f} %".format(length_link))
                else:
                    self.msg(" * total path length = {:1.3f} {} ({:1.3f} {})".format(self.svg.uutounit(stotal, self.options.creationunit), self.options.creationunit, stotal, self.svg.unit)) #show length, converted in selected unit
                    self.msg(" * (calculated) offset: {:1.3f} {}".format(self.svg.uutounit(stroke_dashoffset, self.options.creationunit), self.options.creationunit))
                    if self.options.creationtype == "entered_values":
                        self.msg(" * (calculated) gap length: {:1.3f} {}".format(length_link, self.options.creationunit))
                if self.options.creationtype == "entered_values":        
                    self.msg(" * total gaps = {}".format(self.options.link_count))
                self.msg(" * (calculated) dash/gap pattern: {} ({})".format(stroke_dasharray, self.svg.unit))
     
            # Conversion step (split cosmetic path into real segments)    
            if self.options.no_convert is False:
                style = node.style #get the style again, but this time as style class    
                    
                new = []
                for sub in node.path.to_superpath():
                    idash = 0
                    dash = dashes[0]
                    length = float(stroke_dashoffset)
                    while dash < length:
                        length = length - dash
                        idash = (idash + 1) % len(dashes)
                        dash = dashes[idash]
                    new.append([sub[0][:]])
                    i = 1
                    while i < len(sub):
                        dash = dash - length
                        length = bezier.cspseglength(new[-1][-1], sub[i])
                        while dash < length:
                            new[-1][-1], nxt, sub[i] = bezier.cspbezsplitatlength(new[-1][-1], sub[i], dash/length)
                            if idash % 2: # create a gap
                                new.append([nxt[:]])
                            else:  # splice the curve
                                new[-1].append(nxt[:])
                            length = length - dash
                            idash = (idash + 1) % len(dashes)
                            dash = dashes[idash]
                        if idash % 2:
                            new.append([sub[i]])
                        else:
                            new[-1].append(sub[i])
                        i += 1
                style.pop('stroke-dasharray')
                node.pop('sodipodi:type')
                csp = CubicSuperPath(new)
                node.path = CubicSuperPath(new)
                node.style = style
                
                # break apart the combined path to have multiple elements
                if self.options.breakapart is True:
                    breakOutputNodes = None
                    breakOutputNodes = self.breakContours(node, breakOutputNodes)
                    breakApartGroup = nodeParent.add(inkex.Group())
                    for breakOutputNode in breakOutputNodes:
                        breakApartGroup.append(breakOutputNode)
                        #self.msg(replacedNode.get('id'))
                        #self.svg.selection.set(replacedNode.get('id')) #update selection to split paths segments (does not work, so commented out)

                        #cleanup useless points
                        p = breakOutputNode.path
                        commandsCoords = p.to_arrays()
                        # "m 45.250809,91.692739" - this path contains onyl one command - a single point
                        if len(commandsCoords) == 1:
                            breakOutputNode.delete()
                        # "m 45.250809,91.692739 z"  - this path contains two commands, but only one coordinate. 
                        # It's a single point, the path is closed by a Z command
                        elif len(commandsCoords) == 2 and commandsCoords[0][1] == commandsCoords[1][1]:
                            breakOutputNode.delete()
                        # "m 45.250809,91.692739 l 45.250809,91.692739" - this path contains two commands, 
                        # but the first and second coordinate are the same. It will render als point
                        elif len(commandsCoords) == 2 and commandsCoords[-1][0] == 'Z':
                            breakOutputNode.delete()
                        # "m 45.250809,91.692739 l 45.250809,91.692739 z" - this path contains three commands, 
                        # but the first and second coordinate are the same. It will render als point, the path is closed by a Z command
                        elif len(commandsCoords) == 3 and commandsCoords[0][1] == commandsCoords[1][1] and commandsCoords[2][1] == 'Z':
                            breakOutputNode.delete()
                        
        if len(self.svg.selected) > 0:
            for node in self.svg.selection.values():
                #at first we need to break down combined nodes to single path, otherwise dasharray cannot properly be applied
                breakInputNodes = None
                breakInputNodes = self.breakContours(node, breakInputNodes)
                for breakInputNode in breakInputNodes:
                    createLinks(breakInputNode)
        else:
            self.msg('Please select some paths first.')
            return
        
if __name__ == '__main__':
    LinksCreator().run()