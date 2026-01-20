from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, null=True, blank=True)
    image = models.URLField(max_length=500)

    # THÊM TRƯỜNG NGÀY NHẬP HÀNG
    import_date = models.DateField(
        verbose_name="Ngày nhập hàng",
        null=True,
        blank=True,
        help_text="Ngày sản phẩm được nhập vào kho"
    )

    expiry_date = models.DateField(
        verbose_name="Hạn sử dụng",
        null=True,
        blank=True
    )
    price = models.IntegerField()  # giá gốc
    discount_price = models.IntegerField(  # giá sau giảm
        null=True,
        blank=True
    )

    description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)

    # Nhóm đánh giá: các sản phẩm cùng review_group sẽ chia sẻ chung đánh giá
    review_group = models.SlugField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Các sản phẩm có cùng review_group sẽ chia sẻ chung đánh giá. VD: 'royal-canin-cho-cho'"
    )

    size_label = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Tên hiển thị cho nhóm Size (ví dụ 'Huong')"
    )

    # NEW: Sản phẩm liên quan do admin tự chọn
    related_products = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="related_to"
    )

    def __str__(self):
        return self.name

    def get_review_identifier(self):
        """
        Trả về identifier dùng cho review.
        Nếu có review_group thì dùng review_group (để nhiều sản phẩm chia sẻ chung review)
        Nếu không có thì dùng slug của chính nó
        """
        return self.review_group if self.review_group else self.slug

    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    is_expired.boolean = True
    is_expired.short_description = "Hết hạn?"

    # THÊM PHƯƠNG THỨC KIỂM TRA SẢN PHẨM MỚI
    def is_new_product(self):
        """
        Kiểm tra sản phẩm có phải là sản phẩm mới không.
        Sản phẩm mới: Thời gian sử dụng còn lại >= 1/2 tổng thời gian sử dụng
        """
        if not self.import_date or not self.expiry_date:
            return False

        today = timezone.now().date()

        # Tổng thời gian sử dụng của sản phẩm
        total_usage_time = (self.expiry_date - self.import_date).days

        # Thời gian sử dụng còn lại
        remaining_time = (self.expiry_date - today).days

        # Kiểm tra: thời gian còn lại >= 1/2 tổng thời gian
        if total_usage_time > 0:
            return remaining_time >= (total_usage_time / 2)

        return False

    is_new_product.boolean = True
    is_new_product.short_description = "Sản phẩm mới?"

    # THÊM PHƯƠNG THỨC LẤY % THỜI GIAN CÒN LẠI
    def get_freshness_percentage(self):
        """
        Tính % độ tươi của sản phẩm
        """
        if not self.import_date or not self.expiry_date:
            return None

        today = timezone.now().date()
        total_usage_time = (self.expiry_date - self.import_date).days
        remaining_time = (self.expiry_date - today).days

        if total_usage_time > 0:
            return int((remaining_time / total_usage_time) * 100)

        return 0

    # CHÍNH SÁCH GIẢM GIÁ TỰ ĐỘNG THEO HẠN SỬ DỤNG
    def get_expiry_discount_percent(self):
        """
        Tính % giảm giá tự động dựa trên thời gian sử dụng còn lại.
        
        Chính sách:
        - Sản phẩm gần hết hạn: thời gian còn lại < 1/2 tổng thời gian sử dụng và > 0
        - ≤ 3 tháng còn lại: Giảm 10%
        - ≤ 2 tháng còn lại: Giảm 20%
        - ≤ 1 tháng còn lại: Giảm 50%
        - Hết hạn (HSD ≤ ngày hiện tại): Không được bán (0%)
        """
        if not self.import_date or not self.expiry_date:
            return 0

        today = timezone.now().date()
        
        # Kiểm tra hết hạn
        if self.expiry_date <= today:
            return 0  # Sản phẩm hết hạn không được giảm giá
        
        # Tính tổng thời gian sử dụng và thời gian còn lại
        total_usage_time = (self.expiry_date - self.import_date).days
        remaining_time = (self.expiry_date - today).days
        
        # Kiểm tra có phải sản phẩm gần hết hạn không
        # (thời gian còn lại < 1/2 tổng thời gian)
        if total_usage_time > 0 and remaining_time >= (total_usage_time / 2):
            return 0  # Sản phẩm còn mới, không giảm giá
        
        # Áp dụng chính sách giảm giá theo thời gian còn lại
        # 1 tháng = 30 ngày
        if remaining_time <= 30:  # ≤ 1 tháng
            return 50
        elif remaining_time <= 60:  # ≤ 2 tháng
            return 20
        elif remaining_time <= 90:  # ≤ 3 tháng
            return 10
        
        return 0

    def is_near_expiry(self):
        """
        Kiểm tra sản phẩm có phải gần hết hạn không.
        Gần hết hạn: 0 < thời gian còn lại < 1/2 tổng thời gian sử dụng
        """
        if not self.import_date or not self.expiry_date:
            return False

        today = timezone.now().date()
        
        # Đã hết hạn
        if self.expiry_date <= today:
            return False
        
        total_usage_time = (self.expiry_date - self.import_date).days
        remaining_time = (self.expiry_date - today).days
        
        if total_usage_time > 0:
            return remaining_time < (total_usage_time / 2)
        
        return False

    is_near_expiry.boolean = True
    is_near_expiry.short_description = "Gần hết hạn?"

    def can_be_sold(self):
        """
        Kiểm tra sản phẩm có thể được bán không.
        Sản phẩm hết hạn (HSD ≤ ngày hiện tại) không được phép bán.
        """
        if not self.expiry_date:
            return True  # Sản phẩm không có HSD thì được bán
        
        today = timezone.now().date()
        return self.expiry_date > today

    can_be_sold.boolean = True
    can_be_sold.short_description = "Có thể bán?"


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Tự động tạo review_group từ tên nếu chưa có
        if not self.review_group and self.name:
            self.review_group = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        """
        Tính giá cuối cùng của sản phẩm theo thứ tự ưu tiên:
        1. Promotion (nếu có)
        2. Giảm giá tự động theo HSD (nếu gần hết hạn)
        3. Giảm giá thủ công (discount_price)
        4. Giá gốc
        """
        now = timezone.now()

        # 1️⃣ Ưu tiên promotion gắn trực tiếp cho sản phẩm
        promo = self.promotions.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()

        # 2️⃣ Fallback: promotion theo category
        if not promo:
            promo = self.category.promotions.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now
            ).first()

        # 3️⃣ Nếu có promotion → tính theo %
        if promo:
            return int(self.price * (100 - promo.discount_percent) / 100)

        # 4️⃣ Giảm giá tự động theo HSD (sản phẩm gần hết hạn)
        expiry_discount = self.get_expiry_discount_percent()
        if expiry_discount > 0:
            return int(self.price * (100 - expiry_discount) / 100)

        # 5️⃣ Không promotion và không gần hết hạn → dùng discount_price nếu có
        if self.discount_price is not None:
            return self.discount_price

        # 6️⃣ Cuối cùng → giá gốc
        return self.price

    def discount_percent(self):
        """
        Tính % giảm giá thực tế (bao gồm promotion, expiry discount, hoặc discount_price)
        """
        if self.final_price < self.price:
            return int((1 - self.final_price / self.price) * 100)
        return 0

    def get_related_products(self, limit=10):
        # 1. Ưu tiên sản phẩm admin gán thủ công
        manual = self.related_products.all()
        if manual.exists():
            return manual[:limit]

        # 2. Fallback: cùng thương hiệu
        same_brand = Product.objects.filter(
            brand=self.brand
        ).exclude(id=self.id)
        if same_brand.exists():
            return same_brand[:limit]

        # 3. Fallback: cùng category
        same_category = Product.objects.filter(
            category=self.category
        ).exclude(id=self.id)
        return same_category[:limit]

    def get_active_promotion(self):
        return self.promotions.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        ).first()

    def get_final_price(self):
        promo = self.get_active_promotion()
        if promo:
            return int(self.price * (100 - promo.discount_percent) / 100)
        return self.discount_price or self.price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    url = models.URLField(max_length=500)

    def __str__(self):
        return f"Image of {self.product.name}"


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
    size_name = models.CharField(max_length=255)
    price = models.IntegerField()

    def get_final_price(self):
        promo = self.product.get_active_promotion()
        if promo:
            return int(self.price * (100 - promo.discount_percent) / 100)
        return self.price

    def __str__(self):
        return f"{self.product.name} - {self.size_name}"


from django.db import models
from django.contrib.auth.models import User  # hoặc model User custom nếu bạn có


class ProductReview(models.Model):
    STAR_CHOICES = [(i, f"{i} sao") for i in range(1, 6)]

    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)  # nếu user không login
    rating = models.IntegerField(choices=STAR_CHOICES)

    #  THÊM
    sentiment = models.CharField(
        max_length=10,
        choices=[("tích cực", "Tích cực"), ("tiêu cực", "Tiêu cực")],
        null=True,
        blank=True
    )
    is_spam = models.BooleanField(default=False)

    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=True)  # dùng nếu muốn duyệt trước khi hiển thị

    class Meta:
        ordering = ["-created_at"]  # hiển thị mới nhất trước

    def __str__(self):
        user_info = self.user.username if self.user else self.email
        return f"{user_info} - {self.product.name} ({self.rating} sao)"


from django.db import models
from django.contrib.auth.models import User


class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="wishlisted_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} ❤️ {self.product.name}"


# models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError


class Promotion(models.Model):
    name = models.CharField(max_length=255)
    discount_percent = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)


    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="promotions"
    )



    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="promotions"
    )

    def clean(self):
        pass

    def is_valid_now(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def __str__(self):
        return self.name


from django.db.models import Q

def get_valid_products_for_promotion(promotion):
    # min_date = timezone.now().date() + timedelta(days=promotion.min_expiry_days)
    # Logic cũ dùng min_expiry_days, giờ bỏ đi -> lấy hết hoặc tùy logic mới
    # Hiện tại chỉ return product theo category
    return Product.objects.filter(
        category__in=promotion.categories.all()
    )
