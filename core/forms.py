from django import forms
from .models import WorkItem, TimeSessionAllocation, CostDocument, Project

class WorkItemForm(forms.ModelForm):
    class Meta:
        model = WorkItem
        fields = ['name','parent','weight','progress','status','sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'class':'w-full'}),
            'weight': forms.NumberInput(attrs={'step':'0.01'}),
            'progress': forms.NumberInput(attrs={'min':'0','max':'100','step':'1'}),
            'status': forms.Select(),
            'sort_order': forms.NumberInput(),
        }
    def clean_progress(self):
        v = self.cleaned_data['progress']
        if v < 0 or v > 100:
            raise forms.ValidationError("Il progress deve essere tra 0 e 100.")
        return v

class TimeStartForm(forms.Form):
    project = forms.ModelChoiceField(queryset=Project.objects.all())
    note = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)

class AllocationForm(forms.ModelForm):
    class Meta:
        model = TimeSessionAllocation
        fields = ['work_item','minutes_allocated','percent_allocated','note']
        widgets = {'note': forms.Textarea(attrs={'rows':2})}
    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('minutes_allocated') and not cleaned.get('percent_allocated'):
            raise forms.ValidationError("Inserisci almeno minuti o percentuale.")
        return cleaned

class VehicleCheckoutForm(forms.Form):
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False)
    start_odometer_km = forms.IntegerField(min_value=0)
    start_fuel_percent = forms.IntegerField(min_value=0, max_value=100)
    notes_out = forms.CharField(widget=forms.Textarea(attrs={'rows':2}), required=False)

class VehicleCheckinForm(forms.Form):
    end_odometer_km = forms.IntegerField(min_value=0)
    end_fuel_percent = forms.IntegerField(min_value=0, max_value=100)
    notes_in = forms.CharField(widget=forms.Textarea(attrs={'rows':2}), required=False)
    damages_report = forms.CharField(widget=forms.Textarea(attrs={'rows':2}), required=False)
    photos_urls = forms.CharField(widget=forms.Textarea(attrs={'rows':2,'placeholder':'URL uno per riga'}), required=False)

class CostForm(forms.ModelForm):
    class Meta:
        model = CostDocument
        fields = ['project','work_item','doc_type','amount_eur','with_vat','doc_url','note']
        widgets = {'note': forms.Textarea(attrs={'rows':2})}
