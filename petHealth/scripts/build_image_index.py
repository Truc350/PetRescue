from my_app.models_Product import ProductImage
from my_app.services.feature import extract_feature_from_url
import numpy as np

features, urls = [], []

for img in ProductImage.objects.all():
    try:
        f = extract_feature_from_url(img.url)
        features.append(f)
        urls.append(img.url)
        print("OK:", img.url)
    except Exception as e:
        print("FAIL:", img.url, e)

np.save("library_features.npy", np.array(features, dtype=np.float32))
np.save("library_urls.npy", np.array(urls))
