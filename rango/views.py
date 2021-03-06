from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from rango.forms import CategoryForm, PageForm, UserProfileForm
from rango.models import Category, Page, UserProfile
from rango.webhoseio_search import run_query


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request,'rango/index.html', context_dict)

    return response


def about(request):
    # If the visits session varible exists, take it and use it.
    # If it doesn't, we haven't visited the site so set the count to zero.
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    # remember to include the visit data
    return render(request, 'rango/about.html', {'visits': count})


@login_required
def category(request, category_name_slug):

    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        category.views += 1
        category.save()
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    if request.method == "POST":
        query = request.POST['query'].strip()
        if query:
            # Run our Webhoseio function to get the results list!
            context_dict['result_list'] = run_query(query)
    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.first_visit = None
                page.last_visit = None
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat}

    return render(request, 'rango/add_page.html', context_dict)


@login_required
def track_url(request):
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            page = Page.objects.get(id=page_id)
            page.views += 1
            if page.first_visit is None:
                page.first_visit = timezone.now()
            page.last_visit = timezone.now()
            page.save()
            return redirect(page.url)
        else:
            return index(request)


@login_required
def register_profile(request):
    user = User.objects.get(id=request.user.id)
    user_profile, _ = UserProfile.objects.get_or_create(user_id=request.user.id)
    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_profile_form.is_valid():
            user_profile_form.save(commit=True)
        else:
            print user_profile_form.errors
        return render(request, 'rango/profile.html', {'user': user, 'user_profile': user_profile, 'curr_user': user})
    else:
        user_profile_form = UserProfileForm(initial=model_to_dict(user_profile))
        return render(request, 'rango/profile_registration.html',
                      {'user': user, 'user_profile_form': user_profile_form})


@login_required
def profile(request, user_id):
    curr_user = request.user
    user = User.objects.get(id=user_id)
    user_profile = UserProfile.objects.get(user_id=user.id)
    return render(request, 'rango/profile.html', {'user': user, 'user_profile': user_profile, 'curr_user': curr_user})


@login_required
def users(request):
    return render(request, 'rango/users.html', {'users': User.objects.all(), 'curr_user': request.user})


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=''):
    cat_list = Category.objects.all()
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if cat_list and max_results > 0:
        if cat_list.count() > max_results:
            cat_list = cat_list[:max_results]

    return cat_list


def suggest_category(request):
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cats = get_category_list(8, starts_with)
    return render(request, 'rango/cats.html', {'cats': cats})


@login_required
def auto_add_page(request):
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            Page.objects.get_or_create(category=cat, title=title, url=url)
            pages = Page.objects.filter(category=cat).order_by('-views')
            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages
    return render(request, 'rango/page_list.html', context_dict)
