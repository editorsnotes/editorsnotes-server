# import re
# 
# import reversion
# 
# from editorsnotes.auth.models import User, ProjectInvitation
# 
# 
# @reversion.create_revision()
# def create_invited_user(email):
#     invitation = ProjectInvitation.objects.filter(email=email)
# 
#     if not invitation.exists():
#         return None
# 
#     invitation = invitation.get()
#     role = invitation.project_role
# 
#     username = re.sub(r'[^\w\-.]', '', email[:email.rindex('@')])[:29]
#     if User.objects.filter(username=username).exists():
#         existing_names = [
#             u.username[len(username):] for u in
#             User.objects.filter(username__startswith=username)]
#         username += str([
#             i for i in range(0, 10) if str(i) not in existing_names][0])
# 
#     new_user = User(username=username, email=email)
#     new_user.set_unusable_password()
#     new_user.save()
# 
#     role.users.add(new_user)
#     invitation.delete()
# 
#     return new_user
