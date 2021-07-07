import json
class GoodsManager:
    def __init__(self, path='lib/goods.json'):
        self.path = path
        self.data = json.load(open(path, 'r'))

    def revise_goods(self, i, name, filename, description, limit, expires):
        self.data.append({
            'items': i,
            'name': name,
            'img': filename + '.jpg',
            'description': description,
            'limit': limit,
            'left': limit,
            'expires': expires,
        })
        self._save()

    def new_order(self, items, number):
        self.data[items]['left'] -= number
        self._save()

    def _save(self):
        json.dump(self.data, open(self.path, 'w'))

    def clear(self):
        self.data = []