"""MCE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.conf.urls.static import static
from django.conf import settings
from .views import RegisterAPI
from .views import SignInAPI
from knox import views as knox_views
from django.urls import path
from region import views
from theme.views import ThemeCreate
from theme.views import TopicCreate
from theme.views import CardsCreate
from theme.views import CardsTitleCreate
from theme.views import ThemeTopicCreate
from theme.views import ThemeGetOne
from theme.views import TopicGetOne
from theme.views import CardGetOne
from theme.views import CardTitleGetOne
from theme.views import ThemeTopicListCreate
from theme.views import ThemeTopicCardList
from theme.views import ThemeIdTopicGet
from theme.views import ThemeIdTopicUpdate
from theme.views import ThemeIdTopicFormView
from theme.views import CardCartitleCreate
from theme.views import CardCartitleUpdate
from theme.views import CardCartitleForm
from theme.views import CardTitleList
from theme.views import CardTitleListView
from theme.views import CardTitleListViewItem
from theme.views import CardTitleListViewFilter
from theme.views import LearnigFocusCreate
from theme.views import LearningCardBulkDeleteAPI
from theme.views import LearningFocusTopicCreate
from theme.views import LearningFocusToipcUpdate
from theme.views import LearningFocusToipcForm
from theme.views import McCreate
from theme.views import MCBulkDeleteAPI
from theme.views import McOptionList
from theme.views import McOptionsFilter
from theme.views import McOptionsCreate
from theme.views import McOptionsForm
from theme.views import McOptionsUpdate
from theme.views import SqCreate
from theme.views import SQBulkDeleteAPI
from theme.views import SqMarkCreate
from theme.views import SqMarkUpdate
from theme.views import SqMarkList
from theme.views import SqMarkFilter
from theme.views import SqMarkForm
from theme.views import ThemeTestList, ThemeTestData, ThemeTestMcSq
from theme.views import PublicUserThemeTestData, PublicThemeTestMcSq
from discounts.views import DiscountCreate
from discounts.views import DiscountGetItem
from accounts.views import FormsLoginFrequencyDay
from accounts.views import FormsLoginFrequencyWeek
from accounts.views import FormsLoginFrequencyMonth
from accounts.views import AccountTokenPasswordVerificationGetOne
from accounts.views import AccountRegisterVerificationGetOne
from accounts.views import AccountFilterInfo
from accounts.views import ResetPasswordApi
from advertisement.views import AdvertisementAPI
from advertisement.views import AdvertisementUpdateAPI
from advertisement.views import AdvertisementGetAPI, AdvertisementList
from advertisement.views import AdvertisementBulkDeleteAPI
from advertisement.views import AdvertisementGetItem
from theme.views import ThemeUsageView
from theme.views import ThemeUsageViewfilter
from theme.views import TopicUsageView
from theme.views import TopicUsageViewfilter
from theme.views import ThemeBulkDelete
from theme.views import TopicBulkDelete
from theme.views import LearningCardUserAccessData
from bookmarks.views import MCBookmarksAPI
from bookmarks.views import MCBookmarksGetAPI
from bookmarks.views import SQBookmarksGetAPI
from bookmarks.views import SQBookmarksAPI
from bookmarks.views import CardsBookmarksAPI
from bookmarks.views import CardBookmarksGetAPI
from bookmarks.views import BookmarkCount
from discounts.views import DiscountGraph
from discounts.views import DiscountBulkDeleteAPI
from discounts.views import DiscountUsageCreate
from discounts.views import DiscountVerify
from discounts.views import DiscountAmount
from discounts.views import DiscountList
from product.views import ProductPriceAPI
from product.views import ProductPriceGetItem
from PurchaseOrder.views import PurchaseUsageViews
from PurchaseOrder.views import PurchaseCreate
from PurchaseOrder.views import PurchaseOrderByUser
from PurchaseOrder.views import CreateCheckoutSessionView
from PurchaseOrder.views import PurchaseKeys
from accounts.views import HomeOverviewGraphInfo
from Test.views import TestDetailsAPI
from Test.views import TestDetailsGetItem
from Test.views import IntegratedTest
from Test.views import TestDurationFrequency, TestAnsweredQuestionAPI
from theme.views import ThemeUsageCreateApi
from site_settings.views import PrivacyPolicyAPI, TermsAndConditionAPI
from site_settings.views import PrivacyPolicyGetAPI, TermsAndConditionGetAPI
from export_data.views import StudentDataExport, UserDataExport, LearningCardDataExport, QuestionsDataExport
from export_data.views import LoginStatistics, RegistrationUnit, TestStatistics
from export_data.views import PopularStatistics, SpecificDiscount
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='Register'),
    path('api/login/', SignInAPI.as_view(), name='Login'),
    path('api/signin/', SignInAPI.as_view(), name='Login Mobile'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='Logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='Logout All'),
    path('school/region/list', views.SchoolRegionList.snippet_detail),
    path('school/details', views.SchoolRegionCreate.as_view(), name='Create School'),
    path('school/form', views.SchoolRegionForm.as_view(), name='School Form'),
    path('region/', views.regionList.as_view(), name='Region'),
    path('district/', views.distcitList.as_view(), name='District'),
    path('school/', views.schoolList.as_view(), name='School'),
    path('account/', views.accountList.as_view(), name='Account'),
    path('form/', views.FormList.as_view(), name='Form'),
    path('account/update/email', views.AccountUpdateEmail.as_view(), name='Account Edit'),
    path('account/update/email/<str:token>', views.EmailResetTokenVerification.snippet_detail),
    path('account/verify/email', views.RegisterVerifyEmail.as_view(), name='Account Email Verify'),
    path('account/verify/email/<str:token>', views.RegisterEmailTokenVerification.snippet_detail),
    path('account/edit', views.accountListEdit.as_view(), name='Account Edit'),
    path('account/edit/admin', views.accountListEditAdmin.as_view(), name='Account Edit Admin'),
    path('password/reset', ResetPasswordApi.as_view(), name='Password OTP'),
    path('delete/user', views.DeleteUserViewApi.as_view(), name='Delete User'),
    path('recover/user', views.RecoverUserViewApi.as_view(), name='Recover User'),
    path('delete/multiple/users', views.DeleteMultiUserViewApi.as_view(), name='Delete Multiple User'),
    path('theme/', ThemeCreate.as_view(), name='Theme'),
    path('theme/bulk/delete', ThemeBulkDelete.as_view(), name='Theme Bulk Delete'),
    path('topic/', TopicCreate.as_view(), name='Topic'),
    path('topic/bulk/delete', TopicBulkDelete.as_view(), name='Topic Bulk Delete'),
    path('learningfocus/', LearnigFocusCreate.as_view(), name='Learning Focus'),
    path('card/title/bulk/delete', LearningCardBulkDeleteAPI.as_view(), name='Learning Card Delete'),
    path('topic/learningfocus/create', LearningFocusTopicCreate.as_view(), name='Topic Learning Focus Create'),
    path('topic/learningfocus/update', LearningFocusToipcUpdate.as_view(), name='Topic Learning Focus Update'),
    path('topic/learningfocus/form', LearningFocusToipcForm.as_view(), name='Topic Learning Focus Form'),
    path('card/', CardsCreate.as_view(), name='Learning card'),
    path('card/title', CardsTitleCreate.as_view(), name='Learning card Title'),
    path('theme/topic/create/', ThemeTopicCreate.as_view(), name='Theme Topic create'),
    path('theme/<int:pk>', ThemeGetOne.snippet_detail),
    path('topic/<int:pk>', TopicGetOne.snippet_detail),
    path('card/<int:pk>', CardGetOne.snippet_detail),
    path('card/title/<int:pk>', CardTitleGetOne.snippet_detail),
    path('theme/list/', ThemeTopicListCreate.snippet_detail),
    path('theme/card/list/', ThemeTopicCardList.snippet_detail),
    path('password/token/<str:token>', AccountTokenPasswordVerificationGetOne.snippet_detail),
    path('password/reset/<str:token>', AccountRegisterVerificationGetOne.snippet_detail),
    path('theme/topic/list', ThemeIdTopicGet.as_view(), name='Theme Topic List'),
    path('theme/topic/update/', ThemeIdTopicUpdate.as_view(), name='Theme Topic Update'),
    path('theme/topic/form', ThemeIdTopicFormView.as_view(), name='Theme Topic Form'),
    path('cardtitle/card/create', CardCartitleCreate.as_view(), name='Card Title Card Create'),
    path('cardtitle/card/update', CardCartitleUpdate.as_view(), name='Card Title Card Update'),
    path('cardtitle/card/form', CardCartitleForm.as_view(), name='Card Title Card Form'),
    path('cardtitle/card/list', CardTitleList.snippet_detail),
    path('cardtitle/card/list/view', CardTitleListView.snippet_detail),
    path('cardtitle/card/list/filter', CardTitleListViewFilter.as_view(), name='Card Title Card Filter'),
    path('cardtitle/card/list/item', CardTitleListViewItem.as_view(), name='Card Title Card Item'),
    path('mc/', McCreate.as_view(), name='MC'),
    path('mc/bulk/delete', MCBulkDeleteAPI.as_view(), name='Discount Bulk Delete'),
    path('mc/option/list', McOptionList.snippet_detail),
    path('mc/option/list/filter', McOptionsFilter.as_view(), name='MC Option Filter'),
    path('mc/option/create', McOptionsCreate.as_view(), name='MC Option Create'),
    path('mc/option/form', McOptionsForm.as_view(), name='MC Option Form'),
    path('mc/option/update', McOptionsUpdate.as_view(), name='MC Option Update'),
    path('sq/', SqCreate.as_view(), name='Short Question'),
    path('sq/bulk/delete', SQBulkDeleteAPI.as_view(), name='Discount Bulk Delete'),
    path('sq/mark/create', SqMarkCreate.as_view(), name='Short Question Create'),
    path('sq/mark/update', SqMarkUpdate.as_view(), name='Short Question Update'),
    path('sq/mark/list', SqMarkList.snippet_detail),
    path('sq/mark/list/filter', SqMarkFilter.as_view(), name='MC option Filter'),
    path('sq/mc/list', IntegratedTest.as_view(), name='Short QuestC List'),
    path('sq/mark/form', SqMarkForm.as_view(), name='Short Question Form'),
    path('login_frequency/day', FormsLoginFrequencyDay.as_view(), name='Login Frequency Day'),
    path('login_frequency/week', FormsLoginFrequencyWeek.as_view(), name='Login Frequency Week'),
    path('login_frequency/month', FormsLoginFrequencyMonth.as_view(), name='Login Frequency Month'),
    path('advertisement/', AdvertisementAPI.as_view(), name='Advertisement'),
    path('advertisement/update', AdvertisementUpdateAPI.as_view(), name='Advertisement'),
    path('advertisement/bulk/delete', AdvertisementBulkDeleteAPI.as_view(), name='Advertisement Bulk Delete'),
    path('advertisement/item', AdvertisementGetItem.as_view(), name='Advertisement Item'),
    path('advertisement/list', AdvertisementList.as_view(), name='Advertisement List'),
    path('advertisement/get', AdvertisementGetAPI.snippet_detail),
    path('discount/', DiscountCreate.as_view(), name='Discount'),
    path('discount/usage/create', DiscountUsageCreate.as_view(), name='Discount Usage Create'),
    path('discount/item', DiscountGetItem.as_view(), name='Discount Item'),
    path('discount/list', DiscountList.as_view(), name='Discount List'),
    path('theme/usage/all', ThemeUsageView.as_view(), name='Theme Usage All'),
    path('theme/usage/filter', ThemeUsageViewfilter.as_view(), name='Theme Usage Filter'),
    path('theme/usage/create', ThemeUsageCreateApi.as_view(), name='Theme Usage Create'),
    path('topic/usage/all', TopicUsageView.as_view(), name='Topic Usage All'),
    path('topic/usage/filter', TopicUsageViewfilter.as_view(), name='Topic Usage Filter'),
    path('purchase/graph', PurchaseUsageViews.as_view(), name='Purchase Graph'),
    path('purchase/create', PurchaseCreate.as_view(), name='Purchase Create'),
    path('purchase/form', PurchaseOrderByUser.as_view(), name='Purchase form'),
    path('purchase/keys', PurchaseKeys.as_view(), name='Purchase Keys'),
    path('discount/bulk/delete', DiscountBulkDeleteAPI.as_view(), name='Discount Bulk Delete'),
    path('discount/graph', DiscountGraph.as_view(), name='Discount Graph'),
    path('discount/verify', DiscountVerify.as_view(), name='Discount Verify'),
    path('discount/amount', DiscountAmount.as_view(), name='Discount Amount Calculation'),
    path('theme/test/list', ThemeTestList.snippet_detail),
    path('theme/test/data', ThemeTestData.snippet_detail),
    path('theme/test/data/public', PublicUserThemeTestData.snippet_detail),
    path('theme/mc/sq', ThemeTestMcSq.as_view(), name='Theme MC SQ List'),
    path('theme/mc/sq/public', PublicThemeTestMcSq.as_view(), name='Theme MC SQ List Public'),
    path('product/price', ProductPriceAPI.as_view(), name='Product Price'),
    path('product/price/item', ProductPriceGetItem.as_view(), name='Product Price Item'),
    path('home/overview', HomeOverviewGraphInfo.as_view(), name='Home Overview Graph'),
    path('account/filter', AccountFilterInfo.as_view(), name='Account Filter'),
    path('mc/bookmark', MCBookmarksAPI.as_view(), name='MC Bookmark'),
    path('mc/bookmark/get', MCBookmarksGetAPI.snippet_detail),
    path('sq/bookmark/get', SQBookmarksGetAPI.snippet_detail),
    path('sq/bookmark', SQBookmarksAPI.as_view(), name='SQ Bookmark'),
    path('card/bookmark', CardsBookmarksAPI.as_view(), name='Card Bookmark'),
    path('card/bookmark/get', CardBookmarksGetAPI.snippet_detail),
    path('bookmark/count', BookmarkCount.snippet_detail),
    path('test/details', TestDetailsAPI.as_view(), name='Test Details'),
    path('test/details/form', TestDetailsGetItem.as_view(), name="Test Details Form"),
    path('stripe/payment/intent', CreateCheckoutSessionView.as_view(), name='Stripe Payment Intent'),
    path('privacy/policy', PrivacyPolicyAPI.as_view(), name='Privacy Policy'),
    path('terms/conditions', TermsAndConditionAPI.as_view(), name='Terms And Condition'),
    path('privacy/policy/get', PrivacyPolicyGetAPI.as_view(), name='Privacy Policy Get'),
    path('terms/conditions/get', TermsAndConditionGetAPI.as_view(), name='Terms And Condition Get'),
    path('test/duration/frequency', TestDurationFrequency.as_view(), name='Terms And Condition Get'),
    path('learning/card/user/data', LearningCardUserAccessData.as_view(), name='Learning Card User Access Data'),
    path('questions/user/data', TestAnsweredQuestionAPI.as_view(), name='Questions Data Update'),
    path('student/data/export', StudentDataExport.as_view(), name='Student Data Export'),
    path('user/data/export', UserDataExport.as_view(), name='User Data Export'),
    path('learning/card/data/export', LearningCardDataExport.as_view(), name='Learning Card Data Export'),
    path('questions/data/export', QuestionsDataExport.as_view(), name='Questions Data Export'),
    path('login/statistics/export', LoginStatistics.as_view(), name='Login Statistics Export'),
    path('registration/unit/export', RegistrationUnit.as_view(), name='Registration Unit Export'),
    path('test/statistics/export', TestStatistics.as_view(), name='Test Statistics Export'),
    path('popular/statistics/export', PopularStatistics.as_view(), name='Popular Statistics Export'),
    path('specific/discount/export', SpecificDiscount.as_view(), name='Specific Discount Export'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
