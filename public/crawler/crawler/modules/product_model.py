from datetime import datetime


class Product:
    def __init__(self, url, name, price, options, specifications, features, breadcrumbs, web_series, media, ratings):
        self.url = url
        self.name = name
        self.price = price
        self.options = options
        self.specifications = specifications
        self.features = features
        self.breadcrumbs = breadcrumbs
        self.web_series = web_series
        self.media = media
        self.ratings = ratings
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        self.scrape_date = datetime.utcnow().date().isoformat()

    def to_dict(self):
        return {
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'scrape_date': self.scrape_date,
            'url': self.url,
            'name': self.name,
            'price': self.price,
            'options': self.options,
            'specifications': self.specifications,
            'features': self.features,
            'breadcrumbs': self.breadcrumbs,
            'web_series': self.web_series,
            'media': self.media,
            'ratings': self.ratings
        }