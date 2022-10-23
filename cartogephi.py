import argparse
import codecs
from collections import defaultdict
from encodings import search_function
import json
import xml.sax

from scipy.spatial import ConvexHull

class ScalarBound:
    def __init__(self,_min=float("inf"),_max=-float("inf")) -> None:
        self.min = _min
        self.max = _max
    def update(self, value:float) -> None:
        self.min = min(self.min,value)
        self.max = max(self.max,value)

    def zeroBased(self) :
        return ScalarBound(
            self.min -self.min,
            self.max - self.min
        )

    def __repr__(self) -> str:
        return f'[{self.min},{self.max}]'

class Vec2Bounds:
    def __init__(self,x=ScalarBound(),y=ScalarBound()) -> None:
        self.x = x
        self.y = y
    def update(self,x:float,y:float) -> None:
        self.x.update(x)
        self.y.update(y)
    def zeroBased(self) :
        return Vec2Bounds(
            self.x.zeroBased(),
            self.y.zeroBased()
        )
    def __repr__(self) -> str:
        return f'<x:{self.x},y:{self.y}>'

class CartogephiHandler(xml.sax.ContentHandler):
    def __init__(self, modularity_column, search_column):
        self.bounds = Vec2Bounds()
        self.index = dict()
        self.current = None
        self.modularity = defaultdict(list)
        self.modularity_color = dict()
        self.modularity_column = modularity_column
        self.search_column = search_column
    # Handle startElement
    def startElement(self, tagName, attrs):
        if "node" == tagName:
            self.current = {'id':attrs['id'],'label':attrs['label']}
            if self.search_column == 'id':
                self.current['search_column'] = attrs['id']
            elif self.search_column == 'label':
                self.current['search_column'] = attrs['label']
        if "attvalue" == tagName and attrs['for'] == self.modularity_column:
            self.current['modularity'] = attrs['value']
        if "attvalue" == tagName and attrs['for'] == self.search_column:
            self.current['search_column'] = attrs['value']
        if "viz:position" in tagName:
            x, y= float(attrs['x']),float(attrs['y'])
            self.bounds.update(x,y)
            self.index[self.current.get('search_column')] = {
                "x":x,
                "y":y,
                "label":self.current['label']
            }
            self.modularity[self.current['modularity']].append([y,x])
        if "viz:color" in tagName:
            if not self.modularity_color.get(self.current['modularity']):
                self.modularity_color[self.current['modularity']]=(
                    float(attrs['r']),
                    float(attrs['g']),
                    float(attrs['b'])
                )

def main(gexf_file, img_file, modularity_column, search_column):
    handler = CartogephiHandler(modularity_column, search_column)
    xml.sax.parse(gexf_file, handler)
    

    # Compute leaflet configuration for the map

    ## Compute max size side
    zeroBased = handler.bounds.zeroBased()
    maxSide = max(zeroBased.y.max,zeroBased.x.max)

    ## Add extra size 
    handler.bounds.x.min -= abs(zeroBased.x.max - maxSide)/2
    handler.bounds.y.min -= abs(zeroBased.y.max - maxSide)/2

    handler.bounds.x.max += abs(zeroBased.x.max - maxSide)/2
    handler.bounds.y.max += abs(zeroBased.y.max - maxSide)/2

    # Compute modularity
    modularities = {}
    for k, v in handler.modularity.items():
        if len(v)>=5 :
            hull = ConvexHull(v)
            modularities[k] = {
                'hull':[v[h] for h in hull.vertices],
                'color': handler.modularity_color[k]
            }

    # File data
    cartogephi_data = {
        'index': handler.index,
        'img_file': img_file,
        'modularities': modularities,
        'leaflet_config': [[handler.bounds.y.min,handler.bounds.x.min],[handler.bounds.y.max,handler.bounds.x.max]]
    }
    with codecs.open("cartogephi.json","w","UTF-8") as f:
        json.dump(cartogephi_data,f)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool to use gexf and png files from Gephi as a Leaflet website')
    parser.add_argument('gexf_file', type=str,  help='Gexf file')
    parser.add_argument('img_file', type=str,  help='Image file')
    parser.add_argument('--modularity', default='modularityclasses', help='modularity (default: modularityclasses)')
    parser.add_argument('--search', default='id', help='searchable column (default: id)')
    args = parser.parse_args()
    main(args.gexf_file,args.img_file, args.modularity, args.search)