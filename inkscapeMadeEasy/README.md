This set of python modules is intended to extend Aaron Spike's inkex.py module, adding functions to help the
development of new extensions for Inkscape <https://inkscape.org>.

# inkscapeMadeEasy

This set of python modules is intended to extend Aaron Spike's inkex.py module, adding functions to help the
development of new extensions for Inkscape <https://inkscape.org>.

Here you will find methods and classes to deal with drawings, styles, markers, texts, plots, etc. It is a
work-in-progress project and new features will be added in the future. However, there is no roadmap right now.

<img src="docs/imagesDocs/samples_01.png" alt="Drawing" style="width: 200px;"/>

Usage
=====

**InskcapeMadeEasy is not an end-user Inkscape extension by itself**. The objective is to provide easier backstage
functions and modules to facilitate the development of Inkscape extensions.

For end-user extensions that employ InskcapeMadeEasy, please refer to my other repositories on
GitHub (more to come soon). They provide many examples of how to use inkscapeMadeEasy:

  - **createMarkers**           <https://github.com/fsmMLK/inkscapeCreateMarkers>

  - **cartesianAxes2D**         <https://github.com/fsmMLK/inkscapeCartesianAxes2D>

  - **cartesianPlotFunction2D** <https://github.com/fsmMLK/inkscapeCartesianPlotFunction2D>

  - **cartesianPlotData2D**     <https://github.com/fsmMLK/inkscapeCartesianPlotData2D>

  - **cartesianStemPlot**       <https://github.com/fsmMLK/inkscapeCartesianStemPlot>

  - **polarAxes2D**             <https://github.com/fsmMLK/inkscapePolarAxes2D>

  - **logicGates**              <https://github.com/fsmMLK/inkscapeLogicGates>

  - **circuitSymbols**          <https://github.com/fsmMLK/inkscapeCircuitSymbols>

  - **wavedromScape**          <https://github.com/fsmMLK/wavedromScape>

  - **dimensions**              <https://github.com/fsmMLK/inkscapeDimensions>

  - **SlopeField**              <https://github.com/fsmMLK/inkscapeSlopeField>

  - **BodePlot**                <https://github.com/fsmMLK/inkscapeBodePlot>

  - **Spirograph**              <https://github.com/fsmMLK/inkscapeSpirograph>

## History and Objectives

Historically, this project started as a way to help myself while creating extensions, namely focusing on scientific
/academic diagrams and graphs. In the academy, we prepare plots and diagrams very often to  explain concepts or
 results for lectures, seminars, congresses and scientific articles.

There are many consecrated mathematical tools that can produce them, e.g., Gnuplot, Octave, Matlab, R, etc. They all
can produce nice plots. However, it might be a little cumbersome when we want to add other elements to these plots,
like text, comments, arrows, etc. These packages have tools to do it but they are cumbersome to use. A better
approach would be using proper graphic software.

One possible approach is to export these plots as raster images and use raster graphic software to produce the
annotations, like Gimp. I prefer to have the plots in a vector graphic format to be able to produce, if needed, raster
images with different resolutions without the fear of having a heavily pixelated image. For this, Inkscape is very
 sound. 

Unfortunately, exporting plots as vector graphics is not always successful in the sense that the resulting
document is quite "dirty" (unorganized groups, isolated elements, etc.). Therefore I decided to make my
plotting/diagram tools for Inkscape.

In the process of creating these tools, I noticed that many of the low-level classes and methods used to manipulate
elements of the svg file could be grouped in a general-purpose set of core modules that extended inkex.py module.
**inkscapeMadeEasy** was born! The core modules I created do not intend to provide an extensive array of methods and
classes to cover all possibilities of manipulations/transformations, and drawing. These modules were created and
 expanded as I felt the necessity to have new methods to help my workflow. Nevertheless, the number of methods
  created allows many possibilities and is still under development so new features can (will) appear in future versions.

**Obs:** Since it is not very easy to find documentation of other Inkscape modules, there might be other modules with
similar/better features that I was not aware of when I was producing my extensions.

Enough mumbo-jumbo. Let's start! =D


# Documentation

You can find the main documentation page here <https://fsmmlk.github.io/inkscapeMadeEasy/>. I tried to make it useful to everyone by adding as many examples as possible. Check it out! =D

# Report issues

This is a work-in-progress project. Please report issues with the modules or documentation.
