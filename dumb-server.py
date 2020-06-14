import json
from shapely.geometry import shape, Point
import os
from shapely.strtree import STRtree
import uuid
from shapely.geometry import mapping, shape

DATA_DIR = 'data'

shapes = []

for file in os.listdir(DATA_DIR):
  if '.geojson' not in file:
    continue
  f = open(os.path.join(DATA_DIR, file))
  js = json.load(f)
  for feature in js['features']:
    s = shape(feature['geometry'])
    s.properties = feature['properties']
    shapes.append(s)


tree = STRtree(shapes)



# # check each polygon to see if it contains the point
#     if polygon.contains(point):
#         print('Found containing polygon:', feature)


from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def lookup():
    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))
    point = Point(lng, lat)
    return {'data': [o.properties for o in tree.query(point)]}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

