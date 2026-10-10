"""Contract checks for artist-authored content, not implementation snapshots."""
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from import_svg import compile_svg, inside

class ImporterTests(unittest.TestCase):
    def compile(self,body,cluster=0):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'art.svg';target=Path(folder)/'art.json'
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'+body+'</svg>')
            return compile_svg(source,target,cluster)

    def test_cubic_quadratic_and_relative_paths(self):
        data=self.compile('<path fill="#FF00AA" d="M10 10 C30 0 70 0 90 10 L90 80 Q50 100 10 80 Z"/><path fill="#00AABB" d="m20 30 l20 0 v20 h-20 z"/>')
        self.assertEqual(len(data['shapes']),2)
        for shape in data['shapes']:self.assertTrue(inside(shape['label'],shape['points']))
        self.assertFalse(inside(data['shapes'][0]['label'],data['shapes'][1]['points']))

    def test_near_colors_cluster_but_distinct_colors_do_not(self):
        data=self.compile('<circle cx="20" cy="20" r="10" fill="#FF00AA"/><circle cx="50" cy="50" r="10" fill="#FE00AA"/><circle cx="80" cy="80" r="10" fill="#00AABB"/>',3)
        self.assertEqual(len(data['palette']),2)
        self.assertEqual(data['shapes'][0]['color'],data['shapes'][1]['color'])

    def test_hidden_shape_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'visible interior'):
            self.compile('<circle cx="50" cy="50" r="10" fill="#FF00AA"/><circle cx="50" cy="50" r="30" fill="#00AABB"/>')

    def test_unsupported_open_arc_and_compound_paths_rejected(self):
        for path in ['M0 0 L80 0 L40 80','M10 10 A30 30 0 0 0 80 80 Z','M0 0 L50 0 L30 50 Z M10 10 L20 10 L15 20 Z']:
            with self.subTest(path=path),self.assertRaises(ValueError):
                self.compile(f'<path fill="#FF00AA" d="{path}"/>')

    def test_transform_requires_explicit_flattening(self):
        with self.assertRaisesRegex(ValueError,'transform'):
            self.compile('<g transform="translate(20 20)"><circle r="10" fill="#FF00AA"/></g>')

    def test_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(ValueError,'unique'):
            self.compile('<circle id="a" cx="20" cy="20" r="10" fill="#FF00AA"/><circle id="a" cx="60" cy="60" r="10" fill="#00AABB"/>')

    def test_all_shipped_levels_have_stable_ids_and_valid_palettes(self):
        files=list((Path(__file__).resolve().parents[1]/'resources/levels').glob('*.json'))
        self.assertEqual(len(files),14)
        for file in files:
            data=json.loads(file.read_text());ids=[x['id'] for x in data['shapes']]
            self.assertEqual(len(ids),len(set(ids)))
            for shape in data['shapes']:
                self.assertIn(shape['color'],range(len(data['palette'])))
                self.assertGreater(shape['label_radius'],2)

if __name__=='__main__': unittest.main()
