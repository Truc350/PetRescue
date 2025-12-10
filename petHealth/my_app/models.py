from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, null=True, blank=True)
    image = models.URLField(max_length=500)

    price = models.IntegerField()                      # giá gốc
    discount_price = models.IntegerField(              # giá sau giảm
        null=True,
        blank=True
    )

    short_description = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def final_price(self):
        """Trả về giá cuối cùng: giá giảm hoặc giá gốc"""
        return self.discount_price if self.discount_price else self.price

    def discount_percent(self):
        """Tính % giảm tự động"""
        if self.discount_price:
            return int((1 - self.discount_price / self.price) * 100)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    url = models.URLField(max_length=500)

    def __str__(self):
        return f"Image of {self.product.name}"


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
    size_name = models.CharField(max_length=255)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.size_name}"
