"""
Definition of views.
"""
from datetime import datetime
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.template import RequestContext
from .forms import RegisterUserForm
from .forms import RegisterToolForm
from .forms import UpdateToolsForm
from .forms import ShedCreation
from .forms import UpdatePersonalInfoForm
from .forms import UpdatePersonalInfoForm2
from .forms import UpdateUserProfileForm
from .forms import UpdateUserProfileForm2
from .forms import UpdateShareZoneForm2
from .forms import UpdateShareZoneForm1
from .models import Notification_User
from .models import Notification
from .forms import LoginForm
from app.models import Tool
from app.models import Shed
from app.models import UserProfile
from app.models import ActiveTransactions
from app.models import ToolHistory
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.context_processors import csrf
from django.http import Http404
from .forms import UpdatePasswordForm
from .forms import TransactionCompletionForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.templatetags import DiggPaginator
from django.http import HttpResponse
from django.contrib import messages


def home(request):
    context_instance = {'title': 'Tool Share, home page',
                        'year': datetime.now().year,
                        }
    """Renders the home page."""
    if request.user.is_authenticated()==False:
        return render(request,'app/index.html', context_instance)

    assert isinstance(request, HttpRequest)
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    zip_code = user_profile.zipcode
    objects_per_page = 3

    page = request.GET.get('page')
    tool_name = request.GET.get('tool_name')
    print(tool_name)
    if tool_name is None or not tool_name:
        print('tool_name is either empty or None')
        tool_name = ""
        tool = Tool.objects.all().filter(~Q(tool_owner_id=request.user.id), status="Active", is_borrowed=False, share_zone=zip_code)

    else:
        print('tool name is not empty and is not None')
        tool = Tool.objects.all().filter(~Q(tool_owner_id=request.user.id), status="Active", is_borrowed=False, share_zone=zip_code).filter(tool_name__contains=tool_name)
        if not tool:
            context_instance['message'] = 'Search resulted with no matching.'
    context_instance['tool_name'] = tool_name
    print(tool_name+ "=tool_name")
    print(page)
    if page is None:
        page = 1
    print(str(page) + "=page")
    try:
        print('before custom_paginator')
        custom_paginator = DiggPaginator(tool, objects_per_page, body=3, padding=1, tail=1).page(page)
        print('after custom paginator')
        context_instance['paginator'] = custom_paginator
    except:
        print('in except')
        raise Http404("Page not found")
    paging = Paginator(tool, objects_per_page)
    tool = paging.page(page)
    context_instance['tool'] = tool

    notifications_shown = updateNotifications(request)
    context_instance['notifications_shown']=notifications_shown
    return render(request,
                  'app/index.html',
                  context_instance)


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(request,
                  'app/contact.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      'title': 'Contact',
                                                      'message': '',
                                                      'year': datetime.now().year,
                                                  }))


def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(request,
                  'app/about.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      'title': 'About Us',
                                                      'message': '',
                                                      'year': datetime.now().year,
                                                  }))


def login(request):
    print('in the login')
    title = 'Login page.'
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            entered_user = form.data['username']
            entered_password = form.data['password']
            user = auth.authenticate(username=entered_user, password=entered_password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/')
            else:
                form = LoginForm()
                error = True
                return render(request, 'app/login.html', {'form': form, 'title': title, 'error': error})
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form , 'title':title})


def register(request):
    if request.user.is_authenticated():
        raise Http404(
            "You are already logged in. So please go to the main site.")
    form = RegisterUserForm(initial={'gender': '1'})
    return render(request,
                  'app/registeruser.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      'title': 'Register',
                                                      'message': '',
                                                      'year': datetime.now().year,
                                                      'form': form,
                                                  }), )


def create_user_profile(shed, form, user):
    user_p = UserProfile.objects.create(address=form.data['address'],
                                        gender=form.data['gender'],
                                        zipcode=shed,
                                        user_id=user)
    user_p.save()
    return user_p


def registerUser(request):
    title = 'registration'
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)  # binding the form.
        if form.is_valid():
            user = User.objects.create_user(first_name=form.data['first_name'],
                                            last_name=form.data['last_name'],
                                            email=form.data['e_mail'],
                                            username=form.data['username'],
                                            password=form.data['password'],
                                            )
            user.save()
            entered_zipcode = form.data['zipcode']
            try:
                shed = Shed.objects.get(zipcode=entered_zipcode)
                create_user_profile(shed, form, user)
                form = LoginForm()
                title = 'You have successfully been registered. Please login.'
                return render(request, 'app/login.html', {'form': form, 'title': title})
            except:  # there are no zipcode values to that one
                title = 'You have been assigned as the coordinator of the Shed.'
                shed = Shed.objects.create(zipcode=entered_zipcode)
                shed.save()
                user_profile = create_user_profile(shed, form, user)
                user_profile.is_coordinator = True
                user_profile.save()
                form = ShedCreation()
                return render(request, 'app/registershed.html', {'form': form, 'title': title, 'zipcode': entered_zipcode})
    else:
        form = RegisterUserForm()
        title = 'Register'
    return render(request, 'app/registeruser.html', {'form': form, 'title': title})


def register_shed(request, zipcode):
    """
    :param request:holds the page that calls register_shed function
    :return: register shed page, where the user creates the shed for the first time.
    """
    print('in register_shed')
    if request.method == 'POST':
        form = ShedCreation(request.POST)
        if form.is_valid():
            shed = Shed.objects.get(zipcode=zipcode)
            shed.address = form.data['address']
            shed.name = form.data['name']
            shed.save()
            loginform = LoginForm()
            title = 'You have been successfully registered. Now, you can login and see what your new share zone offers to you.'
            return render(request, 'app/login.html', {'form': loginform, 'title': title})
    else:
        form = ShedCreation()
    return render(request, 'app/registershed.html', {'form': form,'zipcode': zipcode})


def registerTool(request):
    if request.method == 'POST':
        form = RegisterToolForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = UserProfile.objects.get(user_id=request.user.id)
            # print(user_profile)
            zip_code = user_profile.zipcode
            # print(zip_code.zipcode)
            tool = Tool(tool_name=form.data['tool_name'],
                        status=form.data['status'],
                        category=form.data['category'],
                        tool_owner_id=request.user,
                        location=form.data['location'],
                        condition=form.data['condition'],
                        special_instruction=form.data['special_instruction'],
                        image = request.FILES['image'],
                        share_zone=Shed.objects.get(zipcode=UserProfile.objects.get(user_id=request.user.id).zipcode.zipcode),
                        )
            tool.save()
            messages.success(request, 'New tool has been registered successfully')
            return HttpResponseRedirect('/registeredTools')
    else:
        form = RegisterToolForm()
    notifications_shown = updateNotifications(request)

    act = "Register"
    title = "Register Tool"
    args = {}
    args.update(csrf(request))
    args['form'] = form
    args['id'] = id
    args['act'] = act
    args['title'] = title
    args['notifications_shown'] = notifications_shown
    return render(request, 'app/registertool.html', args)


def displayTools(request):
    assert isinstance(request, HttpRequest)
    # borrow_requests = BorrowRequests.objects.filter(owner_id=request.user.username)

    return render(request,
                  'app/tooltable.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      # A logged in user should be able to see only those tools
                                                      # that have been registered by him
                                                      'tool': Tool.objects.all().filter(tool_owner_id=request.user.id),
                                                      'ownerID': request.user.id,
                                                      'requestedTools': ActiveTransactions.objects.filter(owner_id=request.user.id,
                                                                                                          is_request_approved=False,
                                                                                                          is_set_for_return=False),
                                                      'borrowedTools': ActiveTransactions.objects.filter(borrower_id=request.user.id,
                                                                                                         is_request_approved=True,
                                                                                                         is_set_for_return=False)
                                                  }))


def registeredTools(request):
    is_tool_set_for_return =[]
    tools = Tool.objects.all().filter(tool_owner_id=request.user.id)
    for t in tools:
        print()
        try:
            is_tool_set_for_return.append(ActiveTransactions.objects.get(tool=t.id).is_set_for_return)

        except:
            is_tool_set_for_return.append(False)

    return_val = zip(tools, is_tool_set_for_return)
    for t in tools:
        try:
            print(t)
            print('before tool_notify')
            tool_notify = Notification_User.objects.all().filter(tool_name=t.id).filter(notification=Notification.objects.get(code='TR'))
            print('after tool_notify')
            print(tool_notify)
            for t in tool_notify:
                t.isSeen=True
                t.save()
                print(t.isSeen)
            tool_notify.save()
            print(tool_notify.isSeen)
        except:
            print('Tool does not have a notification')
    notifications_shown = updateNotifications(request)
    return render(request,
                  'app/registeredtools.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      # A logged in user should be able to see only those tools
                                                      # that have been registered by him
                                                      'zipped_data': return_val,
                                                      'notifications_shown': notifications_shown
                                                  }))


def borrowedToolsNotification(request,notification_id):
    user_notification = Notification_User.objects.get(id=notification_id)
    user_notification.isSeen=True
    user_notification.save()
    notifications_shown = updateNotifications(request)
    return render(request,
                  'app/borrowedtools.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      'borrowedTools': ActiveTransactions.objects.filter(borrower_id=request.user.id,
                                                                                                         is_request_approved=True,
                                                                                                         is_set_for_return=False),
                                                      'notifications_shown' : notifications_shown
                                                  }))


def borrowedTools(request):
    notifications_shown = updateNotifications(request)

    return render(request,
                  'app/borrowedtools.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      'borrowedTools': ActiveTransactions.objects.filter(borrower_id=request.user.id,
                                                                                                         is_request_approved=True,
                                                                                                         is_set_for_return=False),
                                                      'notifications_shown': notifications_shown
                                                  }))


def borrowRequestsNotification(request, notification_id):
    requested_tools = ActiveTransactions.objects.filter(owner_id=request.user.id, is_request_approved=False, is_set_for_return=False)
    user_notification = Notification_User.objects.get(id=notification_id)
    user_notification.isSeen = True
    user_notification.save()
    notifications_shown = updateNotifications(request)
    return render(request,
                  'app/borrowrequest.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      # A logged in user should be able to see only those tools
                                                      # that have been registered by him
                                                      'requestedTools': ActiveTransactions.objects.filter(owner_id=request.user.id,
                                                                                                          is_request_approved=False,
                                                                                                          is_set_for_return=False),
                                                      'notifications_shown': notifications_shown,
                                                      'notification': user_notification
                                                  }))


def borrowRequests(request):
    requested_tools = ActiveTransactions.objects.filter(owner_id=request.user.id, is_request_approved=False, is_set_for_return=False)
    borrow_request_notifications = Notification_User.objects.filter(user=request.user, notification=Notification.objects.get(code='BR'),isSeen=False)
    for c in borrow_request_notifications:
        c.isSeen = True
        c.save()
    notifications_shown = updateNotifications(request)
    return render(request,
                  'app/borrowrequest.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      # A logged in user should be able to see only those tools
                                                      # that have been registered by him
                                                      'requestedTools': ActiveTransactions.objects.filter(owner_id=request.user.id,
                                                                                                          is_request_approved=False,
                                                                                                          is_set_for_return=False,
                                                                                                          tool_id__location='Home'),
                                                      'notifications_shown': notifications_shown
                                                  }))


# dead code, displayShedTools is not used
def displayShedTools(request):
    assert isinstance(request, HttpRequest)
    current_user = request.user.id
    user_profile = UserProfile.objects.get(user_id=current_user)
    zip_code = user_profile.zipcode
    shed_users = UserProfile.objects.all().filter(zipcode=zip_code).exclude(user_id=current_user)

    tool = []
    for index in range(len(shed_users)):
        tool.append(Tool.objects.all().filter(tool_owner_id=shed_users[index].user_id, status='Active', is_borrowed=False))

    final_tool = []
    for i in range(len(tool)):
        for j in range(len(tool[i])):
            final_tool.append(tool[i][j])

    return render(request,
                  'app/shedtooltable.html',
                  context_instance=RequestContext(request,
                                                  {
                                                      'tool': final_tool
                                                  }))


def updateUserInfo(request):
    if request.POST:
        value = request.user.id
        current_user = User.objects.get(id=value)
        form = UpdatePersonalInfoForm(request.POST)
        if form.is_valid():
            form = UpdatePersonalInfoForm(request.POST, instance=value)
            form.save()
            return HttpResponseRedirect('/')
    else:
        value = request.user.id
        current_user = User.objects.get(id=value)
        user_profile = UserProfile.objects.get(user_id=value)
        form = UpdatePersonalInfoForm(instance=current_user)

    notifications_shown = updateNotifications(request)

    args = {}
    args.update(csrf(request))
    args['form'] = form
    args['last_name'] = current_user.last_name
    args['first_name'] = current_user.first_name
    args['email'] = current_user.email
    args['address'] = user_profile.address
    args['gender'] = user_profile.gender
    args['form_name'] = False
    args['form_email'] = False
    args['form_address'] = False
    args['form_gender'] = False
    args['form_update'] = False
    args['update_name'] = 'updatename'
    args['update_email'] = 'updateemail'
    args['update_address'] = 'updateaddress'
    args['update_gender'] = 'updategender'
    args['notifications_shown'] = notifications_shown

    return render(request, 'app/updateuserinfo2.html', args)


def onReturnToolRequest(request, toolid):
    print('In return request')
    # print(toolid)
    requested_tool = ActiveTransactions.objects.get(tool=toolid)
    requested_tool.is_set_for_return = True
    notification_type = Notification.objects.get(code="TR")

    tool_return_date = getattr(requested_tool, "return_date")

    if tool_return_date != datetime.now():
        requested_tool.return_date = datetime.now()
        #requested_tool.notification_info = 'requestToolReturn'

    requested_tool.save()
    Notification_User(tool_name=requested_tool.tool, user=requested_tool.owner_id, notification=notification_type).save()

    #show message to borrower
    messages.success(request, 'A return request has been sent successfully')

    return HttpResponseRedirect('/borrowedTools')


def onApproveReturn(request, toolid):

    requested_tool = ActiveTransactions.objects.get(tool=toolid)

    tool = Tool.objects.get(id=toolid)
    tool_owner = User.objects.get(id=tool.tool_owner_id.id)
    borrower = getattr(requested_tool, "borrower_id")
    return_date = getattr(requested_tool, "return_date")
    notification_type = Notification.objects.get(code="VR")
    tool.is_borrowed = False

    print(request.method)
    form = TransactionCompletionForm()

    if request.method == 'POST':
        form = TransactionCompletionForm(request.POST)
        print('inside post')
        if form.is_valid():
            print('form is valid')

            toolHistory = ToolHistory(tool_id=tool,
                                      borrower_id=borrower,
                                      owner_id=request.user,
                                      transaction_date=datetime.now(),
                                      condition=form.data['condition'],
                                      transaction_type='Returned',
                                      owner_comments=form.data['message'],
                                      return_date=return_date,
                                      )

            tool.condition = form.data['condition']
            toolHistory.save()
            Notification_User(notification=notification_type, tool_name=tool, user=borrower).save()
            requested_tool.delete()
            messages.success(request, 'Tool return has been approved')
            return HttpResponseRedirect('/')
    tool.save()
    return render(request, 'app/toolreturn.html', {'tool': tool, 'form': form, 'tool_owner': tool_owner})


def onRejectToolRequest(request, toolid):
    print('In on reject tool request')

    notification_type = Notification.objects.get(code="RR")
    tool = Tool.objects.get(id=toolid)
    tool.is_borrowed = False
    tool.save()

    requested_tool = ActiveTransactions.objects.get(tool=toolid)
    Notification_User(tool_name=tool, user=requested_tool.borrower_id, notification=notification_type).save()
    requested_tool.delete()

    messages.success(request, 'Tool request has been rejected')
    return HttpResponseRedirect('/borrowRequests')


# AL: This method stores the borrower and the tool owner as foreign key to the borrow request table
# This makes the notification functionality easy.
def onBorrowToolRequest(request, id):
    print('in on borrow tool request')
    tool = Tool.objects.get(id=id)
    notification_type = Notification.objects.get(code='BR')
    tool_owner = User.objects.get(id=tool.tool_owner_id.id)
    borrower_id = User.objects.get(id=request.user.id)
    form = TransactionCompletionForm()

    if request.method == 'POST':
        form = TransactionCompletionForm(request.POST)
        if form.is_valid():
            print('form is valid')

            activeTransaction = ActiveTransactions(tool=tool,
                                                   borrower_id=borrower_id,
                                                   owner_id=tool_owner,
                                                   is_request_approved=False,
                                                   return_date=form.data['date'],
                                                   borrower_message=form.data['message'],
                                                   )
            activeTransaction.save()
            tool.is_borrowed = True
            tool.save()
            if tool.location == 'Shed':
                activeTransaction.is_request_approved = True
                activeTransaction.save()
                onAcceptToolRequest(request, id)
                messages.success(request, 'The tool has been borrowed successfully')
            else:
                notification_sent = Notification_User(notification=notification_type,tool_name=tool, user=tool_owner)
                notification_sent.save()
                messages.success(request, 'A borrow request has been sent successfully')
            return HttpResponseRedirect('/')

    return render(request, 'app/tooldetails.html', {'tool': tool, 'form': form, 'tool_owner': tool_owner})


def onAcceptToolRequest(request, toolid):
    print('In accept request')
    requested_tool = ActiveTransactions.objects.get(tool=toolid)
    requested_tool.is_request_approved = True
    requested_tool.save()
    notification_type = Notification.objects.get(code='AR')

    borrower = getattr(requested_tool, "borrower_id")
    borrower_id = getattr(borrower, "id")
    return_date = getattr(requested_tool, "return_date")

    # update tool with tool_id borrower ID
    tool = Tool.objects.get(id=toolid)

    tool.save()

    toolHistory = ToolHistory(tool_id=tool,
                              borrower_id=borrower,
                              owner_id=request.user,
                              transaction_date=datetime.now(),
                              condition=tool.condition,
                              transaction_type='Borrowed',
                              owner_comments='Request has been accepted.',
                              return_date=return_date,
                              borrower_message=requested_tool.borrower_message,
                              )

    toolHistory.save()
    # update the notifications in ActiveTransactions model
    accepted_tool = ActiveTransactions.objects.get(tool=toolid)
    Notification_User(notification=notification_type,user=borrower,tool_name=tool).save()
    #accepted_tool.notification_info = 'acceptToolRequest'
    accepted_tool.save()

    if tool.location != 'Shed':
        messages.success(request, 'The tool request has been accepted')

    return HttpResponseRedirect('/registeredTools')


def updateTool(request, id):
    tools = Tool.objects.get(id=id)
    title = "Update Tool Information"

    if request.POST:
        form = UpdateToolsForm(request.POST, instance=tools)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = UpdateToolsForm(instance=tools)

    act = "Update"
    args = {}
    args.update(csrf(request))
    args['form'] = form
    args['tools'] = tools
    args['id'] = id
    args['act'] = act
    args['title'] = title
    messages.success(request, 'Tool information has been updated successfully')
    return render(request, 'app/registertool.html', args)


def changePwd(request):
    message = ''
    if request.method == 'POST':
        form = UpdatePasswordForm(request.POST)
        if form.is_valid():
            uid = request.user.id
            u = User.objects.get(id=uid)

            password_1 = request.POST['password_1'].encode('ascii', 'replace')
            password_2 = request.POST['password_2'].encode('ascii', 'replace')
            if password_1 == password_2:
                u.set_password(form.data['password_1'])
                u.save()
                return HttpResponseRedirect('/')
            else:
                return render_to_response('app/changepwd.html', {'form': form})

    else:
        form = UpdatePasswordForm(request.POST)
        return render(request, 'app/changepwd.html', {'form': form})


def updatedetails(request,actn):
    form_update = False
    form_name = False
    form_email = False
    form_address = False
    form_gender = False
    if request.POST:
        value = request.user.id
        current_user = User.objects.get(id=value)
        user_profile = UserProfile.objects.get(user_id=value)
        msg = ''
        if actn == "updatename":
            form = UpdatePersonalInfoForm(request.POST)
            if form.is_valid():
                form = UpdatePersonalInfoForm(request.POST, instance=current_user)
                form.save()
                msg = 'Name updated successfully'
        if actn == "updateemail":
            form = UpdatePersonalInfoForm2(request.POST)
            if form.is_valid():
                form = UpdatePersonalInfoForm2(request.POST, instance=current_user)
                form.save()
                msg = 'Email updated successfully'
        if actn == "updateaddress":
            form = UpdateUserProfileForm(request.POST)
            if form.is_valid():
                form = UpdateUserProfileForm(request.POST, instance=user_profile)
                form.save()
                msg = 'Address updated successfully'
        if actn == "updategender":
            form = UpdateUserProfileForm2(request.POST)
            if form.is_valid():
                form = UpdateUserProfileForm2(request.POST, instance=user_profile)
                form.save()
                msg = 'Gender updated successfully'
        messages.success(request, msg)
        return HttpResponseRedirect('/updateUserInfo2/')
    else:
        value = request.user.id
        current_user = User.objects.get(id=value)
        user_profile = UserProfile.objects.get(user_id=value)
        first_name = current_user.first_name
        last_name = current_user.last_name
        email = current_user.email
        if actn == "updatename":
            form = UpdatePersonalInfoForm(instance=current_user)
            form_name = True
            form_update = True
        if actn == "updateemail":
            form = UpdatePersonalInfoForm2(instance=current_user)
            form_email = True
            form_update = True
        if actn == "updateaddress":
            form = UpdateUserProfileForm(instance=user_profile)
            form_address = True
            form_update = True
        if actn == "updategender":
            form = UpdateUserProfileForm2(instance=user_profile)
            form_gender = True
            form_update = True

    notifications_shown = updateNotifications(request)

    args = {}
    args.update(csrf(request))
    args['form'] = form
    args['last_name'] = last_name
    args['first_name'] = first_name
    args['email'] = email
    args['address'] = user_profile.address
    args['gender'] = user_profile.gender
    args['form_update'] = form_update
    args['form_name'] = form_name
    args['form_email'] = form_email
    args['form_address'] = form_address
    args['form_gender'] = form_gender
    args['notifications_shown'] = notifications_shown
    return render(request, 'app/updateuserinfo2.html', args)


def updateNotifications(request):
    """
    # get unseen notifications for the user
    current_user = UserProfile.objects.get(user_id=request.user.id)
    users_notification = ActiveTransactions.objects.filter(
        Q(borrower_id=current_user, notification_is_seen=False) | Q(owner_id=current_user,
                                                                    notification_is_seen=False))
    notifications_shown = []
    # 1. get message/ID needed for notification
    for index in range(len(users_notification)):
        notification_message = getattr(users_notification[index], "notification_info")
        if notification_message == 'borrowRequest' and getattr(users_notification[index], "borrower_id") != current_user:
            notifications_shown.append(['borrowRequest', getattr(users_notification[index], "borrower_id")])
        if notification_message == 'requestToolReturn' and getattr(users_notification[index], "borrower_id") != current_user:
            notifications_shown.append(['requestToolReturn', getattr(users_notification[index], "borrower_id")])
        elif notification_message == 'acceptToolRequest' and getattr(users_notification[index], "owner_id") != current_user:
            toolid = getattr(users_notification[index], "tool_id")
            tool = Tool.objects.get(id=toolid)
            toolname = getattr(tool, "tool_name")
            notifications_shown.append(['acceptToolRequest', toolname])
    # 2. return array with message ID, data
    return notifications_shown """

    user_notifications = Notification_User.objects.all().filter(user=request.user.id).filter(isSeen=False)
    return user_notifications


def changeShareZone(request):
    hasBorrowed = False
    hasLent = False
    current_user = User.objects.get(id=request.user.id)
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    currentZip =   user_profile.zipcode

    if request.POST:
        form = UpdateShareZoneForm2(request.POST)
        if form.is_valid():
                form = UpdateShareZoneForm2(request.POST)
                form.save()
                msg = 'Name updated successfully'
        return render(request, 'app/changeShareZone.html')
    else:
        lentTools = ActiveTransactions.objects.filter(owner_id=request.user.id,
                                                      is_request_approved=True,
                                                      is_set_for_return=False)
        borrwedTools = ActiveTransactions.objects.filter(borrower_id=request.user.id,
                                                      is_request_approved=True,
                                                      is_set_for_return=False)
        if borrwedTools:
            print('user has borrowed tools')
            hasBorrowed = True
        if lentTools:
            print('user has lent tools')
            hasLent = True
        args = {}
        args.update(csrf(request))
        args['form'] = UpdateShareZoneForm2(request.POST)
        args['hasBorrowed'] = hasBorrowed
        args['hasLent'] = hasLent
        args['zipcode'] = currentZip.zipcode
        return render(request, 'app/changeShareZone.html', args)
