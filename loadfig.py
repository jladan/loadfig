"""
Functions to parse a MATLAB .fig file

According to posts online (e.g. https://github.com/rsnape/OpenMatlabFigureInOctave), .fig files are really just a special .mat file.

Figures are simply a tree of structures:

figstruct : {
    type : string,
    handle : number,
    properties : [struct],
    children : [figstruct],
    special : NO IDEA, probably [struct]
}

Because MATLAB defaults to column vectors, numpy represents the lists as ndarrays with shape (N,1). Same thing for any list-type property.

The tree (in types) typically goes something like:
    figure
      |- axes
      |    |- surface
      |    |- graph2d.lineseries
      |    |- specgraph.errorbarseries
      |- legend
      |- scribe.colorbar
      |- scribe.scribeaxes

And I don't know what else
"""

from scipy.io import loadmat
import numpy as np

def loadfig(fname):
    top = loadmat(fname)
    fig = Figure(top['hgS_070000'][0,0])
    return fig

class Figure():
    def __init__(self, fig):
        if fig['type'][0] != 'figure':
            raise ValueError('not a figure (wrong type)')

        self.children = []
        for c in fig['children'][:,0]:
            if c['type'][0] == 'axes':
                self.children.append(Axes(c))
        props = fig['properties'][0,0]
        self.properties = dict(zip(props.dtype.names, props))

class Axes():
    def __init__(self, ax):
        if ax['type'][0] != 'axes':
            raise ValueError('not an axes object')

        self.children = []
        for c in ax['children'][:,0]:
            if c['type'][0] == 'specgraph.errorbarseries':
                self.children.append(ErrorBar(c))
        props = ax['properties'][0,0]
        self.properties = dict(zip(props.dtype.names, props))

class ErrorBar():
    def __init__(self, eb):
        props = eb['properties'][0,0]
        self.properties = {}
        self.properties['label'] = props['DisplayName'][0]
        self.properties['x'] = props['XData'][:,0]
        self.properties['y'] = props['YData'][:,0]
        self.properties['yerr'] = np.stack([
                props['LData'][:,0],
                props['UData'][:,0]])
        self.properties['color'] = props['Color'][0,:]
