import json,tempfile,unittest
from pathlib import Path
from PIL import Image
import numpy as np
from fontmagic.common import CANONICAL,mapping,validate_minimal,load_json
from fontmagic.images import components

def compose(a,b):
    A=np.array(a,float).reshape(3,3); B=np.array(b,float).reshape(3,3); return A@B
def image_to_font(x,y,height,scale,tx,ty): return (tx+x*scale,ty+(height-y)*scale)

class CoreTests(unittest.TestCase):
 def test_transform_composition(self):
  got=compose([1,0,2,0,1,3,0,0,1],[2,0,0,0,2,0,0,0,1]); self.assertEqual(got[0,0],2); self.assertEqual(got[0,2],2)
 def test_coordinate_flip(self): self.assertEqual(image_to_font(4,2,10,2,1,3),(9,19))
 def test_unicode_maps(self):
  for enc in ('phoenician','hebrew','pua'): self.assertEqual(set(mapping(enc)),set(CANONICAL))
 def test_components_keep_drop_basis(self):
  a=np.full((10,10),255,np.uint8); a[1:3,1:3]=0; a[7:9,7:9]=0; self.assertEqual(len(components(Image.fromarray(a))),2)
 def test_schema_subset(self): self.assertTrue(validate_minimal({}, {"type":"object","required":["x"]}))
 def test_all_schemas_are_json_and_structural(self):
  root=Path(__file__).resolve().parents[1]
  for path in (root/'schemas').glob('*.schema.json'):
   schema=load_json(path); self.assertEqual(schema['type'],'object',path.name); self.assertIn('$schema',schema)
 def test_bbox_contract(self):
  c=components(Image.fromarray(np.pad(np.zeros((2,3),np.uint8),1,constant_values=255)))[0]; self.assertEqual(c['bbox'],[1,1,4,3])

if __name__=='__main__': unittest.main()
