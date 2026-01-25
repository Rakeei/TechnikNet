from django.contrib import admin
from .models import Team, TeamMember, Property, PropertyImage

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'member_count', 'property_count', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'

    def property_count(self, obj):
        return obj.properties.count()
    property_count.short_description = 'Properties'

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'joined_at')
    list_filter = ('team',)
    search_fields = ('user__username', 'user__email', 'team__name')
    date_hierarchy = 'joined_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'team')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('number', 'address_id', 'village', 'street', 'house_number', 'house_number_affix', 'owner_name', 'get_teams', 'status', 'created_at')
    list_filter = ('status', 'teams')
    search_fields = ('number', 'village', 'owner_name', 'owner_surname', 'pop_code', 'address_id', 'street')
    filter_horizontal = ('teams',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def get_teams(self, obj):
        return obj.get_team_names() or '-'
    get_teams.short_description = 'Teams'

    fieldsets = (
        ('Basic Information', {
            'fields': ('number', 'address_id', 'village', 'street',
                      'house_number', 'house_number_affix', 'pop_code')
        }),
        ('Owner Information', {
            'fields': ('owner_name', 'owner_surname', 'owner_email',
                      'owner_phone_1', 'owner_phone_2')
        }),
        ('Team Assignment', {
            'fields': ('teams',),
            'description': 'Assign this property to one or more teams'
        }),
        ('Technical Details', {
            'fields': ('gebaute_units', 'hbg', 'hbg_termin', 'ausbau_termin',
                      'kl_15m', 'kl_20m', 'kl_30m', 'kl_50m', 'kl_80m', 'kl_100m',
                      'keller', 'huep', 'spleissen', 'ohne_infra', 'mit_infra',
                      'comments', 'status')
        }),
    )

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('property__number',)
