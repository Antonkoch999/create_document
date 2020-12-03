"""Creates data in the table in database."""

from django.db import models
from django.urls import reverse


class Client(models.Model):
    """Create instance client."""

    number_of_contract = models.CharField(max_length=15)
    date_of_contract = models.CharField(max_length=10)
    city = models.CharField(max_length=40)
    name_of_organization = models.CharField(max_length=255)
    in_face = models.CharField(max_length=40,
                               help_text='"In face" in parental case')
    in_face_in_nominative = models.CharField(max_length=40,
                                             help_text='"In face" in nominative')
    name_face_organizations = models.CharField(max_length=255,
                                               help_text='Full Name in parental case')
    acting_on_the_basis = models.CharField(max_length=255)
    legal_address = models.TextField()
    address_of_bank = models.TextField()
    unp = models.CharField(max_length=9)
    initials = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=13, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def get_absolute_url(self):
        """Get url client."""
        return reverse('input:detail_page',
                       args=[str(self.pk)])

    def __str__(self):
        return f'{self.name_of_organization}'
