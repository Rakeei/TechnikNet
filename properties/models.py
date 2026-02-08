from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    """Teams for organizing users and properties"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class TeamMember(models.Model):
    """Many-to-Many relationship between Users and Teams"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'team')
        ordering = ['team__name']
    
    def __str__(self):
        return f"{self.user.username} → {self.team.name}"

class Property(models.Model):
    number = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Team assignment - a property can be assigned to multiple teams
    teams = models.ManyToManyField(Team, related_name='properties', blank=True)
    
    address_id = models.CharField(max_length=50, blank=True)
    village = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=200, blank=True)
    house_number = models.CharField(max_length=20, blank=True)
    house_number_affix = models.CharField(max_length=10, blank=True)
    owner_email = models.EmailField(blank=True)
    owner_name = models.CharField(max_length=100, blank=True)
    owner_surname = models.CharField(max_length=100, blank=True)
    owner_phone_1 = models.CharField(max_length=20, blank=True)
    owner_phone_2 = models.CharField(max_length=20, blank=True)
    pop_code = models.CharField(max_length=20, blank=True)
    gebaute_units = models.IntegerField(null=True, blank=True)
    hbg = models.CharField(max_length=50, blank=True)
    hbg_termin = models.DateTimeField(null=True, blank=True)
    ausbau_termin = models.DateTimeField(null=True, blank=True)
    
    # K.L choices from 0 to 50
    KL_CHOICES = [(i, str(i)) for i in range(0, 51)]
    kl_15m = models.IntegerField(default=0, null=True, blank=True, choices=KL_CHOICES)
    kl_20m = models.IntegerField(default=0, null=True, blank=True, choices=KL_CHOICES)
    kl_30m = models.IntegerField(default=0, null=True, blank=True, choices=KL_CHOICES)
    kl_50m = models.IntegerField(default=0, null=True, blank=True, choices=KL_CHOICES)
    kl_80m = models.IntegerField(default=0, null=True, blank=True, choices=KL_CHOICES)
    kl_100m = models.IntegerField(default=0, null=True, blank=True, choices=KL_CHOICES)
    
    JA_NEIN_CHOICES = [
        ('', '---------'),
        ('Ja', 'Ja'),
        ('Nein', 'Nein'),
    ]
    keller = models.CharField(max_length=10, choices=JA_NEIN_CHOICES, blank=True)
    huep = models.CharField(max_length=10, choices=JA_NEIN_CHOICES, blank=True)
    spleissen = models.CharField(max_length=10, choices=JA_NEIN_CHOICES, blank=True)
    comments = models.TextField(blank=True, verbose_name='Comments/Notes')
    hbg = models.CharField(max_length=10, choices=JA_NEIN_CHOICES, blank=True)
    ohne_infra = models.IntegerField(default=0, null=True, blank=True, verbose_name='Ohne Infra')
    mit_infra = models.IntegerField(default=0, null=True, blank=True, verbose_name='Mit Infra')
    # Updated Status Field with Choices
    STATUS_CHOICES = [
    ('', '---------'),
    ('klarungen', 'Klarungen'),
    ('auskundung', 'Auskundung terminiert'),
    ('zustimmung_eigentuemer', 'Zustimmung des Eigentümers'),
    ('bereit_zur_umsetzung', 'Bereit zur Umsetzung'),
    ('ausbau_terminiert', 'Ausbau terminiert'),
    ('ausbau_abgeschlossen', 'Ausbau Abgeschlossen'),
    ('bezahlt', 'Bezahlt'),
    ('storniert', 'Storniert'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        return f"{self.number} - {self.village}"
    
    def get_team_names(self):
        """Return comma-separated team names"""
        return ", ".join([team.name for team in self.teams.all()])
    
    def is_completed(self):
        """Check if property is in completed status"""
        return self.status in ['ausbau_abgeschlossen', 'bezahlt']
    
    def can_user_edit(self):
        """Check if regular users can edit this property"""
        return self.status not in ['ausbau_abgeschlossen', 'bezahlt']

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Image for {self.property.number}"
