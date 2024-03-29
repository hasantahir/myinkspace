#! /usr/bin/env python3
#
# Este script dibuja el perfil exterior de corte la caja en un solo 
# path cerrado y añade despues los otros flejes necesarios con colores
# diferentes para identificarlos.
#     rojo > para cortes y perfil exterior
#     azul > para hendidos
#     verde > para taladros
#     amarillo > medios cortes
#
# TODO:
#     agregar opción de dibujo en cm/in
#     mover dibujo al centro del documento
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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

__version__ = "0.2"

import inkex

class GenerarEstuche(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--width", type=float, default=25.0, help="Ancho de la caja")
        pars.add_argument("--height", type=float, default=25.0, help="Alto de la caja")
        pars.add_argument("--depth", type=float, default=25.0, help="Largo de la caja")
        pars.add_argument("--unit", default="mm", help="Tipo de unidades")

    def effect(self):
        centro_ancho_documento = self.svg.unittouu(self.document.getroot().get('width'))/2
        centro_alto_documento = self.svg.unittouu(self.document.getroot().get('height'))/2

        medida_pestana1=2

        ancho_caja = self.svg.unittouu(str(self.options.width) + self.options.unit)
        alto_caja = self.svg.unittouu(str(self.options.height) + self.options.unit)
        largo_caja = self.svg.unittouu(str(self.options.depth) + self.options.unit)

        if self.options.unit=="cm":
            medida_pestana1=0.2
			
        if self.options.unit=='in':
            medida_pestana1=0.0787

        medida1_pestanas_laterales=self.svg.unittouu(str(medida_pestana1) + self.options.unit)

        id_caja = self.svg.get_unique_id('bandeja-4P')
        group = self.svg.get_current_layer().add(inkex.Group(id=id_caja))
        estilo_linea_cortes = {'stroke': '#FF0000', 'fill': 'none', 'stroke-width': str(self.svg.unittouu('1px'))}
        estilo_linea_hendidos = {'stroke': '#0000FF', 'fill': 'none', 'stroke-width': str(self.svg.unittouu('1px'))}
        estilo_linea_taladros = {'stroke': '#00FF00', 'fill': 'none', 'stroke-width': str(self.svg.unittouu('1px'))}
        estilo_linea_medioscortes = {'stroke': '#00FFFF', 'fill': 'none', 'stroke-width': str(self.svg.unittouu('1px'))}

        # line.path --> M = coordenadas absolutas
        # line.path --> l = dibuja una linea desde el punto actual a las coordenadas especificadas
        # line.path --> c = dibuja una curva beizer desde el punto actual a las coordenadas especificadas
        # line.path --> q = dibuja un arco desde el punto actual a las coordenadas especificadas usando un punto como referencia
        # line.path --> Z = cierra path
        
        #Perfil Exterior de la caja
        line = group.add(inkex.PathElement(id=id_caja + '-perfil-exterior'))
        line.path = [
			['M', [0, 0]],
			['l', [alto_caja,0]],
			['l', [ancho_caja,0]],
			['l', [alto_caja,0]],
			['l', [0,alto_caja-medida1_pestanas_laterales]],
			['l', [0-(alto_caja-medida1_pestanas_laterales),0]],
			['l', [0-medida1_pestanas_laterales,medida1_pestanas_laterales]],
			['l', [alto_caja,0]],
			['l', [0,largo_caja]],
			['l', [0-alto_caja,0]],
			['l', [medida1_pestanas_laterales,medida1_pestanas_laterales]],
			['l', [alto_caja-medida1_pestanas_laterales,0]],
			['l', [0,alto_caja-medida1_pestanas_laterales]],
			['l', [0-(alto_caja),0]],
			['l', [0-(ancho_caja),0]],
			['l', [0-(alto_caja),0]],
			['l', [0,0-(alto_caja-medida1_pestanas_laterales)]],
			['l', [alto_caja-medida1_pestanas_laterales,0]],
			['l', [medida1_pestanas_laterales,0-medida1_pestanas_laterales]],
			['l', [0-(alto_caja),0]],
			['l', [0,0-largo_caja]],
			['l', [alto_caja,0]],
			['l', [0-medida1_pestanas_laterales,0-medida1_pestanas_laterales]],
			['l', [0-(alto_caja-medida1_pestanas_laterales),0]],
			['Z', []]
        ]
        line.style = estilo_linea_cortes
        
        #Hendidos
        line = group.add(inkex.PathElement(id=id_caja + '-perfil-hendidos-1'))
        line.path = [
			['M', [alto_caja,0]],
			['l', [0,largo_caja+(alto_caja*2)]]
		]
        line.style = estilo_linea_hendidos

        line = group.add(inkex.PathElement(id=id_caja + '-perfil-hendidos-2'))
        line.path = [
			['M', [ancho_caja+alto_caja,0]],
			['l', [0,largo_caja+(alto_caja*2)]]
		]
        line.style = estilo_linea_hendidos
        
        line = group.add(inkex.PathElement(id=id_caja + '-perfil-hendidos-3'))
        line.path = [
			['M', [alto_caja,alto_caja]],
			['l', [ancho_caja,0]]
		]
        line.style = estilo_linea_hendidos
        
        line = group.add(inkex.PathElement(id=id_caja + '-perfil-hendidos-4'))
        line.path = [
			['M', [alto_caja,alto_caja+largo_caja]],
			['l', [ancho_caja,0]]
		]
        line.style = estilo_linea_hendidos
        
        line = group.add(inkex.PathElement(id=id_caja + '-perfil-hendidos-5'))
        line.path = [
			['M', [alto_caja,alto_caja]],
			['l', [0-alto_caja,alto_caja]]
		]
        line.style = estilo_linea_hendidos
        
        line = group.add(inkex.PathElement(id=id_caja + '-perfil-hendidos-6'))
        line.path = [
			['M', [alto_caja+ancho_caja,alto_caja]],
			['l', [alto_caja,alto_caja]]
		]
        line.style = estilo_linea_hendidos
 
        line = group.add(inkex.PathElement(id=id_caja + '-perfil-hendidos-7'))
        line.path = [
			['M', [alto_caja+ancho_caja,alto_caja+largo_caja]],
			['l', [alto_caja,0-alto_caja]]
		]
        line.style = estilo_linea_hendidos
        
        line = group.add(inkex.PathElement(id=id_caja + '-perfil-hendidos-8'))
        line.path = [
			['M', [alto_caja,alto_caja+largo_caja]],
			['l', [0-alto_caja,0-alto_caja]]
		]
        line.style = estilo_linea_hendidos

if __name__ == '__main__':
    GenerarEstuche().run()