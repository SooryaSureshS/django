from accounts.models import user
from region.views import DeleteUserViewApi, DeleteMultiUserViewApi
from .models import DeletedUsers
from accounts.models import login_frequency
from Test.models import TestDetails, TestAttendedQuestions
from PurchaseOrder.models import PurchaseOrder
from theme.models import ThemeUsage, UserLearningCardData
from bookmarks.models import MCBookmarks, SQBookmarks, CardsBookmarks
from discounts.models import DiscountUsage

class DeleteUserViewApiInherit(DeleteUserViewApi):
    def post(self, request, format=None):
        print("asdasd")
        if user.objects.filter(id=request.data.get('user')):
            user_id = user.objects.get(id=request.data.get('user'))

            login_frequency_data = login_frequency.objects.get(user_id=user_id)
            test_details_data = TestDetails.objects.get(partner_id=user_id)
            test_attended_questions_data = TestAttendedQuestions.objects.get(partner_id=user_id)
            purchase_order_data = PurchaseOrder.objects.get(partner_id=user_id)
            theme_usage_data = ThemeUsage.objects.get(user_id=user_id)
            user_learning_card_data = UserLearningCardData.objects.get(partner_id=user_id)
            mc_bookmarks_data = MCBookmarks.objects.get(partner_id=user_id)
            sq_bookmarks_data = SQBookmarks.objects.get(partner_id=user_id)
            cards_bookmarks_data = CardsBookmarks.objects.get(partner_id=user_id)
            discount_usage_data = DiscountUsage.objects.get(user=user_id)

            print("___________________________")
            print("login_frequency_data", login_frequency_data)
            print("test_details_data", test_details_data)
            print("test_attended_questions_data", test_attended_questions_data)
            print("purchase_order_data", purchase_order_data)
            print("theme_usage_data", theme_usage_data)
            print("user_learning_card_data", user_learning_card_data)
            print("mc_bookmarks_data", mc_bookmarks_data)
            print("sq_bookmarks_data", sq_bookmarks_data)
            print("cards_bookmarks_data", cards_bookmarks_data)
            print("discount_usage_data", discount_usage_data)
            print("--------------------------")

            res = super(DeleteUserViewApiInherit, self).post(request)
            if res.data['success']:
                DeletedUsers.objects.create(email=user_id.email,
                                            contact=user_id.contact,
                                            phone=user_id.phone,
                                            profile_picture=user_id.profile_picture,
                                            firstname=user_id.firstname,
                                            lastname=user_id.lastname,
                                            registration_date=user_id.registration_date,
                                            registration_time=user_id.registration_time,
                                            created_date=user_id.created_date,
                                            updated_date=user_id.updated_date,
                                            is_purchased=user_id.is_purchased,
                                            is_staff=user_id.is_staff,
                                            is_admin=user_id.is_admin,
                                            is_student=user_id.is_student,
                                            is_teacher=user_id.is_teacher,
                                            email_url=user_id.email_url,
                                            reset_email=user_id.reset_email,
                                            password_url=user_id.password_url,
                                            password_set_url=user_id.password_set_url,
                                            language=user_id.language,
                                            user_id=user_id.id).save()
                return res
        else:
            res = super(DeleteUserViewApiInherit, self).post(request)
            return res


class DeleteMultiUserViewApiInherit(DeleteMultiUserViewApi):
    def post(self, request, format=None):
        arr = []
        if request.data.get('users'):
            for user_list in request.data.get('users'):
                if user.objects.filter(id=user_list):
                    user_id = user.objects.get(id=user_list)
                    arr.append(user_id)
            res = super(DeleteMultiUserViewApiInherit, self).post(request)
            if res.data['success']:
                for user_id in arr:
                    DeletedUsers.objects.create(email=user_id.email,
                                                contact=user_id.contact,
                                                phone=user_id.phone,
                                                profile_picture=user_id.profile_picture,
                                                firstname=user_id.firstname,
                                                lastname=user_id.lastname,
                                                registration_date=user_id.registration_date,
                                                registration_time=user_id.registration_time,
                                                created_date=user_id.created_date,
                                                updated_date=user_id.updated_date,
                                                is_purchased=user_id.is_purchased,
                                                is_staff=user_id.is_staff,
                                                is_admin=user_id.is_admin,
                                                is_student=user_id.is_student,
                                                is_teacher=user_id.is_teacher,
                                                email_url=user_id.email_url,
                                                reset_email=user_id.reset_email,
                                                password_url=user_id.password_url,
                                                password_set_url=user_id.password_set_url,
                                                language=user_id.language,
                                                user_id=user_id.id).save()
            return res
