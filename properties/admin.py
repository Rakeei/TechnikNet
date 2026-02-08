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
    list_per_page = 50  
    list_max_show_all = 10000  
    show_full_result_count = True

    def changelist_view(self, request, extra_context=None):
        """Override to add custom per_page options"""
        per_page = request.GET.get('per_page', None)

        if per_page:
            try:
                if per_page == 'all':
                    self.list_per_page = self.list_max_show_all
                else:
                    per_page_int = int(per_page)
                    if 1 <= per_page_int <= 10000:
                        self.list_per_page = per_page_int
            except (ValueError, TypeError):
                pass

        extra_context = extra_context or {}
        extra_context['per_page_options'] = [50, 1000, 2000]
        extra_context['current_per_page'] = request.GET.get('per_page', '50')

        return super().changelist_view(request, extra_context=extra_context)
    actions = ['bulk_change_status', 'bulk_assign_team', 'bulk_remove_team']

    def get_teams(self, obj):
        return obj.get_team_names() or '-'
    get_teams.short_description = 'Teams'

    @admin.action(description='Change status for selected properties')
    def bulk_change_status(self, request, queryset):
        from django import forms
        from django.shortcuts import render
        
        class StatusForm(forms.Form):
            status = forms.ChoiceField(
                choices=Property.STATUS_CHOICES,
                label='New Status',
                help_text='Select the status to apply to all selected properties'
            )
        
        if 'apply' in request.POST:
            form = StatusForm(request.POST)
            if form.is_valid():
                status = form.cleaned_data['status']
                count = queryset.update(status=status)
                self.message_user(request, f'Successfully updated status for {count} properties to "{dict(Property.STATUS_CHOICES).get(status)}"')
                return
        else:
            form = StatusForm()
        
        return render(request, 'admin/bulk_change_status.html', {
            'form': form,
            'properties': queryset,
            'title': 'Change Status'
        })
    
    @admin.action(description='Assign team to selected properties')
    def bulk_assign_team(self, request, queryset):
        from django import forms
        from django.shortcuts import render
        
        class TeamForm(forms.Form):
            team = forms.ModelChoiceField(
                queryset=Team.objects.all(),
                label='Team',
                help_text='Select the team to assign to all selected properties'
            )
            clear_existing = forms.BooleanField(
                required=False,
                initial=False,
                label='Clear existing teams first',
                help_text='Check this to remove all existing teams before assigning the new one'
            )
        
        if 'apply' in request.POST:
            form = TeamForm(request.POST)
            if form.is_valid():
                team = form.cleaned_data['team']
                clear_existing = form.cleaned_data['clear_existing']
                
                for prop in queryset:
                    if clear_existing:
                        prop.teams.clear()
                    prop.teams.add(team)
                
                self.message_user(request, f'Successfully assigned team "{team.name}" to {queryset.count()} properties')
                return
        else:
            form = TeamForm()
        
        return render(request, 'admin/bulk_assign_team.html', {
            'form': form,
            'properties': queryset,
            'title': 'Assign Team'
        })
    
    @admin.action(description='Remove team from selected properties')
    def bulk_remove_team(self, request, queryset):
        from django import forms
        from django.shortcuts import render
        
        class TeamRemoveForm(forms.Form):
            team = forms.ModelChoiceField(
                queryset=Team.objects.all(),
                label='Team',
                help_text='Select the team to remove from all selected properties'
            )
        
        if 'apply' in request.POST:
            form = TeamRemoveForm(request.POST)
            if form.is_valid():
                team = form.cleaned_data['team']
                
                for prop in queryset:
                    prop.teams.remove(team)
                
                self.message_user(request, f'Successfully removed team "{team.name}" from {queryset.count()} properties')
                return
        else:
            form = TeamRemoveForm()
        
        return render(request, 'admin/bulk_remove_team.html', {
            'form': form,
            'properties': queryset,
            'title': 'Remove Team'
        })

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
