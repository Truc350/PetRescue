from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def get_home(request):
    return render(request, 'home.html')  # tra ve trang my_app trong trang web
def getChatWithAI(request):
    return render(request, 'frontend/chatWithAI.html')
def getFooter(request):
    return render(request, 'frontend/footer.html')
def getHeader(request):
    return render(request, 'frontend/header.html')
def getLogin(request):
    return render(request, 'frontend/login.html')
def getRegister(request):
    return render(request, 'frontend/register.html')
def getForgotPassword(request):
    return render(request, 'frontend/forgot-password.html')
def getPayment(request):
    return render(request, 'frontend/payment.html')
def getPaymentInfor(request):
    return render(request, 'frontend/delivery-infor.html')
def getCategory(request):
    return render(request, 'frontend/category.html')
def getCategoryManage(request):
    return render(request, 'frontend/admin/category-manage.html')
def getCustomerManage(request):
    return render(request, 'frontend/admin/customer-manage.html')
def getProductManagement(request):
    return render(request, 'frontend/admin/product-management.html')
def getProfileAdmin(request):
    return render(request, 'frontend/admin/profileAdmin.html')
def getDogKibbleView(request):
    return render(request, 'frontend/DogKibbleView.html')
def getPersonal(request):
    return render(request, 'frontend/personal-page.html')
def getHomePage(request):
    return render(request, 'frontend/homePage.html')
def getDashBoard(request):
    return render(request, 'frontend/admin/dashboard.html')
def getHealthDog(request):
    return render(request, 'frontend/health-dog.html')
def getPolicy(request):
    return render(request, 'frontend/policy-purchases.html')
def getCatFood(request):
    return render(request, 'frontend/cat-food.html')
def getHealthCat(request):
    return render(request, 'frontend/health-cat.html')
def getCatToilet(request):
    return render(request, 'frontend/cat-toilet.html')
def getPromotion(request):
    return render(request, 'frontend/promotion.html')
def getDetailProduct(request):
    return render(request, 'frontend/detailProduct.html')
def getPromotionManage(request):
    return render(request, 'frontend/admin/promotion-manage.html')
def getStatistic(request):
    return render(request, 'frontend/admin/statistics.html')
def getDogHygiene(request):
    return render(request, 'frontend/dogHygiene.html')
