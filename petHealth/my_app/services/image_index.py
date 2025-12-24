import numpy as np
from django.conf import settings
import os

library_features = np.load(os.path.join(settings.BASE_DIR, "library_features.npy"))
library_urls = np.load(os.path.join(settings.BASE_DIR, "library_urls.npy"))
