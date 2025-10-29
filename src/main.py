import json
import zlib
import base64
from PIL import Image

from utils import generate_signal_id


class BlueprintJson:
    def __init__(self):
        self.colors = []
        self.blueprint_json = {}
        self.entity_counter = 1

    def _get_current_version(self) -> int:
        return (1 << 48) | (69 << 32) | (0 << 16) | 2
    
    def _seed_json(self) -> None:
        self.blueprint_json = {
            "blueprint": {
                "icons": [
                    {
                        "signal": {
                            "name": "constant-combinator"
                        },
                        "index": 1
                    }
                ],
                "entities": [],
                "wires": [],
                "item": "blueprint",
                "version": self._get_current_version(),
            }
        }
    
    def _create_combinator(self, colors: list[int], y: int) -> int:
        filters = []

        for i, color in enumerate(colors):
            filters.append({
                "index": i + 1,
                "type": "virtual",
                "name": f"signal-{generate_signal_id(i)}",
                "quality": "normal",
                "comparator": "=",
                "count": color
            })

        entity = {
            "entity_number": self.entity_counter,
            "name": "constant-combinator",
            "position": {"x": 0, "y": y},
            "control_behavior": {
                "sections": {
                    "sections": [
                        {
                            "index": 1,
                            "filters": filters
                        }
                    ]
                }
            }
        }
        self.blueprint_json["blueprint"]["entities"].append(entity)
        self.entity_counter += 1

        return self.entity_counter - 1
    
    def _create_line(self, colors: list[int], y: int) -> None:
        prev_entity_number = self._create_combinator(colors, y)
        x = 1

        for i, color in enumerate(colors):
            entity = {
                "entity_number": self.entity_counter,
                "name": "small-lamp",
                "position": {"x": x, "y": y},
                "control_behavior": {
                    "use_colors": True,
                    "rgb_signal": {
                        "type": "virtual",
                        "name": f"signal-{generate_signal_id(i)}"
                    },
                    "color_mode": 2
                },
                "always_on": True
            }

            self.blueprint_json["blueprint"]["wires"].append([prev_entity_number, 1, self.entity_counter, 1])
            self.blueprint_json["blueprint"]["entities"].append(entity)
            prev_entity_number = self.entity_counter
            self.entity_counter += 1
            x += 1

    
    def generate_blueprint_json(self) -> dict[str]:
        self._seed_json()
        
        for y, row_colors in enumerate(self.colors):
            self._create_line(colors=row_colors, y=y)
        
        return self.blueprint_json


class Blueprint:
    def __init__(self, colors: list[list[int]]):
        self.colors = colors
        self.blueprint = BlueprintJson()

    def encode(self) -> str:
        self.blueprint.colors = self.colors

        json_str = json.dumps(self.blueprint.generate_blueprint_json(), separators=(",", ":"))
        compressed = zlib.compress(json_str.encode("utf-8"))
        encoded = base64.b64encode(compressed).decode("utf-8")
        return "0" + encoded


class ImageConvertor:
    def __init__(self, path: str):
        self.path = path
        self.image = None
        self.pixels = None
        self.colors = []
    
    def _load_image(self) -> None:
        self.image = Image.open(self.path)
        if self.image.mode != 'RGB':
            self.image = self.image.convert('RGB')
        self.pixels = self.image.load()
    
    def get_colors(self):
        self._load_image()
        width, height = self.image.size

        for y in range(height):
            row_colors = []
            for x in range(width):
                r, g, b = self.pixels[x, y]
                row_colors.append((r << 16) + (g << 8) + b)
            self.colors.append(row_colors)
        
        return self.colors
                

def main() -> None:
    path = input("Enter the path to file: ")
    colors = ImageConvertor(path).get_colors()
    print(Blueprint(colors).encode())


if __name__ == "__main__":
    main()