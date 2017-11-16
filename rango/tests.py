from datetime import timedelta

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

from rango.models import Category, Page


class CategoryMethodTests(TestCase):

    def test_ensure_views_are_positive(self):
        """
        ensure_views_are_positive should results True for categories where views are zero or positive
        """
        cat = Category(name='test', views=-1, likes=0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        """
        slug_line_creation checks to make sure that when we add a category an appropriate slug line is created
        i.e. "Random Category String" -> "random-category-string"
        """
        cat = Category(name='Random Category String')
        cat.save()
        self.assertEqual(cat.slug, 'random-category-string')


class PageMethodTests(TestCase):

    def test_last_visit_and_first_visit_not_in_future(self):
        """
        last_visit and first_visit should not have dates set to the future
        """
        page = Page(category_id=1,
                    title="test",
                    url="http://www.test.com",
                    views=0,
                    last_visit=timezone.now() + timedelta(days=1),
                    first_visit=timezone.now() + timedelta(days=2)
                    )
        page.save()
        self.assertLessEqual(page.last_visit, timezone.now())
        self.assertLessEqual(page.first_visit, timezone.now())

    def test_last_visit_happens_after_first_visit(self):
        """
        last_visit and first_visit should not have dates set to the future
        """
        page = Page(category_id=1,
                    title="test",
                    url="http://www.test.com",
                    views=0,
                    last_visit=timezone.now() - timedelta(days=2),
                    first_visit=timezone.now() - timedelta(days=1)
                    )
        page.save()
        self.assertLessEqual(page.first_visit, page.last_visit)


class IndexViewTests(TestCase):

    def test_index_view_with_no_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        add_cat('test', 1, 1)
        add_cat('temp', 1, 1)
        add_cat('tmp', 1, 1)
        add_cat('tmp test temp', 1, 1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tmp test temp")

        num_cats = len(response.context['categories'])
        self.assertEqual(num_cats, 4)


# Helper Functions
def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c
