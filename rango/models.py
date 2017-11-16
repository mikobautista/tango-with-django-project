from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        # Uncomment if you don't want the slug to change every time the name changes
        # if self.id is None:
        # self.slug = slugify(self.name)
        self.slug = slugify(self.name)

        # Prevent from having negative views
        if self.views < 0:
            self.views = 0

        super(Category, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    last_visit = models.DateTimeField(null=True, default=None)
    first_visit = models.DateTimeField(null=True, default=None)

    def save(self, *args, **kwargs):
        # first_visit <= last_visit <= now
        now = timezone.now()
        if self.last_visit and self.last_visit > now:
            self.last_visit = now
        if self.first_visit and self.first_visit > now:
            self.first_visit = now
        if self.last_visit and self.first_visit and self.first_visit > self.last_visit:
            self.first_visit = self.last_visit
        super(Page, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title


class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username
