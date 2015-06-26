# -*- coding: utf-8 -*-

"""
Made by Lars Solberg - 2015

We need to generate gliffy diagrams based on something. I wasnt able to find any import/export tool to do this, offline as we need.

Some of (mostly the uninteresting part of) the json is collapsed to keep readability.

This library is only implementing a very few bits of what Gliffy can give us. The plan was to implement more shapes and types
when we need it. Implementing all at once will be to much right now.. More will come :)

"""

import json
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

class ShapeException(Exception):
    pass

class Gliffy(object):
    gliffy_object_raw = {}
    current_node_id = 0
    embedded_resources_map = {}  # Name of resource mapped to the internal embeddedResources ID that gliffy uses.

    def __init__(self, debug=False, extra_libraries=[], embeddedResources=[]):
        logger.handlers = []  # In case we are doing multiple imports, reloading and so on.. Dont want double-logs

        if debug:
            lh = logging.StreamHandler()
            lh.setFormatter(logging.Formatter('%(levelname)s in %(funcName)s (line:%(lineno)d) - %(message)s'))
            logger.addHandler(lh)
            logger.setLevel(logging.DEBUG)
        else:
            logger.addHandler(logging.NullHandler())

        embeddedResourcesList = []
        embeddedResourcesCount = 0
        for e in embeddedResources:
            self.embedded_resources_map[e['name']] = embeddedResourcesCount
            embeddedResourcesList .append({
                "id": embeddedResourcesCount,
                "mimeType": e.get('mimeType', 'image/svg+xml'),
                "data": e.get('data'),
                "x": e.get('x', 0),
                "y": e.get('y', 0),
                "width": e.get('width', 64),
                "height": e.get('height', 64)
            })
            embeddedResourcesCount += 1
        embeddedResources = {'index': embeddedResourcesCount, 'resources': embeddedResourcesList}

        self.gliffy_object_raw = {
            'contentType': "application/gliffy+json", 'version': "1.3",
            'metadata': {
                'title': "untitled", 'revision': 0, 'exportBorder': False, 'loadPosition': "default",
                'libraries': [
                    "com.gliffy.libraries.flowchart.flowchart_v1.default",
                    "com.gliffy.libraries.basic.basic_v1.default",
                    "com.gliffy.libraries.swimlanes.swimlanes_v1.default",
                    "com.gliffy.libraries.images"
                ] + extra_libraries,
                'lastSerialized': 1432113247513
            },
            'embeddedResources': embeddedResources,
            'stage': {
                'objects': [], 'background': "#FFFFFF", 'width': 656, 'height': 175, 'maxWidth': 5000, 'maxHeight': 5000, 'nodeIndex': 0,
                'autoFit': True, 'exportBorder': False, 'gridOn': True, 'snapToGrid': True, 'drawingGuidesOn': True, 'pageBreaksOn': False, 'printGridOn': False,
                'printPaper': "LETTER", 'printShrinkToFit': False, 'printPortrait': True,
                'shapeStyles': {
                    'com.gliffy.shape.flowchart.flowchart_v1.default': {'fill': "#FFFFFF", 'stroke': "#333333", 'strokeWidth': 2}
                },
                'lineStyles': {'global': {}}, 'textStyles': {}, 'themeData': None, 'viewportType': "default", 'fitBB': {'min': {'x': 0, 'y': 0}, 'max': {'x': 0, 'y': 0}}
            }
        }

    def align(self, method):
        # Not yet implemented, but we need a way to align our objects once we have them all..
        if method == 'star':
            pass

    @property
    def _node_id(self):
        nid = self.current_node_id
        self.current_node_id += 1
        return nid

    @property
    def gliffy_json(self):
        self.gliffy_object_raw['stage']['nodeIndex'] = self.current_node_id
        return json.dumps(self.gliffy_object_raw, indent=2)

    def Item(self, obj):
        self.gliffy_object_raw['stage']['objects'].append(obj)
        return obj


    class GliffyObject(OrderedDict):
        def __init__(self, parent, args, kwargs):
            self.parent = parent  # We must be able to update parent data
            self.args = args
            self.kwargs = kwargs
            self.data = {}  # Storage for the data we generate
            self.apply()  # Generate the data

        def __repr__(self):
            return repr(self.data)

        def __getitem__(self, key):
            return self.data[key]

        def __setitem__(self, key, value):
            self.data[key] = value

        def __delitem__(self, key):
            del self.data[key]

        def __len__(self):
            return len(self.data)

        def __contains__(self, key):
            return key in self.data

        def __str__(self):
            return str(self.data)

        def __unicode__(self):
            return unicode(self.__str__())

        def __iter__(self):
            return iter(self.data)

        def keys(self):
            return self.data.keys()

        @property
        def _node_id(self):
            return self.parent._node_id

        def apply(self):
            # Needs to be overridden with the function that should create the json-data
            pass


    class TextObj(GliffyObject):
        def apply(self):
            self.data = {
                'x': 2, 'y': 0, 'rotation': 0, 'id': self._node_id, 'uid': None, 'width': 96, 'height': 14, 'lockAspectRatio': False, 'lockShape': False, 'order': "auto", 'hidden': False,
                'graphic': {
                    'type': "Text",
                    'Text': {
                        'tid': None, 'valign': "middle", 'overflow': "none",
                        'vposition': self.kwargs.get('vposition', 'none'), 'hposition': self.kwargs.get('hposition', 'none'),
                        'html': '<p style="text-align: center;"><span style="font-family: Arial; font-size: 12px; text-decoration: none;"><span style="text-decoration: none; line-height: 14px;" class="">{text}</span></span></p>'.format(text=self.args[0].encode('utf-8')),
                        'paddingLeft': 8, 'paddingRight': 8, 'paddingBottom': 8, 'paddingTop': 8, 'outerPaddingLeft': 6, 'outerPaddingRight': 6, 'outerPaddingBottom': 2, 'outerPaddingTop': 6
                    }
                },
                'children': None
            }
    def Text(self, *args, **kwargs):
        # We need to bring with us the instance of ourself.. Thats why we need this little factory.
        return self.TextObj(self, args, kwargs)


    class ConnectObj(GliffyObject):
        line_map = {
            'default': {
                'uid': 'com.gliffy.shape.basic.basic_v1.default.line',
                'graphic': {
                    'type': "Line",
                    'Line': {
                        'strokeWidth': 2, 'strokeColor': "#000000", 'fillColor': "none", 'dashStyle': None, 'startArrow': 0, 'endArrow': 0, 'startArrowRotation': "auto", 'endArrowRotation': "auto",
                        'ortho': True, 'interpolationType': "linear", 'cornerRadius': 10,
                        'lockSegments': {},

                        # FIXME
                        # There is no way of (nor should we) calculate this. It defines the path a line is taking
                        # in the diagram. If we define it to something "random", like now, the Gliffy editor will
                        # show it where we define it, but recalculate it to the correct values once we actually
                        # click (or select), the line inside the editor. Defining this as an empty list, None, or undefined
                        # wont to the trick either. Gliffy gives us a 500 error if it cant be found.
                        # Currently in a chat with Gliffy to see if we can find a better way :)
                        'controlPath': [[0, -0.5], [50, -0.5], [100, -0.5], [150, -0.5]]
                    }
                }
            }
        }

        def apply(self):
            from_obj = self.args[0]
            to_obj = self.args[1]
            line_info = self.line_map[self.kwargs.get('style', 'default')]

            constraints = {
                'constraints': [],
                'startConstraint': {'type': "StartPositionConstraint", 'StartPositionConstraint': {'nodeId': from_obj['id'], 'px': 1, 'py': 0.5}},
                'endConstraint': {'type': "EndPositionConstraint", 'EndPositionConstraint': { 'nodeId': to_obj['id'], 'px': 0, 'py': 0.5}}
            }

            self.data = {
                'x': 100, 'y': 100, 'rotation': 0, 'id': self._node_id, 'uid': line_info['uid'],
                'width': 151, 'height': 64, 'lockAspectRatio': False, 'lockShape': False, 'order': 4, 'hidden': False,
                'graphic': line_info['graphic'], 'constraints': constraints,
                'children': None, 'linkMap': []
            }

            self.parent.Item(self.data)
    def Connect(self, *args, **kwargs):
        return self.ConnectObj(self, args, kwargs)


    class ShapeObj(GliffyObject):
        # We are only using shape_map to map the 'uid' and 'graphic' field of the shape.
        # The rest of the shape is added in apply()
        shape_map = {}

        def __init__(self, parent, args, kwargs):
            # We need access to 'self' to generate this shape_map, thats why this shape_map is in __init__
            self.shape_map = {
                'svg': {
                    'uid': 'com.gliffy.shape.basic.basic_v1.default.svg',
                    'graphic': {
                        'type': 'Svg',
                        'Svg': {
                            'embeddedResourceId': 0, # We will replace this in apply()
                            'strokeWidth': 2, 'strokeColor': '#000000', 'dropShadow': True, 'shadowX': 5, 'shadowY': 5
                        }
                    },
                },
                'process': {
                    'uid': 'com.gliffy.shape.flowchart.flowchart_v1.default.process',
                    'graphic': {
                        'type': 'Shape',
                        'Shape': {
                            'tid': 'com.gliffy.stencil.rectangle.basic_v1', 'strokeWidth': 2, 'strokeColor': "#333333", 'fillColor': "#FFFFFF", 'gradient': False, 'dropShadow': False, 'state': 0, 'shadowX': 0, 'shadowY': 0,'opacity': 1
                        }
                    }
                },
            }
            super(self.__class__, self).__init__(parent, args, kwargs)

        def apply(self):
            shape = self.args[0]
            shape_info = self.shape_map.get(shape, None)
            if shape_info is None:
                raise ShapeException('Invalid shape. "{shape}" not in "{valid_shapes}"'.format(shape=shape, valid_shapes=','.join(self.shape_map.keys())))

            if shape == 'svg':
                try:
                    erid = self.parent.embedded_resources_map[self.kwargs['shape_image_name']]
                except KeyError:
                    raise ShapeException('Unable to find a shape with name {shape_image_name} in embedded resources. Valid shapes are "{valid_shape_names}"'.format(shape_image_name=kwargs['shape_image_name'], valid_shape_names=','.join(self.parent.embedded_resources_map.keys())))
                shape_info['graphic']['Svg']['embeddedResourceId'] = erid

            children = self.kwargs.get('children', [])
            text = self.kwargs.get('text', None)
            if text:
                # Make it easier to create objects with text..
                # Defining "children" to create text on an object is not that logical :)
                children.append(text)

            import random
            x = random.randint(1,800)
            y = random.randint(1,800)

            self.data = {
                'id': self._node_id, 'uid': shape_info['uid'], 'graphic': shape_info['graphic'], 'children': children, 'linkMap': [],
                'x': x, 'y': y, 'rotation': self.kwargs.get('rotation', 0),
                'width': self.kwargs.get('width', 100), 'height': self.kwargs.get('height', 100),
                'lockAspectRatio': self.kwargs.get('lockAspectRatio', False), 'lockShape': self.kwargs.get('lockShape', False),
                'order': self.kwargs.get('order', 1), 'hidden': self.kwargs.get('hidden', False)
            }
    def Shape(self, *args, **kwargs):
        return self.ShapeObj(self, args, kwargs)
